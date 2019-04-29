#---------------------
# polyfills
#---------------------

# promise
Promise::finally = (callback) ->
  constructor = @constructor
  @then ((value) ->
    constructor.resolve(callback()).then ->
      value
  ), (reason) ->
    constructor.resolve(callback()).then ->
      throw reason
      return
