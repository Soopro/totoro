requests = require('libs/requests.js')
Session = require('libs/session.js')

config = require('config.js')
utils = require('utils.js')
image = require('constant/image.js')


# session
session = new Session()


# enhanced page
PageEnhanced = (opts)->
  self = @
  opts = {} if not opts
  onLoadFn = opts.onLoad or (opts)->
  onShowFn = opts.onShow or ->

  opts.onLoad = (param)->
    self = @
    if utils.isFunction(opts.beforeLoad)
      Promise.resolve()
      .then ->
        opts.beforeLoad()
      .then ->
        onLoadFn.call self, param
    else
      onLoadFn.call self, param

  opts.onShow = ->
    self = @
    if utils.isFunction(opts.beforeShow)
      Promise.resolve()
      .then ->
        opts.beforeShow()
      result.then ->
        onShowFn.call self
    else
      onShowFn.call self

  return Page(opts)


# interceptor
requests.config.common.interceptor = (opts)->
  if not opts.url.match(/^http[s]:.*/)
    opts.url = config.baseURL.api + '/' + utils.strip(opts.url, '/')

  opts.after_reject = (res)->
    if res.statusCode in [401, 403]
      session.remove('token')
    console.error(res)
    wx.redirectTo
      url: config.paths.error
      args: res

  opts.header = opts.header or {}
  token = session.get('token')
  if token and not opts.header.Authorization
    opts.header =
      Authorization: ('Bearer ' + token)
  return opts


# authorize
get_authorize = (scope_name, callback)->
  opts = {} if not opts
  wx.getSetting
    success: (data) ->
      callback(data.authSetting[scope_name])
    fail: (error)->
      callback(null, error)


# form validator
_validator =
  required: (value)->
    return /.+/i.test(value.replace(' ', ''))

_validation = (rules, value)->
  if utils.isString(rules)
    rules = [rules]
  else if not utils.isArray(rules)
    return null
  for rule in rules
    try
      if _validator[rule] and not _validator[rule](value)
         return false
    catch
      return false
  return true

form_validator =
  validate: (from_value, rules)->
    return if not utils.isDict(rules, true)
    ffv = {}
    for k, v of from_value
      ffv[k] = _validation(rules[k], v)
    for k, v of ffv
      ffv.$error = true if v is false
    return ffv

  setPristine: (ffv, field_name)->
    try
      delete ffv[field_name]
    catch e
      console.error e
    for k, v of ffv
      ffv.$error = true if v is false
    return ffv


# reform
reform_consignee = (info)->
  payload =
    name: info.userName
    detail: info.detailInfo
    tel: info.telNumber
    province: info.provinceName
    city: info.cityName
    county: info.countyName
    postal_code: info.postalCode
    recipient: [
      info.userName
      info.telNumber
      info.provinceName
      info.cityName
      info.countyName
      info.detailInfo
      '[' + info.postalCode + ']'
    ].join(' ')
  return payload


reform_userinfo = (userinfo)->
  if not userinfo
    userinfo = {}
  _gender_map =
    1: 1  # male
    2: 0  # female
    0: 2  # unknow
  info =
    country: userinfo.country or ''
    province: userinfo.province or ''
    city: userinfo.city or ''
    language: userinfo.language or 'zh_CN'
    name: userinfo.nickName or ''
    avatar: userinfo.avatarUrl or ''
    gender: _gender_map[userinfo.gender] or 2
  return info


purify_content_img = (text, cls_name) ->
  cls_name = 'img' if not cls_name
  text.replace /<img\s.*?>/ig, (img)->
    if img.includes(' class=')
      regex = /class=[\"\'](.*?)[\"\']/
      replace = 'class="$1 ' + cls_name + '"'
    else
      regex = /\<img\s(.*?)>/
      replace = '<img class="' + cls_name + '" $1 >'
    return img.replace(regex, replace)


# toast
toast = (opts, callback)->
  opts = {} if not opts
  if not opts.duration
    opts.duration = 2400
  wx.showToast
    title: opts.title or ''
    icon: opts.icon or 'none'
    image: opts.image
    duration: opts.duration
    mask: opts.mask or true
    complete: ->
      if utils.isFunction(callback)
        setTimeout ->
          callback()
        , opts.duration


# model
dialog =
  confirm: (opts)->
    opts = {} if not opts
    if not utils.isFunction(opts.confirm)
      opts.confirm = ->
    if not utils.isFunction(opts.cancel)
      opts.cancel = ->

    modal_opts =
      title: opts.title or ''
      content: opts.content or ''
      success: (result)->
        if result.confirm
          opts.confirm()
        else
          opts.cancel(result.cancel)
      fail: ->
        opts.cancel(null)

    if opts.confirmColor
      modal_opts.confirmColor = opts.confirmColor
    if opts.confirmText
      modal_opts.confirmText = opts.confirmText
    if opts.cancelColor
      modal_opts.cancelColor = opts.cancelColor
    if opts.cancelText
      modal_opts.cancelText = opts.cancelText

    wx.showModal(modal_opts)

  alert: (opts)->
    opts = {} if not opts
    if not utils.isFunction(opts.confirm)
      opts.confirm = ->
    modal_opts =
      title: opts.title or '',
      content: opts.content or '',
      showCancel: false
      success: (result)->
        if result.confirm
          opts.confirm()
    if opts.confirmColor
      modal_opts.confirmColor = opts.confirmColor
    if opts.confirmText
      modal_opts.confirmText = opts.confirmText

    wx.showModal(modal_opts)


module.exports =
  Page: PageEnhanced
  config: config
  session: session
  image: image
  get_authorize: get_authorize
  form_validator: form_validator
  reform_consignee: reform_consignee
  reform_userinfo: reform_userinfo
  purify_content_img: purify_content_img
  toast: toast
  dialog: dialog
