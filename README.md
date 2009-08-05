Hookah
======
The HTTP event engine

Current Features
----------------
* Interface is 100% HTTP (use easily from any language)
* Dispatches POST requests (webhooks) asynchronously with retry
* Provides publish/subscribe interface using [PubSubHubbub protocol](http://code.google.com/p/pubsubhubbub/) (experimental)
* Provides "Twitter Stream API"-style long-polling interface for topics (super experimental)


About
-----
Hookah was originally created to ease the implementation of webhooks in your web systems. While webhooks are still at the core, it's becoming a scalable HTTP event engine with HTTP pubsub and long-polling event streaming. And of course, webhooks. Any system with webhooks or looking to implement webhooks will benefit from Hookah.

Requirements
------------
Hookah currently depends on Twisted.

Usage
-----
Hookah is a simple, lightweight standalone web server that you run locally alongside your existing web stack. Starting it from the command line is simple:

        twistd hookah --port 8080
        
Using the Dispatcher
--------------------
Posting to /dispatch with a _url POST parameter will queue that POST request for that URL and return immediately. This allows you to use Hookah as an outgoing request queue that handles retries, etc. Using HTTP means you can do this easily from any language using a familiar API.

Posting to /dispatch with a _topic POST parameter will broadcast that post to any callbacks subscribed to that topic (see following PubSub section), or any stream consumers with a long-running request on that topic.

Using PubSub
------------
Refer to the [PubSubHubbub spec](http://pubsubhubbub.googlecode.com/svn/trunk/pubsubhubbub-core-0.1.html), as Hookah is currently quite compliant with this excellent protocol. The hub endpoint is at /hub, but this multiplexes (based on 'hub.mode' param) between /publish for publish pings, and /subscribe for subscription requests. 

**This feature is still very early** and as a result it is incomplete. The main caveat is that there is no permanent storage of subscription data or of the queues. This means if you were to restart Hookah, all subscriptions would have to be made again. 

Using Streams
-------------
Hookah implements a long-running stream API, modeled after [Twitter's Stream API](http://apiwiki.twitter.com/Streaming-API-Documentation). Just do a GET request to /stream with a topic parameter, and you'll get a persistent, chunked HTTP connection that will send you messages published to that topic as they come in. Refer to the Twitter Stream API docs to get a better feel for this pragmatic Comet streaming technique.

Todo
----

1. Persistent storage (SQLite, MySQL, CouchDB) and queuing (in memory, Kestrel, RabbitMQ) backends
1. Configuration
1. Backlog/history with resend
1. "Errback" webhook
1. Async response handling

License
-------

Hookah is released under the MIT license, which can be found in the LICENSE file.

Contributors
------------
* you?

Author
------
Jeff Lindsay <progrium@gmail.com>

Learn more about web hooks
--------------------------
http://webhooks.org