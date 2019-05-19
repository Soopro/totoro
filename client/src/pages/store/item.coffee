core = require('../../core.js')
utils = require('../../utils.js')
deco = require('../../decorators.js')
restStore = require('../../restapi/store.js')


app = getApp()

core.Page
  data:
    book: {}
    consignee: null
    sheet_status:false
    image: core.image

  # lifecycle
  onShareAppMessage: ->
    app.share()

  onLoad: deco.login_required (opts)->
    self = @
    self.check_address_authorization()
    self.get_book(opts.path)

  # methods
  get_book: (slug)->
    self = @
    restStore.book.get(slug)
    .then (book)->
      wx.setNavigationBarTitle
        title: book.meta.title or ''
      self.setData
        book: book

  get_shipping_address: ->
    self = @
    self.check_address_authorization()
    wx.chooseAddress
      success: (info)->
        self.setData
          consignee: core.reform_consignee(info)
      fail: ->
        self.check_address_authorization()

  check_address_authorization: ->
    self = @
    core.get_authorize 'scope.address'
    , (status) ->
      if status is undefined
        status = true
      self.setData
        address_authorized: status

  # hanlders
  open_sheet: (e)->
    self = @
    book = e.currentTarget.dataset.book
    return if not book
    if book.overlend
      core.toast
        title: '你不能同时借那么多书'
    else if not book.is_afford
      core.toast
        title: '你的UCoin不够'
    else
      self.setData
        sheet_status: true

  checkout: (e)->
    self = @
    book = e.currentTarget.dataset.book
    consignee = e.currentTarget.dataset.consignee
    return if not book or not consignee
    restStore.book.checkout(book.slug, consignee)
    .then (book)->
      self.setData
        book: book
        sheet_status: false
      core.toast
        title: '已借阅'
        icon: 'success'
