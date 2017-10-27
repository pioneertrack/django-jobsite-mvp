jQuery(document).ready(function($) {

  if (history.state === null || history.state.hasOwnProperty('search_state') === false) {
    $('#selector').niceSelect();
    $('.cd-search-nav.first select.filter').niceSelect();
  }
  $('ul#cd-navigation select.filter').niceSelect();
  $('ul#cd-navigation ul.list li:first').hide();

  $('#profiles_holder').on('click', function(e) {
    e.preventDefault();
  })

  $('ul#cd-navigation ul.list li').on('click', function() {
    window.location.href = $(this).attr('data-value');
  });

  $(document).on('mouseleave', '.tags', function(e) {
    var tags = $(this).children('.filter-container');
    var children = $(tags.children(':not(.outer)').get().reverse());
    children.each(function(i) {
      var tag = $(this);
      if (tag.offset().left + tag.outerWidth() >
          tags.offset().left + tags.outerWidth()) {
        tag.addClass('outer');
      }
    })
  })

  $(document).on('click', 'span.label-clear', function(e) {
    var tags = $(this).parent();
    tags.find('span[data-role="remove"]').each(function(e) {
      $(this).trigger('click');
    })
  })

  $(document).on('click', 'span.tag span[data-role="remove"]', function(e) {
    var data_value = $(this).parent().data('value');
    var data_name = $(this).parent().data('name');
    var selector = $("#selector").val();
    var tags = $(`#tags_${selector}`);
    var select = $(`select[name="${data_name}"]`);
    var data_class = select.data('class');

    if (tags.children().length === 2) {
      tags.parent().removeClass('selected');
      $('.messages.tags').removeClass('tags');
    }
    $(this).parent().remove();
    tags.children('.outer').each(function(i) {
      var tag = $(this);
      if (tag.offset().left + tag.outerWidth() <
          tags.offset().left + tags.outerWidth()) {
        tag.removeClass('outer');
      }
    });
    select.children(`option[value="${data_value}"]`).prop('selected', false);
    select.next().
        find(`li[data-value="${data_value}"]`).
        removeClass('selected');

    if (select.val().length === 1) {
      var option_all = select.next().find('li:first');
      if (option_all.data('all') === 0) {
        var inrevert = option_all.text();
        option_all.data('all', 1);
        option_all.text(option_all.data('revert') || null);
        option_all.data('revert', inrevert);
      }
    }
  })

  $('.cd-search-nav.first select.filter option').
      bind('option_change.nice_select', function(e) {
        var selector = $("#selector").val();
        var tags = $(`#tags_${selector}`);
        var data_value = $(this).val();
        var data_name = $(this).parent().attr('name');
        var data_class = $(this).parent().data('class');
        if ($(this).prop('selected')) {
          tags.parent().addClass('selected');
          if ($('.messages').hasClass('tags') === false) {
            $('.messages').addClass('tags');
          }
          if (tags.children().length === 0) {
            var tag_clear = $(`<span class="tag label label-clear"></span>`).
                text('Clear All');
            tag_clear.prependTo(tags);
          } else {
            var tag_clear = tags.children('.label-clear');
          }
          var tag = $(`<span class="tag label ${data_class}"></span>`).
              attr('data-value', data_value).
              attr('data-name', data_name).
              text($(this).text());
          tag.append('<span data-role="remove"></span>');
          tag.insertAfter(tag_clear);
          $(tags.children(':not(.outer)').get().reverse()).each(function(i) {
            var tag = $(this);
            if (tag.offset().left + tag.outerWidth() >
                tags.offset().left + tags.outerWidth()) {
              tag.addClass('outer');
            }
          })
        } else {
          if (tags.children().length === 2) {
            tags.parent().removeClass('selected');
            $('.messages.tags').removeClass('tags');
          }
          tags.find(
              `.tag[data-value="${data_value}"][data-name="${data_name}"]`).
              remove();
          tags.children('.outer').each(function(i) {
            var tag = $(this);
            if (tag.offset().left + tag.outerWidth() <
                tags.offset().left + tags.outerWidth()) {
              tag.removeClass('outer');
            }
          });
        }
      })
});