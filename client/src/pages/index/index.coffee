core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')

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
    restStore.page.get('index')
    .then (page)->
      app.set_navbar(page.meta.title)
      self.setData
        meta: page.meta
        content: page.content
    .then ->
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
      products: []
      has_more: null

    self.list()


  list: ->
    self = @
    self.setData
      is_loading: true

    restStore.product.list
      paged: self.paged
      t: self.timestamp
    .then (results)->
      self.setData
        products: self.data.products.concat(results)
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
