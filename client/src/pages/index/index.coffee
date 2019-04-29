core = require('../../core.js')
utils = require('../../utils.js')
restLibrary = require('../../restapi/library.js')

app = getApp()

core.Page
  data:
    image: core.image
    is_loading: null
    has_more: null
    products: []
    meta: {}
    content: ''

  paged: 1
  timestamp: null


  # lifecycle
  onShareAppMessage: ->
    app.share()

  onLoad: ->
    self = @
    self.refresh()


  onPullDownRefresh: ->
    self = @
    self.refresh()
    .finally ->
      wx.stopPullDownRefresh()

  onReachBottom: ->
    self = @
    if self.data.has_more is true
      self.paged += 1
      self.list()


  # hanlders
  refresh: ->
    self = @
    self.paged = 1
    self.timestamp = utils.now()

    self.setData
      bookss: []
      has_more: null

    self.list()


  list: ->
    self = @
    self.setData
      is_loading: true

    restLibrary.book.list
      paged: self.paged
      t: self.timestamp
    .then (results)->
      self.setData
        books: results
        has_more: results[0] and results[0]._more
    .finally ->
      self.setData
        is_loading: false


  enter: (e)->
    self = @
    item = e.currentTarget.dataset.item
    return if not item
    app.nav.go
      route: core.config.paths.item
      args:
        slug: item.slug
