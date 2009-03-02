Hookah
======
The web hook event broker

About
-----
Hookah was created to ease the implementation of web hooks in your web apps. Normally, assuming you have a way for users to register callback URLs, invoking a web hook can be as trivial as this Python pseudo-code:

        def some_significant_event_in_your_app(user):
            # Actually do the event
            results = do_significant_work(user)
            
            # Invoke the web hook
            urllib.urlopen(user.hooks['some_significant_event'].url, results)
            
            return results
            
However, this does not scale and lacks many features common in web hook implementations such as retries, verification, response handling, authentication, etc. It was also assumed you had an interface to let the user define their callback URLs. Hookah aims to solve these problems so that you can implement them as easy as the above code and still get all these features.

Requirements
------------
Hookah currently depends on CherryPy.

Usage
-----
Hookah is a simple, lightweight standalone web server that you run locally alongside your existing web stack. Starting it from the command line is simple:

        python hookah.py 8000
        
The first argument is the port you want it to run on. Because its interface is HTTP, you can use it nearly any programming environment and invoke it using code slightly modified from the above example:

        # Invoke the web hook
        urllib.urlopen(user.hooks['some_significant_event'].url.replace('http://', HOOKAH_BASEURL), results)
        
The idea is that you make the same request but to Hookah, using a modified version of the URL. For example:

        http://example.com/user/handler/endpoint
        
Becomes:

        http://localhookah/example.com/user/handler/endpoint
        
Where localhookah is the host for Hookah. Starting off, this might just be localhost:8000 or whatever port you put Hookah on.

Hookah will return immediately and perform the outgoing request asynchronously, also performing retries if the request fails. 

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