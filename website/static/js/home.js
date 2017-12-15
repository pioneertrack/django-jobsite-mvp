$(function() {

  $(document).on('click', '.welcome-links', function(e) {
    var d = new Date();
    d.setTime(d.getTime() + (24 * 60 * 60 * 1000));
    var expires = 'expires=' + d.toUTCString();
    document.cookie = 'select-category=' + $(this).data('category') + ';' +
        expires + ';path=/';
  });

  $('#intro').waitForImages(function() {
        $('#intro').css({'background': ''});
      }, $.noop, true);

});
