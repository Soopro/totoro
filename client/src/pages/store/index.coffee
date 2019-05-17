core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')

app = getApp()

core.Page
  data:
    image: core.image
    is_loading: null
    has_more: null
    books: []
    meta: {}
    content: ''

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
      self.list()


  # methods
  refresh: ->
    self = @
    self.timestamp = utils.now()

    self.setData
      books: []
      has_more: null

    self.list()


  list: ->
    self = @
    self.setData
      is_loading: true

    restStore.book.list
      offset: self.data.books.length
      t: self.timestamp
    .then (results)->
      self.setData
        books: self.data.books.concat(results)
        has_more: Boolean(results[0] and results[0]._more)
    .finally ->
      self.setData
        is_loading: false

  # hanlders
  search: (e)->
    self = @
    self.setData
      is_loading: true
    try
      keys = e.detail.value.keywords.split()
    catch
      self.setData
        books: []
        has_more: false
      return

    restStore.book.search
      search_keys: keys
    .then (results)->
      self.setData
        books: results
        has_more: false
    .finally ->
      self.setData
        is_loading: false

  scan: ->
    self = @
    wx.scanCode
      success: (data) ->
        try
          slug = data.result.split('/')[0]
        catch
          return
        app.nav.go
          route: core.config.paths.item
          args:
            slug: slug

  enter: (e)->
    self = @
    slug = e.currentTarget.dataset.slug
    return if not slug
    app.nav.go
      route: core.config.paths.item
      args:
        slug: slug
