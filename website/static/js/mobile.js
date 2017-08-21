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

  $( controller.events ).on( 'closing', function ( event, id ) {
      if (controller.isActiveSlidebar('id-2')) {
        controller.close('id-2');
      }
  });

  $( controller.events ).on( 'closed', function ( event, id ) {
    event.stopPropagation();
    if (id == 'id-1') {
      $(document).unbind('swiperight.mobile');
      $(document).unbind('swipeleft.mobile');
    }
    if (id == 'id-2') {
      $(document).unbind('swiperight.mobile');
    }
    // console.log( 'Slidebar ' + id + ' is closed.' );
  } );

  $( controller.events ).on( 'opened', function ( event, id ) {
    event.stopPropagation();
    $(document).bind('swipeleft.mobile', function (e) {
      controller.close('id-2');
      controller.close('id-1');
    });
    if (id == 'id-2') {
      $(document).bind('swiperight.mobile', function (e) {
        controller.close('id-2');
        $(document).unbind('swiperight.mobile');

      });
    }
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

  window.addEventListener("orientationchange", function() {
    controller.close('id-1');
    controller.close('id-2');
  }, false);

  $('input[name="select-category"]').on('change', function(e) {
    var checked = $('input[name="select-category"]:checked');
    var class_to_show = checked.val();
    var blocs_to_show = $('.mobile-filters .checkboxes.' + class_to_show);

    $('.mobile-filters .checkboxes').removeClass('is-visible');

    blocs_to_show.addClass('is-visible');
  });

	$('input[name="select-category"]').trigger('change');

  // $('ul#cd-navigation select.filter').niceSelect();

});
