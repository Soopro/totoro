core = require('../../core.js')
utils = require('../../utils.js')
restStore = require('../../restapi/store.js')


app = getApp()

core.Page
  data:
    meta: {}
    content: ''
    amount: 1
    shelf: null
    sku_list: []
    sel_sku: null
    sheet_status: false
    sku_status: null
    image: core.image
    action_type: null

  slug: null
  sel_attrs: {}

  # lifecycle
  onShareAppMessage: ->
    self = @
    meta = self.data.meta
    if meta
      try
        img_src = meta.featured_img.src
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
    self.get_product()

  # hanlders
  get_product: ->
    self = @
    restStore.product.get self.slug
    .then (product)->
      app.set_navbar(product.meta.title)
      self.setData
        meta: product.meta
        content: product.content
    .then ->
      restStore.product.shelf self.slug
    .then (data)->
      if utils.isArrau(data.shelf.spec, true)
        # init selectable attrs
        for spec in data.shelf.spec
          self.sel_attrs[spec.key] = null
        data.shelf.spec = self._organize_spec(data.shelf.spec, data.sku_list)
      self.setData
        shelf: data.shelf
        sku_list: data.sku_list
        sku_status: self._check_sku_status(data.sku_list)
        discounts: data.discounts


  open_sheet: (e)->
    self = @
    self.setData
      action_type: e.currentTarget.dataset.actionType
      sel_sku: self._find_selected_sku()
      sheet_status: true

  select_spec: (e)->
    self = @
    spec_key = e.currentTarget.dataset.specKey
    curr_opt_idx = e.currentTarget.dataset.optIndex
    curr_spec = false
    shelf_spec = self.data.shelf.spec
    for spec in shelf_spec
      if spec.key == spec_key
        curr_spec = spec
        for opt in spec.options
          delete opt.selected
    return if not curr_spec

    curr_spec.options[curr_opt_idx].selected = true
    self.sel_attrs[curr_spec.key] = curr_spec.options[curr_opt_idx].value
    self.data.shelf.spec = self._organize_spec(shelf_spec, self.data.sku_list)
    self.setData
      sel_sku: self._find_selected_sku()
      shelf: self.data.shelf


  increase_amount: ->
    self = @
    amount = Math.max(self.data.amount += 1, 1)
    self.setData
      amount: amount

  decrease_amount: ->
    self = @
    amount = Math.max(self.data.amount -= 1, 1)
    self.setData
      amount: amount

  buy: (e)->
    self = @
    action_type = e.currentTarget.dataset.actionType
    self.setData
      action_type: null
      sheet_status: false

    sku = self.data.sel_sku
    return if not sku

    cart_item =
      id: sku.id
      item_id: sku.commodity_id
      name: sku.name
      figure: self._get_sku_figure_src(sku)
      detail: sku.detail
      attrs: sku.attrs
      signature: sku.signature
      price: if sku.dis_price >= 0 then sku.dis_price else sku.price
      amount: self.data.amount
      coupon: self._get_coupon_name()
      vouchers: self._get_voucher_names()

    # purchase
    if action_type is 'purchase'
      app.checkout.sync([cart_item])
      app.nav.go
        route: core.config.paths.purchase
        args:
          direct: true
    # add to cart
    else
      old_cart_item = app.cart.get(cart_item.id)
      if old_cart_item and old_cart_item.signature == cart_item.signature
        cart_item.amount += old_cart_item.amount
        app.cart.update(cart_item)
      else
        app.cart.add(cart_item)

  # helpers
  _check_sku_status: (sku_list)->
    if not sku_list or sku_list.length <= 0
      return 0
    count_qty = sku_list.reduce (x, y) ->
      return x + y.qty
    , 0
    if count_qty > 0
      return 1
    else
      return 2

  _organize_spec: (shelf_spec, sku_list)->
    self = @
    __check_opt_in_skus = (k, v, skus) ->
      for sku in skus
        return true if sku.attrs[k] == v
      return false

    stock_list = (sku for sku in sku_list when sku.qty)
    for spec in shelf_spec
      _tmp_list = stock_list
      for s in shelf_spec
        continue if s.key == spec.key
        sel_op = {}
        for op in s.options
          if op.selected
            sel_op = op
            break
        if sel_op.value
          _tmp_list = (sku for sku in _tmp_list \
                       when sku.attrs[s.key] == sel_op.value and sku.qty)
      for opt in spec.options
        if __check_opt_in_skus(spec.key, opt.value, _tmp_list)
          opt.disabled = false
        else
          opt.disabled = true

    return shelf_spec


  _find_selected_sku: ->
    self = @
    if not self.data.shelf.is_various
      if self.data.sku_list[0] and self.data.sku_list[0].qty
        return self.data.sku_list[0]
      else
        return null

    for k, v of self.sel_attrs
      return null if not v

    __match_attrs = (sku)->
      for k, v of self.sel_attrs
        return false if sku.attrs[k] != v
      return true

    for sku in self.data.sku_list
      if __match_attrs(sku)
        return sku
    return null

  _get_sku_figure_src: (sku)->
    self = @
    if not self.data.shelf or not utils.isArray(self.data.shelf.spec)
      return ''
    for spec in self.data.shelf.spec
      for opt in spec.options
        if sku.attrs[spec.key] == opt.value and opt.src
          return opt.src

  _get_coupon_name: ->
    self = @
    try
      return self.data.discount.coupon.tagname
    catch e
      return null

  _get_voucher_names: ->
    self = @
    try
      return (voucher.tagname for voucher in self.data.discount.vouchers)
    catch e
      return null
