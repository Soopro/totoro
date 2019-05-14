app = getApp()

Component
  properties:

    duration:
      type: Number
      value: 300

    status:
      type: Boolean
      value: false
      observer: (status)->
        self = @
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
    animate: (status)->
      self = @
      if status
        self.anim_mask.opacity(1).step()
        self.anim_element.left(0).step()
        if status
          self.setData
            active: true
      else
        self.anim_mask.opacity(0).step()
        self.anim_element.left('-100%').step()
        setTimeout ->
          self.setData
            active: false
        , self.data.duration

      self.setData
        anim_mask: self.anim_mask.export()
        anim_element: self.anim_element.export()


    dismiss: ->
      self = @
      self.triggerEvent('dismiss')
      self.setData
        status: false


    noop: ->
