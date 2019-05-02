# Config
config =
  baseURL:
    api: 'http://localhost:9000'

  paths:
    index: '/pages/index/index'
    profile: '/pages/index/profile'
    collection: '/pages/collection/index'
    item: '/pages/collection/item'
    error: '/pages/error/error'

  retry: 3


module.exports = config
