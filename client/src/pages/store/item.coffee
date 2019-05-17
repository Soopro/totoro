core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')


app = getApp()

core.Page
  data:
    book: {}
    consignee: null
    sheet_status:false
    image: core.image

  # lifecycle
  onLoad: (opts)->
    self = @
    self.check_address_authorization()
    self.get_book(opts.slug)

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
    console.log book
    if book.overlend
      core.toast
        title: '你不能同时借那么多书'
    else
      self.setData
        sheet_status: true

  checkout: (e)->
    self = @
    book = e.currentTarget.dataset.book
    return if not book

