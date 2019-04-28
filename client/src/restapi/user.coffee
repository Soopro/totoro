requests = require('../libs/requests.js')

login = (data)->
  requests.post('/user/login', data)

join = (data)->
  requests.post('/user/join', data)

get_profile = ->
  requests.get('/user/profile', args)

update_profile = (data)->
  requests.put('/user/profile', data)

list_inventory_books = (args)->
  requests.get('/user/inventory/book', args)

list_inventory_records = (args)->
  requests.get('/user/inventory/records', args)


module.exports =
  login: login
  join: join
  profile:
    get: get_profile
    update: update_profile
  inventory:
    books: list_inventory_books
    records: list_inventory_records
