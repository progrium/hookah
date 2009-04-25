Hookah
======
The webhook event broker

Current Features
----------------
* Asynchronously dispatches webhook callbacks
* Interface is 100% HTTP (use easily with any language)
* Handles retries (very dumbly right now)


About
-----
Hookah was created to ease the implementation of webhooks in your web apps. The simplest way to do webhooks is to do inline HTTP requests in your app to invoke the user callbacks. However, this should be asynchronous and there are various other concerns you might want to address to have a decent webhook system. Hookah aims to be the ultimate webhook provider buddy ... perhaps the SMTP daemon of webhooks.

Requirements
------------
Hookah currently depends on Twisted.

Usage
-----
Hookah is a simple, lightweight standalone web server that you run locally alongside your existing web stack. Starting it from the command line is simple:

        python hookah.py 8000
        
The first argument is the port you want it to run on. Because its interface is HTTP, you can use it from nearly any programming environment and invoke it using an HTTP client (like urlopen in python):

        # Invoke the callback
        urllib.urlopen(user.callback_url.replace('http://', 'http://localhost:8000/'), payload)
        
The idea is that you make a request as if you were directly invoking the callback URL, but you call Hookah instead. For example, a callback of:

        http://example.com/user/callback/endpoint
        
Becomes:

        http://localhost:8000/example.com/user/callback/endpoint

Your request to Hookah will return immediately and perform the outgoing request asynchronously, also performing retries if the request fails.

Coming Soon
-----------
Obviously, Hookah was designed to be the simplest solution possible. Right now, it basically performs asynchronous HTTP requests with retries using HTTP as the interface. However, this is useful for many people getting started with web hooks and Hookah will continue to provide more functionality around this core mechanism. Features coming soon (with your help?) include:

1. Response handling - Hookah only works for the fire and forget usage model. If you want response data, you'll have to do synchronous requests yourself inline, or wait until we handle response handling. This includes a blocking inline response handling mode, but also an asynchronous handling mode, where Hookah provides a web hook for you to handle the responses.
1. Verification - Hookah will keep track of outgoing requests and provide an endpoint you can expose to your users that will verify requests. This makes sure requests to users weren't spoofed, but requires your users to perform a request back to you for verification. However, this works as proven by PayPal.
1. Event channel management and registration - Hookah will eventually manage your user callback URLs for you (using a datastore of your choice) and provide a web API you can expose to users for letting them programmatically register callbacks. This means you don't have to manage state and all your web hook implementation code can be made up of just invoking HTTP requests to Hookah. 
1. Authentication - Hookah can provide HMAC signature authentication for you so you don't have to worry about it. 
1. More!

Contributors
------------
* Jeff Lindsay
* you?

Learn more about web hooks
--------------------------
http://webhooks.org