core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')


app = getApp()

core.Page
  data:
    book: {}
    image: core.image

  # lifecycle
  onLoad: (opts)->
    self = @
    self.get_book(opts.slug)

  # methods
  get_book: (slug)->
    self = @
    restStore.book.get(slug)
    .then (book)->
      self.setData
        book: book

  # hanlders
  checkout: (e)->
    self = @
    slug = e.currentTarget.dataset.slug
    return if not slug
    app.nav.go
      route: core.config.paths.checkout
      args:
        slug: slug
