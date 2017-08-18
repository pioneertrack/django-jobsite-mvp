jQuery(document).ready(function($){

  // Initialize Slidebars
  var controller = new slidebars();
  controller.init();

  $('.toggle-id-1').on('click', function(e) {
    // Stop default action and bubbling
    e.stopPropagation();
    e.preventDefault();
    controller.toggle('id-1');
  });

  $('.toggle-id-2').on('click', function(e) {
    // Stop default action and bubbling
    e.stopPropagation();
    e.preventDefault();
    controller.toggle('id-2');
  });

  $('.filter-show').on('click', function(e){
    if ($(this).parent().hasClass('show')) {
      $(this).parent().removeClass('show');
      $(this).text('Show all');
    } else {
      $(this).parent().addClass('show');
      $(this).text('Hide');
    }
  });

  $('#reset').on('click', function(e) {
    e.preventDefault();
    $(this).parents('[off-canvas]').find('input[type="checkbox"]:checked').each(function(e) {
      $(this).prop('checked', false);
    })
  })

  $('[off-canvas]').on('swipeleft', function(e) {
    controller.close();
  })

  $('input[name="select-category"]').on('change', function(e) {
    var checked = $('input[name="select-category"]:checked');
    var class_to_show = checked.val();
    var blocs_to_show = $(`.mobile-filters .checkboxes.${class_to_show}`);

    $('.mobile-filters .checkboxes').removeClass('is-visible');

    blocs_to_show.addClass('is-visible');
  });

	$('input[name="select-category"]').trigger('change');

});
