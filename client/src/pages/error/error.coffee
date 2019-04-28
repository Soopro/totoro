core = require('../../core.js')

app = getApp()

core.Page
  data:
    status: null

  # lifecycle
  onLoad: (opts)->
    self = @
    app.set_navbar(core.static_title.error)

  # hendler
  back: ->
    self = @
    app.nav.launch
      route: core.config.paths.index
