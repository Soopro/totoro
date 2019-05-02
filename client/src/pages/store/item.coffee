core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')


app = getApp()

core.Page
  data:
    meta: {}
    content: ''
    image: core.image

  # lifecycle
  onShareAppMessage: ->
    self = @
    meta = self.data.meta
    if meta
      try
        img_src = meta.cover_src
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
    self.slug = opts.slug
    restStore.book.get

    .then (results)->


  # hanlders
  get_book: ->
    self = @


  # helpers
