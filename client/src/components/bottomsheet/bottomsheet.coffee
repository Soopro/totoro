app = getApp()

Component
  properties:

    minHeight:
      type: Number
      value: 60  # 'px'

    maxHeight:
      type: Number
      value: 480  # 'px'

    duration:
      type: Number
      value: 300

    status:
      type: Boolean
      value: false
      observer: (status)->
        self = @
        setTimeout ->
          self.set_height()
        , 100
        self.animate(status)


  # lifecycle
  ready: ->
    self = @

    self.anim_element = wx.createAnimation
      duration: self.data.duration
      timingFunction: "ease"
      delay: 0

    self.anim_mask = wx.createAnimation
      duration: self.data.duration
      timingFunction: "ease"
      delay: 0

  # methods
  methods:
    set_height: ->
      self = @
      query = wx.createSelectorQuery().in(self)
      query.select('.bottomsheet-content').boundingClientRect (rect)->
        height = Math.min(rect.height, self.data.maxHeight)
        height = Math.max(height, self.data.minHeight)
        self.setData
          scrollable: rect.height > self.data.maxHeight
          sheet_height: height
      .exec()


    animate: (status)->
      self = @
      if status
        self.anim_mask.opacity(1).step()
        self.anim_element.bottom(0).step()
        if status
          self.setData
            active: true
      else
        self.anim_mask.opacity(0).step()
        self.anim_element.bottom('-100%').step()
        setTimeout ->
          self.setData
            active: false
        , self.data.duration

      self.setData
        anim_mask: self.anim_mask.export()
        anim_element: self.anim_element.export()


    dismiss: ->
      self = @
      self.setData
        status: false


    noop: ->
