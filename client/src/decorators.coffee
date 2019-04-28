core = require('core.js')

app = getApp()

# Decorators
login_required = (fn)->
  if typeof(fn) isnt 'function'
    throw new Error('Decorator: must wrap on function.')

  wrapped_fn = (opts)->
    self = @
    if core.session.get('token')
      fn.call(self, opts)
    else
      app.login ->
        fn.call(self, opts)


  return wrapped_fn

module.exports =
  login_required: login_required
