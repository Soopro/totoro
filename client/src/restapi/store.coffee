requests = require('../libs/requests.js')

get_configure = ->
  requests.get('/store/configure')

list_books = (args)->
  requests.get('/store/book', args)

search_books = (data)->
  requests.post('/store/search', data)

get_book = (book_slug)->
  requests.get('/store/book/'+book_slug)

list_category = (args)->
  requests.get('/store/category', args)

get_category = (term_key, args)->
  requests.get('/store/category'+term_key, args)


module.exports =
  configure:
    get: get_configure
  book:
    list: list_books
    get: get_book
    search: search_books
  category:
    list: list_category
    get: get_category
