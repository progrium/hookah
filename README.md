Hookah
======
The webhook event broker

Current Features
----------------
* Interface is 100% HTTP (use easily with any language)
* Dispatches POST requests (webhooks) asynchronously with retry
* Provides publish/subscribe interface using PubSubHubbub protocol (experimental)


About
-----
Hookah was created to ease the implementation of webhooks in your web apps. The simplest way to do webhooks is to do inline HTTP requests in your app to invoke the user callbacks. However, this should be asynchronous and there are various other concerns you might want to address to have a decent webhook system. Hookah aims to be the ultimate webhook provider buddy ... perhaps the SMTP daemon of webhooks.

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

Using PubSub
------------
Refer to the PubSubHubbub spec, as Hookah is currently quite compliant with this excellent protocol. The endpoints are similar to their App Engine implementation: publish pings go to /publish, and subscription requests go to /subscribe. 

**This feature is still very early** and as a result it is incomplete. The main caveat is that there is no permanent storage of subscription data or of the queues. This means if you were to restart Hookah, all subscriptions would have to be made again. 

Todo
----

1. Persistent storage and queuing backends
1. Configuration
1. Async response handling
1. HTTP streaming module

Contributors
------------
* you?

Author
------
Jeff Lindsay <progrium@gmail.com>

Learn more about web hooks
--------------------------
http://webhooks.org