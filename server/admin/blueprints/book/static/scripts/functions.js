(function ($) {
  $(document).ready(function() {

    $('#CREATE-BOOK-MODAL').each(function (e) {
      var modal = $(this);
      var form = $(modal.find('form'));
      var submit_btn = modal.find('button[type="submit"]');
      submit_btn.click(function(e){
        e.preventDefault();
        form.submit();
      });
    });

    $(".upload-img").each(function(e){
      var upload_form = $(this);
      $(this).find("input[type='file']").change(function(e) {
        if (!this.files || !this.files.length) {
          return
        } else if (this.files.length > 12) {
          alert('Too many files to upload. (limited to 12)');
          return
        }
        upload_form.submit();
      });
    });

  });
})(jQuery);