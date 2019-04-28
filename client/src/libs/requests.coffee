#---------------------
# Requests
#
# Author : Redy Ru
# Email : redy.ru@gmail.com
# License : MIT
# Description: Requests is a wrapper for wx.request.
# Options:
# - show_navbar_loading: `bool` display navbar loading icon while requesting.
# - before_request: `function` run before request.
# - after_success: `function` run after request success.
# - after_reject: `function` run after request reject.
#---------------------

version = '1.0.0'


config =
  common:
    interceptor: (opts)->
      return opts


_interceptor = (opts, custom_interceptor)->
  try
    config.common.interceptor(opts)
  catch e
    console.error e
  if typeof(custom_interceptor) is 'function'
    custom_interceptor(opts)
  return opts

request = (method, url, opts)->
  opts = {} if not opts
  opts.method = method
  opts.url = url
  opts = _interceptor(opts, opts.interceptor)

  promise = new Promise (resolve, reject)->
    if opts.show_navbar_loading
      wx.showNavigationBarLoading()

    opts.success = (res) ->
      if res.statusCode >= 400
        if typeof(opts.after_reject) is 'function'
          opts.after_reject(res)
        reject(res)
      else
        if typeof(opts.after_success) is 'function'
          opts.after_success(res)
        resolve(res.data, res)

    opts.fail = (res) ->
      reject(res)

    opts.complete = ->
      if opts.show_navbar_loading
        wx.hideNavigationBarLoading()

    wx.request(opts)

  return promise


request_get = (url, args, opts)->
  opts = {} if not opts
  opts.data = args
  request('GET', url, opts)


request_put = (url, data, opts)->
  opts = {} if not opts
  opts.data = data
  request('PUT', url, opts)


request_post = (url, data, opts)->
  opts = {} if not opts
  opts.data = data
  request('POST', url, opts)


request_del = (url, args, opts)->
  opts = {} if not opts
  opts.data = args
  request('DELETE', url, opts)


requests =
  version: version
  config: config
  request: request
  get: request_get
  put: request_put
  update: request_put
  post: request_post
  del: request_del
  remove: request_del


module.exports = requests
