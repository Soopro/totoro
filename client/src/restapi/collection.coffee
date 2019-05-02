requests = require('../libs/requests.js')

list_books = (args)->
  requests.get('/library/book', args)

get_book = (book_id)->
  requests.get('/library/book/'+book_id)

list_category = (args)->
  requests.get('/library/category', args)

get_category = (term_key, args)->
  requests.get('/library/category'+term_key, args)


module.exports =
  book:
    list: list_books
    get: get_book
  category:
    list: list_category
    get: get_category
