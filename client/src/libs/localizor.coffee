#---------------------
# Localizor
#
# Author : Redy Ru
# Email : redy.ru@gmail.com
# License : MIT
# Description: Localize UI text translations.
#---------------------

version = '1.0.0'

if not Function::property
  Function::property = (prop, methods) ->
    Object.defineProperty @prototype, prop, methods


class Localizor
  constructor: (dict_map, opts)->
    self = @
    opts = {} if not opts
    self.localizedDict = {}
    self.localizedText = {}
    self.locale_code = ''
    self.options =
      case_sensitive: false

    for k, v of self.options
      self.options[k] = opts[k] or v

    if Array.isArray(dict_map)
      for d in dict_map
        self.load(d.key, d.texts)

    else if typeof(dict_map) is 'object' and dict_map
      for k, v of dict_map
        self.load(k, v)

  @property 'version',
    get: ->
      return version

  @property 'locale',
    get: ->
      self = @
      return self.locale_code

  @property 'lang',
    get: ->
      self = @
      return self.locale_code.split('_')[0]

  @property '_dictionary',
    get: ->
      self = @
      return self.localizedText


  load: (loc, tanslates)->
    self = @
    if loc and Array.isArray(tanslates)
      self.localizedDict[loc.toString()] = tanslates


  set: (loc)->
    self = @
    locale = loc.replace('-', '_')
    lang = loc.split('_')[0]
    loc_dict = self.localizedDict

    for k, v of loc_dict
      if k.toLowerCase() is loc.toLowerCase()
        locale = k
        break

    loc_text = {}
    trans_text_list = loc_dict[lang] or loc_dict[locale] or []
    for text in trans_text_list
      continue if not text.msgid
      key =
        if self.options.case_sensitive
        then text.msgid
        else text.msgid.toLowerCase()
      loc_text[key] = text.msgstr

    self.localizedText = loc_text
    self.locale_code = locale


  translate: (str)->
    self = @
    if not str or typeof str isnt 'string'
      return str

    strkey = if self.options.case_sensitive then str else str.toLowerCase()
    trans = self.localizedText[strkey] or str

    args = []
    for arg in arguments
      args.push arg

    for arg in args[1..]
      arg = '' if arg is undefined
      trans = trans.replace("%s", arg)

    return trans


module.exports = Localizor
