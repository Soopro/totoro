core = require('../../core.js')

app = getApp()

core.Page
  data:
    status: null

  # lifecycle
  onLoad: (opts)->
    self = @

  # hendler
  back: ->
    self = @
    app.nav.launch
      route: core.config.paths.index
