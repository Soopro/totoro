core = require('../../core.js')
deco = require('../../decorators.js')
utils = require('../../utils.js')
restUser = require('../../restapi/user.js')


app = getApp()

core.Page
  data:
    image: core.image
    profile: {}
    records: []
    volumes: []
    logged: null
    scene: 0

  # lifecycle
  onLoad: deco.login_required (opts)->
    self = @
    restUser.profile.get()
    .then (profile)->
      self.setData
        profile: profile
        logged: true

  onShow: deco.login_required (opts)->
    self = @
    self.inv_volumes()
    self.inv_records()


  # hanlders
  inv_volumes: ->
    self = @
    restUser.book.list()
    .then (volumes)->
      self.setData
        volumes: volumes

  inv_records: ->
    self = @
    restUser.record.list()
    .then (records)->
      self.setData
        records: records

  go_library: ->
    app.nav.tab
      route: core.config.paths.store

  switch_scene: (e)->
    self = @
    scene = parseInt(e.currentTarget.dataset.scene)
    self.setData
      scene: scene

  edit_profile: ->
    app.nav.go
      route: core.config.paths.profile

  sync_profile: (e)->
    self = @
    app.sync_profile(e.detail.userInfo)
    .then (profile)->
      self.setData
        profile: profile


  join: (e)->
    self = @
    encrypted_data = e.detail.encryptedData
    iv = e.detail.iv
    return if not encrypted_data or not iv
    wx.checkSession
      success: ->
        self._join(encrypted_data, iv)
      fail: ->
        app.login ->
          self._join(encrypted_data, iv)
        , true

  enter: (e)->
    self = @
    slug = e.currentTarget.dataset.slug
    return if not slug
    app.nav.go
      route: core.config.paths.item
      args:
        slug: slug

  # helpers
  _join: (encrypted_data, iv)->
    self = @
    restUser.register
      encrypted_data: encrypted_data
      iv: iv
    .then (profile)->
      self.setData
        profile: profile
