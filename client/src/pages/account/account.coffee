core = require('../../core.js')
deco = require('../../decorators.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')
restCustomer = require('../../restapi/customer.js')


app = getApp()

core.Page
  data:
    image: core.image
    orders: []
    total_count: null
    has_more: false
    logged: null

  timestamp: null

  # lifecycle
  onLoad: deco.login_required (opts)->
    self = @
    app.set_navbar(core.static_title.account)
    app.get_profile (profile)->
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
    self.timestamp = utils.now()

    self.setData
      orders: []
      has_more: null
    self.list_orders()

  list_orders: ->
    self = @
    restCustomer.order.list
      offset: self.data.orders.length
      t: self.timestamp
    .then (results)->
      orders = self.data.orders.concat(results)
      last_one = results[0] or {_more: false, _count: 0}
      self.setData
        orders: orders
        has_more: last_one._more
        total_count: last_one._count

  check_detail: (e)->
    self = @
    order = e.currentTarget.dataset.order
    return if not order
    app.nav.go
      route: core.config.paths.order
      args:
        id: order.id

  go_buy: ->
    app.nav.tab
      route: core.config.paths.index

  # member
  join_member: (e)->
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
    restCustomer.member.create
      encrypted_data: encrypted_data
      iv: iv
    .then (profile)->
      app.set_profile profile, (profile)->
        self.setData
          profile: profile

  sync_profile: (e)->
    self = @
    profile = core.reform_userinfo(e.detail.userInfo)
    app.set_profile profile, (profile)->
      self.setData
        profile: profile
