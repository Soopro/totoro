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
    self.inv_volumes()
    self.inv_records()
    self.setData
      logged: true

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

  find_book: ->
    app.nav.tab
      route: core.config.paths.store

  switch_scene: (e)->
    self = @
    scene = parseInt(e.currentTarget.dataset.scene)
    self.setData
      scene: scene

  # member
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

  _join: (encrypted_data, iv)->
    self = @
    restUser.register
      encrypted_data: encrypted_data
      iv: iv
    .then (profile)->
      self.setData
        profile: profile

  sync_profile: (e)->
    self = @
    userinfo = e.detail.userInfo
    _gender_map =
      1: 1  # male
      2: 0  # female
      0: 2  # unknow
    restUser.profile.update
      meta:
        country: userinfo.country or ''
        province: userinfo.province or ''
        city: userinfo.city or ''
        language: userinfo.language or 'zh_CN'
        name: userinfo.nickName or ''
        avatar: userinfo.avatarUrl or ''
        gender: _gender_map[userinfo.gender] or 2
    .then (profile)->
      self.setData
        profile: profile


