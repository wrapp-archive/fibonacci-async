import json

from cogen.core import sockets
from cogen.core import schedulers
from cogen.core.coroutines import coroutine

@coroutine
def server():
    srv = sockets.Socket()
    srv.bind(('localhost', 8080))
    srv.listen(10)

    # Serve forever
    while True:
        print "Listening..."
        conn, addr = yield srv.accept()
        print "Connection from %s:%s" % addr
        m.add(handler, args=(conn, addr))

@coroutine
def handler(sock, addr):
    # Read and parse input
    data = yield sock.recv(8192)
    n = int(data)

    # Calc fib
    if n == 0 or n == 1:
        ret = n
    else:
        fib_1 = yield request_fib(n-1)
        fib_2 = yield request_fib(n-2)
        ret = fib_1 + fib_2

    # Return the result
    message = format_message(ret)
    yield sock.send(message)
    sock.close()

@coroutine
def request_fib(n):
    # Send request
    client = sockets.Socket()
    yield client.connect(('localhost', 8080))
    yield client.send(str(n))
    response = yield client.recv(8196)
    client.close()

    # Parse response
    ret = json.loads(response)['message']
    raise StopIteration(ret)

def format_message(n):
    return json.dumps({'message': n}) + '\n'

m = schedulers.Scheduler()
m.add(server)
m.run()
