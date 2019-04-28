core = require('../../core.js')
deco = require('../../decorators.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')
restCustomer = require('../../restapi/customer.js')


app = getApp()

core.Page
  data:
    image: core.image
    profile: null
    orders: []
    total_count: null
    has_more: false
    logged: null

  submitted: false

  # lifecycle
  onLoad: deco.login_required (opts)->
    self = @
    self.id = opts.id
    app.set_navbar(core.static_title.order)
    restCustomer.order.get(opts.id)
    .then (order)->
      self.setData
        order: order
        logged: true

  # hanlders
  copy_delivery: (e)->
    delivery = e.currentTarget.dataset.delivery
    return if not delivery
    wx.setClipboardData
      data: delivery
    wx.showToast
      icon: 'none'
      title: delivery

  complete_order: (e)->
    self = @
    title = e.currentTarget.dataset.title
    content = e.currentTarget.dataset.content
    return if self.submitted
    core.dialog.confirm
      title: title
      content: content
      confirm: ->
        self.submitted = true
        restCustomer.order.done(self.id)
        .then (order)->
          self.setData
            order: order
        .finally ->
          self.submitted = false
