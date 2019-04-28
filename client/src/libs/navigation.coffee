#---------------------
# Navigation
#
# Author : Redy Ru
# Email : redy.ru@gmail.com
# License : MIT
# Description: Navigation methods.
#---------------------

version = '1.0.0'

if not Function::property
  Function::property = (prop, methods) ->
    Object.defineProperty @prototype, prop, methods


class Navigation
  constructor: (opts)->
    self = @
    opts = {} if not opts

  @property 'version',
    get: ->
      return version

  config: (opts)->
    self = @
    opts = {} if not opts

  _goto: (opts)->
    target_url = opts.route
    joiner = '?'
    for k, v of opts.args
      continue if not k
      arg_str =
        if v
        then joiner + k + '=' + v
        else joiner + k
      target_url += arg_str
      joiner = '&'
    nav_fn = opts.method or wx.navigateTo
    nav_fn
      url: target_url

  go: (opts)->
    self = @
    self._goto(opts)

  tab: (opts)->
    self = @
    opts.method = wx.switchTab
    self._goto(opts)

  redirect: (opts)->
    self = @
    opts.method = wx.redirectTo
    self._goto(opts)

  back: (delta)->
    wx.navigateBack
      delta: delta or 1

  launch: (opts)->
    self = @
    opts = {} if not opts
    if not opts.route
      pages = getCurrentPages()
      curr_page = pages[pages.length - 1]
      opts.route = curr_page.route
      opts.args = curr_page.options or {}
    opts.method = wx.reLaunch
    self._goto(opts)


module.exports = Navigation
