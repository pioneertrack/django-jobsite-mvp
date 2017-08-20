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

  $('.toggle-id-1-find').on('click', function(e) {
    controller.close('id-1');
    controller.close('id-2');
    // $('.loading-overlay').show();
  });

  $( controller.events ).on( 'closed', function ( event, id ) {
    event.stopPropagation();
    // console.log( 'Slidebar ' + id + ' is open.' );
  } );
  $( controller.events ).on( 'opened', function ( event, id ) {
    event.stopPropagation();
    // console.log( 'Slidebar ' + id + ' is open.' );
  } );

  $('.filter-show, [name="select-category"]').on('click', function(e){
    if ($(this).parents('.filter-container:first').hasClass('show')) {
      $(this).parents('.filter-container:first').removeClass('show');
      if ($(this).prop("tagName") === 'BUTTON') {
        $(this).text('Show all');
      }
    } else {
      $(this).parents('.filter-container:first').addClass('show');
      if ($(this).prop("tagName") === 'BUTTON') {
        $(this).text('Hide');
      }
    }
    if ($(this).prop("name") === 'select-category') {
      var value = $('[name="select-category"]:checked').val();
      $(this).parents('.checkboxes').find('.current').text(value);
      controller.open('id-2');
    }
  });

  $('#reset').on('click', function(e) {
    e.preventDefault();
    var current = $(this).parents('[off-canvas]').find('.checkboxes.is-visible');
    current.find('input[type="checkbox"]:checked').each(function(e) {
      $(this).prop('checked', false);
    })
  })


  $('input[name="select-category"]').on('change', function(e) {
    var checked = $('input[name="select-category"]:checked');
    var class_to_show = checked.val();
    var blocs_to_show = $('.mobile-filters .checkboxes.' + class_to_show);

    $('.mobile-filters .checkboxes').removeClass('is-visible');

    blocs_to_show.addClass('is-visible');
  });

	$('input[name="select-category"]').trigger('change');

  $(".mobile-filters.search-select").on('swiperight',  function(){
    controller.open('id-2');
  })

  $(".mobile-filters.filter-select").on('swipeleft',  function(e){
    e.stopPropagation();
    controller.close('id-2');
  })

  $(".mobile-filters.search-select").on('swipeleft',  function(){
    controller.close('id-1');
  })

});
