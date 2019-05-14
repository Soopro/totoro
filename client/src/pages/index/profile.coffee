core = require('../../core.js')
deco = require('../../decorators.js')
utils = require('../../utils.js')
restUser = require('../../restapi/user.js')


app = getApp()

core.Page
  data:
    image: core.image
    profile: {}
    gender_list: ['女', '男', '保密']
    gender: -1
    logged: null

  submitted: false

  # lifecycle
  onLoad: deco.login_required (opts)->
    self = @
    restUser.profile.get()
    .then (profile)->
      self.setData
        profile: profile
        gender: profile.meta.gender
        logged: true

  # hanlders
  sync_profile: (e)->
    self = @
    app.sync_profile(e.detail.userInfo)
    .then (profile)->
      self.setData
        profile: profile

  gender_change: (e)->
    self = @
    profile = self.data.profile
    self.setData
      gender: parseInt(e.detail.value)

  submit: (e)->
    self = @
    form_data = e.detail.value
    profile = self.data.profile or {}
    meta = profile.meta or {}
    meta.name = form_data.name
    meta.contact = form_data.contact
    meta.gender = self.data.gender
    restUser.profile.update
      meta: meta
    .then (profile)->
      self.setData
        profile: profile
        gender: profile.meta.gender
      wx.showToast
        title: '成功',
        icon: 'success',
        duration: 1200
