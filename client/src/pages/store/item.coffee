core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')


app = getApp()

core.Page
  data:
    meta: {}
    image: core.image

  # lifecycle
  onShareAppMessage: ->
    self = @
    meta = self.data.meta
    if meta
      try
        img_src = meta.figure
      catch e
        img_src = ''
      share_obj =
        title: meta.title
        imageUrl: img_src
        path: core.config.paths.item + '?slug=' + meta.slug
    else
      share_obj = {}
    app.share(share_obj)

  onLoad: (opts)->
    self = @
    self.get_book(opts.slug)

  # hanlders
  get_book: (slug)->
    self = @
    restStore.book.get(slug)
    .then (book)->
      console.log book
      self.setData
        id: book.id
        meta: book.meta
        terms: book.terms
        tags: book.tags
        status: book.status
        creation: book.creation
        updated: book.updated


  # helpers
