from twisted.internet import reactor
from twisted.web import client, error, http
from twisted.web.resource import Resource
from hookah import queue
import urllib
import sys, os
from urllib import unquote

import cgi
import StringIO
import mimetools
import mimetypes

# TODO: Make these configurable
RETRIES = 3
DELAY_MULTIPLIER = 5

def decode_multipart_formdata(body_io, cgi_environ):
    body_io.seek(0,0)
    fs = cgi.FieldStorage(fp=body_io, environ=cgi_environ, keep_blank_values=True)
    fields = {}
    files = {}
    for field in fs.list:
        if field.filename:
            files.setdefault(field.name, []).append((field.name, field.filename, field.value))
        else:
            fields.setdefault(field.name, []).append(field.value)
    return fields, files

def encode_multipart_formdata(fields, files):
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []
    for key in fields:
        for value in fields[key]:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
    for key in files:
        for key, filename, value in files[key]:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
            L.append('')
            L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def cgi_environ_factory(request):
    if request.prepath:
        scriptName = '/' + '/'.join(request.prepath)
    else:
        scriptName = ''
    
    if request.postpath:
        pathInfo = '/' + '/'.join(request.postpath)
    else:
        pathInfo = ''
    
    parts = request.uri.split('?', 1)
    if len(parts) == 1:
        queryString = ''
    else:
        queryString = unquote(parts[1])
    
    environ = {
        'REQUEST_METHOD': request.method,
        'REMOTE_ADDR': request.getClientIP(),
        'SCRIPT_NAME': scriptName,
        'PATH_INFO': pathInfo,
        'QUERY_STRING': queryString,
        'CONTENT_TYPE': request.getHeader('content-type') or '',
        'CONTENT_LENGTH': request.getHeader('content-length') or '',
        'SERVER_NAME': request.getRequestHostname(),
        'SERVER_PORT': str(request.getHost().port),
        'SERVER_PROTOCOL': request.clientproto}
    
    for name, values in request.requestHeaders.getAllRawHeaders():
        name = 'HTTP_' + name.upper().replace('-', '_')
        # It might be preferable for http.HTTPChannel to clear out
        # newlines.
        environ[name] = ','.join([
                v.replace('\n', ' ') for v in values])
                
    return environ

def post_and_retry(url, data, retry=0, content_type='application/x-www-form-urlencoded'):
    if type(data) is dict:
        print "Posting [%s] to %s with %s" % (retry, url, data)
        data = urllib.urlencode(data)
    else:
        print "Posting [%s] to %s with %s bytes of postdata" % (retry, url, len(data))
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(data)),
    }    
    client.getPage(url, followRedirect=0, method='POST' if len(data) else 'GET', headers=headers, postdata=data if len(data) else None).addCallbacks( \
                    if_success, lambda reason: if_fail(reason, url, data, retry, content_type))

def if_success(page): pass
def if_fail(reason, url, data, retry, content_type):
    if reason.getErrorMessage()[0:3] in ['301', '302', '303']:
        return # Not really a fail
    print reason.getErrorMessage()
    if retry < RETRIES:
        retry += 1
        reactor.callLater(retry * DELAY_MULTIPLIER, post_and_retry, url, data, retry, content_type)

class DispatchResource(Resource):
    isLeaf = True

    def render(self, request):
        path = '/'.join(request.prepath[1:])
        
        content_type = request.getHeader('content-type')
        if content_type.startswith('application/x-www-form-urlencoded'):
            content_type = 'urlencoded'
            fields, files = request.args, {}
        elif content_type.startswith('multipart/form-data'):
            content_type = 'multipart'
            fields, files = decode_multipart_formdata(request.content, cgi_environ_factory(request))

        topic_param = fields.get('_topic', [None])[0]
        if topic_param:
            del fields['_topic']

            if content_type == 'multipart':
                out_type, data = encode_multipart_formdata(fields, files)
            else:
                out_type, data = 'application/x-www-form-urlencoded', urllib.urlencode(fields, doseq=True)
            queue.put('dispatch', {
                'topic' : topic_param,
                'data' : data,
                'content_type' : out_type,
                })
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled"
        
        url = fields.get('_url', [None])[0]
        if url:
            del fields['_url']
            
            if content_type == 'multipart':
                out_type, data = encode_multipart_formdata(fields, files)
            else:
                out_type, data = 'application/x-www-form-urlencoded', urllib.urlencode(fields, doseq=True)
            post_and_retry(url, data, content_type=out_type)
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 No destination URL"
