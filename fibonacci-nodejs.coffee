url = require 'url'
http = require 'http'

PORT = 3000
NUMBER_REGEXP = /\d+$/

http.globalAgent.maxSockets = 2000

get = (number, callback) ->
  r = http.get host: '0.0.0.0', port: PORT, path: "/#{number}", (request) ->
    data = ''
    request.on('data', (chunk) -> data += chunk)
    request.on('end', -> callback(parseInt(data)))

  r.setNoDelay(true)
  r.setSocketKeepAlive(false, 0)
  r.end()

server = http.createServer (request, response) ->
  number = NUMBER_REGEXP.exec(url.parse(request.url).path)[0]
  response.writeHead 200, 'Content-Type': 'text/plain', 'Connection': 'close'

  if number <= 1
    response.end number.toString()
  else
    numbers = []
    for n in [number-1, number-2]
      get n, (n) ->
        numbers.push(n)
        response.end (numbers[0]+numbers[1]).toString() if numbers.length is 2

server.listen PORT, '127.0.0.1'
console.log "Server running at http://127.0.0.1:#{PORT}/"
