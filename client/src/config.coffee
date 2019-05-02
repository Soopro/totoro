# Config
config =
  baseURL:
    api: 'http://localhost:9000'

  paths:
    index: '/pages/index/index'
    profile: '/pages/index/profile'
    store: '/pages/store/index'
    item: '/pages/store/item'
    error: '/pages/error/error'

  retry: 3


module.exports = config
