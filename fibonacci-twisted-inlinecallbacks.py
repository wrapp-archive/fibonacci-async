import sys, json

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
        # Do some bookkeeping on open connections
        self.total_connections += 1
        self.concurrent_connections += 1
        self.max_concurrent_connections = max(
                self.max_concurrent_connections, self.concurrent_connections)

        # This is the in param.
        n = int(request.path.split('/')[1])

        if n == 0 or n == 1:
            self.write_response(n, request)
        else:
            self.recurse(request, n)

        return server.NOT_DONE_YET

    @defer.inlineCallbacks
    def recurse(self, request, n):
        deferreds = [
            self.request_fib(n-1),
            self.request_fib(n-2),
        ]
        try:
            results = yield defer.gatherResults(deferreds)
            message = sum(results)
        except defer.FirstError, e:
            subFailure = e.subFailure
            if isinstance(e.value, web_error.Error):
                message = json.loads(subFailure.value.response)['message']
            else:
                message = str(subFailure.value)
        self.write_response(message, request)

    def write_response(self, message, request):
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

    def request_fib(self, n):
        def callback(result):
            return json.loads(result)['message']

        deferred = client.getPage('http://localhost:8080/%s' % n)
        deferred.addCallback(callback)
        return deferred

site = server.Site(Fibonacci())
reactor.listenTCP(8080, site)
reactor.run()
