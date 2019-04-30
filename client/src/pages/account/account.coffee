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
    total_count: null
    logged: null

  # lifecycle
  onLoad: deco.login_required (opts)->
    self = @
    restUser.profile.get()
    .then (profile)->
      self.setData
        profile: profile
    self.refresh()
    self.setData
      logged: true

  onPullDownRefresh: ->
    self = @
    if not self.data.logged
      wx.stopPullDownRefresh()
      return
    self.refresh()
    .finally ->
      wx.stopPullDownRefresh()

  onReachBottom: ->
    self = @
    return if not self.data.logged
    if self.data.has_more is true
      self.list_orders()

  # hanlders
  refresh: ->
    self = @

    self.setData
      records: []
      has_more: null

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


