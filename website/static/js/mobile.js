jQuery(document).ready(function($){
  // Initialize Slidebars
  var controller = new slidebars();
  controller.init();
  // Toggle Slidebars
  $('.toggle-id-1').on('click', function(e) {
    // Stop default action and bubbling
    e.stopPropagation();
    e.preventDefault();

    // Toggle the Slidebar with id 'id-1'
    controller.toggle('id-1');
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

  $("#selector").on('change', function(e) {
    var class_to_show = $(this).val();
    var blocs_to_show = $(`.mobile-filters .checkboxes.${class_to_show}`);

    $('.mobile-filters .checkboxes').removeClass('is-visible');

    blocs_to_show.addClass('is-visible');

    if ($(this).val() === 'jobs') {
      $('.cd-dropdown-content.people').hide();
      $('.cd-dropdown-content.jobs').show();
    } else {
      $('.cd-dropdown-content.jobs').hide();
      $('.cd-dropdown-content.people').show();
    }
  });

	$("#selector").trigger('change');

});
