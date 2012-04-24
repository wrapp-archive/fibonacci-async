import sys, json

import tornado.platform.twisted
tornado.platform.twisted.install()

from twisted.web import server, resource, client, error as web_error
from twisted.internet import reactor, defer
from twisted.python import log

client.HTTPClientFactory.noisy = False
log.startLogging(sys.stdout)

class Fibonacci(resource.Resource):

    isLeaf = True
    total_connections = 0
    concurrent_connections = 0
    max_concurrent_connections = 0

    def render_GET(self, request):

        def callback(results):
            # Everything went well. Just sum up the results!
            return sum(results)

        def errback(failure):
            # Something went wrong.
            request.setResponseCode(500)
            failure.trap(defer.FirstError)
            subFailure = failure.value.subFailure

            # Check the error. If someone further down the recursion tree sent
            # us an error message, just keep raising it.
            if subFailure.check(web_error.Error):
                return json.loads(subFailure.value.response)['message']

            # Otherwise just send a summary of the error.
            return str(subFailure.value)

        def write_response(message):
            self.concurrent_connections -= 1
            response = json.dumps({
                'message': message,
                'connections': {
                    'total': self.total_connections,
                    'concurrent': self.concurrent_connections,
                    'max_concurrent': self.max_concurrent_connections
                }
            }, indent=4) + '\n'
            request.write(response)
            request.finish()


        # Do some bookkeeping on open connections
        self.total_connections += 1
        self.concurrent_connections += 1
        self.max_concurrent_connections = max(
                self.max_concurrent_connections, self.concurrent_connections)

        # This is the in param.
        n = int(request.path.split('/')[1])

        # Base case
        if n == 0 or n == 1:
            write_response(n)

        # Recurse
        else:
            deferreds = [
                self.request_fib(n-1),
                self.request_fib(n-2),
            ]
            deferred = defer.gatherResults(deferreds)
            deferred.addCallbacks(callback, errback)
            deferred.addBoth(write_response)

        return server.NOT_DONE_YET


    def request_fib(self, n):
        def callback(result):
            return json.loads(result)['message']

        deferred = client.getPage('http://localhost:8080/%s' % n)
        deferred.addCallback(callback)
        return deferred

site = server.Site(Fibonacci())
reactor.listenTCP(8080, site)
reactor.run()
