core = require('../../core.js')

app = getApp()

core.Page
  data:
    status: null

  # lifecycle
  onLoad: (opts)->
    self = @
    if not opts
      self.setData
        errmsg: opts.errmsg
        errcode: opts.errcode
        hint: opts.hint

  # hendler
  back: ->
    self = @
    app.nav.launch
      route: core.config.paths.index
