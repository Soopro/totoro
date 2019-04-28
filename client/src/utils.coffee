# ------------
# Utils
# ------------

# promise enhance
Promise::finally = (callback) ->
  constructor = @constructor
  @then ((value) ->
    constructor.resolve(callback()).then ->
      value
  ), (reason) ->
    constructor.resolve(callback()).then ->
      throw reason
      return


# helpers
_is_object = (obj)->
  return Boolean(obj isnt null and typeof(obj) is 'object')

_equals = (obj1, obj2, deep)->
  if typeof(deep) isnt 'number'
    deep = 6
  else
    deep = Math.min(deep, 60)

  deep -= 1

  if obj1 and obj2 and _is_object(obj1) and _is_object(obj2) and deep
    keys1 = Object.keys(obj1)
    keys2 = Object.keys(obj2)
    if keys1.length != keys2.length
      return false
    keys = []
    for _k in (keys1.concat(keys2))
      keys.push(_k) if _k not in keys

    for k in keys
      if not _equals(obj1[k], obj2[k], deep)
        return false
  else if obj1 != obj2
    return false
  return true


_format_num = (n)->
  n = n.toString()
  return n[1] ? n : '0' + n


# --- is ---
isObject = (obj, not_empty) ->
  if not _is_object(obj)
    return false
  return not not_empty or Object.keys(obj).length > 0

isDict = (obj, not_empty) ->
  if not _is_object(obj) or Array.isArray(obj)
    return false
  return not not_empty or Object.keys(obj).length > 0

isArray = (obj, not_empty) ->
  if not Array.isArray(obj)
    return false
  return not not_empty or obj.length > 0

isString = (obj) ->
  return typeof(obj) is 'string'

isNumber = (obj) ->
  return typeof(obj) is 'number'

isFunction = (obj)->
  return typeof(obj) is 'function'

# --- time ---
format_time = (date) ->
  year = date.getFullYear()
  month = date.getMonth() + 1
  day = date.getDate()
  hour = date.getHours()
  minute = date.getMinutes()
  second = date.getSeconds()

  date = [year, month, day].map(_format_num).join('/')
  time = [hour, minute, second].map(f_format_num).join(':')
  return date + ' ' + time

now = ->
  return parseInt(Date.now() / 1000)

# --- file ---
guess_file_name = (path)->
  path_pairs = path.split('/')
  return path_pairs[path_pairs.length-1] or ''

guess_file_ext = (str)->
  try
    str = str.split('?')[0].split('#')[0]
    if str.substr(-1) is '/'
      str = str.substr(0, str.length - 1)
    pair = str.split('.')
    if pair.length > 1
      ext = pair.pop()
      return ext.toLowerCase()
    return ''
  catch e
    return ''

# --- dict ---
dict =
  update: (obj, obj2)->
    for k, v of obj2
      obj[k] = v


# --- list ---
list =
  deduplicate: (list, attr)->
    return [] if not Array.isArray(list)
    new_list = []
    attr_map = {}
    _dup = (item)->
      if attr
        return item[attr] of attr_map
      else
        return item in new_list

    for item in list
      if not _dup(item)
        attr_map[item[attr]] = item if attr
        new_list.push(item)
    return new_list

  get: (list, item, attr) ->
    is_eq = (obj1, obj2, attr)->
      if attr
        return _equals(obj1[attr], obj2[attr])
      else
        return _equals(obj1, obj2)

    for obj, idx in list
      if is_eq(obj, item, attr)
        return obj

    return null

  popup: (list, item, attr) ->
    is_eq = (obj1, obj2, attr)->
      if attr
        return _equals(obj1[attr], obj2[attr])
      else
        return _equals(obj1, obj2)

    pop_obj = null
    for obj, idx in list
      if is_eq(obj, item, attr)
        pop_obj = obj
        list.splice idx, 1
        break

    return pop_obj

  shift: (list, curr_index, next_index, switching) ->
    switching = true if switching is undefined
    if curr_index < 0
      curr_index = 0
    else if curr_index > list.length - 1
      curr_index = list.length - 1

    next_index = Math.max(Math.min(next_index, list.length - 1), 0)
    if next_index != curr_index
      if switching
          list[curr_index] = list.splice(next_index, 1, list[curr_index])[0]
      else
        _tmp = list[curr_index]
        list.splice curr_index, 1
        list.splice next_index, 0, _tmp
    return list

  remove: (list, item, attr) ->
    equals = (obj1, obj2, attr)->
      if attr
        return _equals(obj1[attr], obj2[attr])
      else
        return _equals(obj1, obj2)

    indexes = []
    for obj, idx in list
      if equals(obj, item, attr)
        indexes.unshift idx

    for i in indexes
      list.splice i, 1

    return list

  index: (list, item, attr) ->
    equals = (obj1, obj2, attr)->
      if attr
        return _equals(obj1[attr], obj2[attr])
      else
        return _equals(obj1, obj2)

    for obj, idx in list
      if equals(obj, item, attr)
        return idx
    return null


list2dict = (list, key, key2)->
  if typeof key isnt 'string'
    key = null
  if typeof key2 isnt 'string'
    key2 = null

  dict = {}
  for item, idx in list
    key = idx.toString() if not key
    dict[item[key]] = if key2 then item[key2] else item
  return dict


list2str = (list, separator) ->
  if typeof(list) == 'string'
    return list
  else if not Array.isArray(list)
    return ''
  if not separator
    separator = ', '
  try
    str = list.join(separator)
  catch e
    str = ''
  return str



str2list = (str, is_set, separator, whitespace) ->
  if Array.isArray(str)
    return str
  else if typeof(str) isnt 'string'
    return []
  unless separator
    separator = ','
    str = str.replace(/[，]/g,',')

  try
    orglist = str.split(',')
  catch e
    orglist = []

  newlist = []
  for s in orglist
    if s
      unless whitespace
        s = s.trim()
      if is_set and s in newlist
        continue
      newlist.push(s)

  return newlist


# --- str ---
startswith = (str, text) ->
  if typeof(str) isnt 'string' or typeof(text) isnt 'string'
    return null
  return str.indexOf(text) is 0

endswith = (str, text) ->
  if typeof(str) isnt 'string' or typeof(text) isnt 'string'
    return null
  return str.substr(str.length - text.length) == text


# --- dict ---
pop = (obj, key)->
  value = obj[key]
  delete obj[key]
  return value


# --- id ---
uuid4 = (dig, hex)->
  s4 = ->
    return Math.floor((1+Math.random())*0x10000).toString(16).substring(1)
  if hex is undefined
    hex = true
  if hex
    output = s4() + s4() + s4() + s4() + s4() + s4() + s4() + s4()
  else
    output = s4() + s4() + '-' + s4() + '-' + s4() + '-' +
             s4() + '-' + s4() + s4() + s4()
  try
    limit = parseInt(dig)
  catch e
    limit = 0

  if limit
    output = output.substring(0, limit)

  return output


# ---- strip ----
strip = (str, text)->
  return _strip(str, text, true, true)

lstrip = (str, text)->
  return _strip(str, text, true, false)

rstrip = (str, text)->
  return _strip(str, text, false, true)

_strip = (str, text, left, right)->
  if typeof(str) isnt 'string'
    return null
  if typeof(text) isnt 'string'
    text = null
  if text is null
    text = '\\s'
  else if not text
    return str
  if left
    regex_left = new RegExp('^('+text+')*', 'g')
    str = str.replace(regex_left, '')
  if right
    regex_right = new RegExp('('+text+')*$', 'g')
    str = str.replace(regex_right, '')
  return str


# ---- URL ----
url =
  add_params: (url, params) ->
    if not angular.isObject(params)
      return url
    _add = (url, key, value)->
      joint = if url.indexOf('?') > -1 then '&' else '?'
      key = encodeURIComponent(key)
      value = encodeURIComponent(value)
      url = url+joint+key+'='+value
      return url

    for k, v of params
      if angular.isArray(v)
        for item in v
          url = _add(url, k, item)
      else
        url = _add(url, k, v)

    return url

  get_params: (url, unique) ->
    if typeof url isnt 'string'
      return {}
    if unique is undefined
      unique = true
    hash_idx = url.indexOf('#')
    if hash_idx > -1
      url = url.substring(0, hash_idx)

    params = {}
    query_idx = url.indexOf('?')
    if query_idx > -1
      query_vars = url.split('?')[1].split('&')
      for v in query_vars
        pair = v.split('=')
        k = pair[0]
        v = pair[1]
        if not k
          continue
        else if not params[k]
          params[k] = v
        else if not unique
          if not angular.isArray(params[k])
            params[k] = [params[k]]
          params[k].push(v)

    return params


# ---- dataurl ----
dataurl2blob = (dataURL) ->
    BASE64_MARKER = ';base64,'
    if dataURL.indexOf(BASE64_MARKER) == -1
      parts = dataURL.split(',')
      contentType = parts[0].split(':')[1]
      raw = parts[1]
      return new Blob([ raw ], type: contentType)
    parts = dataURL.split(BASE64_MARKER)
    contentType = parts[0].split(':')[1]
    raw = window.atob(parts[1])
    rawLength = raw.length
    uInt8Array = new Uint8Array(rawLength)
    i = 0
    while i < rawLength
      uInt8Array[i] = raw.charCodeAt(i)
      ++i
    new Blob([ uInt8Array ], type: contentType)


# ---- price ----
price = (amount, use_currency, symbol, fractionSize)->
  symbol = '' if symbol is undefined
  size = parseInt(fractionSize) or 2
  price = (parseInt(amount) / 100) or 0
  if use_currency
    price = price.toFixed(size).replace(/(\d)(?=(\d{3})+\.)/g, '$1,')
  else
    price = price.toFixed(size)
  return symbol + price


module.exports =
  isArray: isArray
  isObject: isObject
  isDict: isDict
  isFunction: isFunction
  isNumber: isNumber
  isString: isString
  format_time: format_time
  now: now
  list: list
  list2dict: list2dict
  list2str: list2str
  str2list: str2list
  startswith: startswith
  endswith: endswith
  equals: _equals
  pop: pop
  uuid4: uuid4
  strip: strip
  lstrip: lstrip
  rstrip: rstrip
  url: url
  guess_file_name: guess_file_name
  guess_file_ext: guess_file_ext
  dataurl2blob: dataurl2blob
  price: price

