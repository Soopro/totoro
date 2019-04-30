requests = require('../libs/requests.js')

login = (data)->
  requests.post('/user/login', data)

register = (data)->
  requests.post('/user/join', data)

get_profile = ->
  requests.get('/user/profile')

update_profile = (data)->
  requests.put('/user/profile', data)

list_inventory_books = ->
  requests.get('/user/inventory/book')

list_inventory_records = ->
  requests.get('/user/inventory/records')


module.exports =
  login: login
  register: register
  profile:
    get: get_profile
    update: update_profile
  inventory:
    books: list_inventory_books
    records: list_inventory_records
