(function ($) {
  $(document).ready(function() {
    $(".media-uploader input[name='file']").change(function(e) {
      file = (this.files && this.files[0]) ? this.files[0] : null;
      if (!file) {
        $('.media-preview').attr('src', '#');
        $(".media-uploader button[type=submit]").hide();
        return
      }
      var reader = new FileReader();
      reader.onloadend = function() {
        $('.media-preview').attr('src', reader.result);
      }
      reader.readAsDataURL(file);
      $(".media-uploader button[type=submit]").show();
    });
  });
})(jQuery);