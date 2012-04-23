# Instructions
# Install node.js (`brew install node` on OS X)
# Install npm: `curl http://npmjs.org/install.sh | sh`
# Install CoffeeScript: `npm install -g coffee-script`
# Run using `coffee fibonacci-nodejs.coffee`

url = require 'url'
http = require 'http'

PORT = 3000
NUMBER_REGEXP = /\d+$/

http.globalAgent.maxSockets = 2000

requests =
  total: 0
  concurrent: 0
  maxConcurrent: 0

get = (number, callback) ->
  r = http.get host: '0.0.0.0', port: PORT, path: "/#{number}", (request) ->
    data = ''
    request.on('data', (chunk) -> data += chunk)
    request.on('end', -> callback(parseInt(data)))

  r.setNoDelay(true)
  r.setSocketKeepAlive(false, 0)
  r.end()

end = (response, output) ->
  --requests.concurrent
  response.writeHead 200,
    'Content-Type': 'text/plain'
    'Connection': 'close'
    'TotalRequests': requests.total
    'MaxConcurrentRequests': requests.maxConcurrent
    'ConcurrentRequests': requests.concurrent

  response.end output.toString()

server = http.createServer (request, response) ->
  requests.total += 1
  requests.concurrent += 1
  requests.maxConcurrent = Math.max(requests.concurrent, requests.maxConcurrent)

  number = NUMBER_REGEXP.exec(url.parse(request.url).path)[0]

  if number <= 1
    end response, number.toString()
  else
    numbers = []
    for n in [number-1, number-2]
      get n, (n) ->
        numbers.push(n)
        end response, (numbers[0]+numbers[1]).toString() if numbers.length is 2

server.listen PORT, '127.0.0.1'
console.log "Server running at http://127.0.0.1:#{PORT}/"
