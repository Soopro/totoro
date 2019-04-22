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
  });
})(jQuery);