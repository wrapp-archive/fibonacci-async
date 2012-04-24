import json

import tornado.ioloop
import tornado.web
import tornado.httpclient

class Fibonacci(tornado.web.RequestHandler):

    result = []

    def write_to_results(self, n):
        self.result.append(n)
        print self.result
        if len(self.result) == 2:
            self.write_response(sum(self.result))

    def write_response(self, message):
        response = json.dumps({'message': message}) + '\n'
        self.write(response)
        self.finish()

    @tornado.web.asynchronous
    def get(self, n):

        n = int(n)
        if n == 0 or n == 1:
            self.write_response(n)
        else:
            self.request_fib(n-1)
            self.request_fib(n-2)

    @tornado.web.asynchronous
    def request_fib(self, n):
        def handle_request(response):
            if response.error:
                print 'Error:', response.error
            else:
                ret = json.loads(response.body)['message']
                self.write_to_results(int(ret))

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(tornado.httpclient.HTTPRequest(url='http://localhost:8888/%s' % n, method='GET'), callback=handle_request)

application = tornado.web.Application([(r"/(?P<n>\d+)$", Fibonacci)])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
