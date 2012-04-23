require 'goliath'
require 'em-synchrony/em-http'

require 'pp'

class App < Goliath::API
  use Goliath::Rack::Params

  attr_accessor :total_connections, :concurrent_connections, :max_concurrent_connections

  def initialize
    self.total_connections = 0
    self.concurrent_connections = 0
    self.max_concurrent_connections = 0
  end

  def response(env)
    self.total_connections += 1

    n = env["PATH_INFO"].split("/")[1].to_i

    if n == 0 or n == 1
      [200, {}, n]
    else
      multi = EventMachine::Synchrony::Multi.new
      multi.add :a, EM::HttpRequest.new("http://127.0.0.1:9000/#{n - 1}").aget
      multi.add :b, EM::HttpRequest.new("http://127.0.0.1:9000/#{n - 2}").aget
      multi.perform

      a = multi.responses[:callback][:a].response.to_i
      b = multi.responses[:callback][:b].response.to_i

      [200, {}, a + b]
    end
  end
end
