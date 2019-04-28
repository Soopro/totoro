requests = require('../libs/requests.js')

get_configure = (args)->
  requests.get('/configure', args)


module.exports =
  configure:
    get: get_configure
