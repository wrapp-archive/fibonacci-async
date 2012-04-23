require 'goliath'
require 'em-synchrony/em-http'

require 'pp'

class App < Goliath::API
  def response(env)
    n = env["PATH_INFO"].split("/")[1].to_i

    if n == 0 or n == 1
      [200, {}, n]
    else
      a = EM::HttpRequest.new("http://0.0.0.0:9000/#{n - 1}").get
      b = EM::HttpRequest.new("http://0.0.0.0:9000/#{n - 2}").get

      [200, {}, a.response.to_i + b.response.to_i]
    end
  end
end
