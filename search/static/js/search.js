$(function() {

  function cutText() {
    $('.cut-text').each(function(i) {
      len = $(this).text().length;
      if (len > $(this).data('cut')) {
        $(this).text($(this).text().substr(0, $(this).data('cut')) + '...');
      }
    });
  }

  cutText();

  // ########
  // Search
  // ########

  // underscore templates
  var person = _.template($('#search_person_template').html());
  var startup = _.template($('#search_startup_template').html());
  var job = _.template($('#search_job_template').html());

  var currentPage = 1;
  var currentSearchData = [];
  var end_of_results = false;
  var is_active_request = false;

  /**
   * Renders search results in main container
   * @param data Object
   */
  function render_search(data) {
    if (data.length > 0) {

      data.forEach(function(item) {
        switch (item._type) {
          case 'people_document':
            $('main .container .row').append(person({'data': item}));
            break;
          case 'startup_document':
            $('main .container .row').append(startup({'data': item}));
            break;
          case 'job_document':
            $('main .container .row').append(job({'data': item}));
            break;
        }
      });

      cutText();

    } else if (currentPage == '0') {
      // underscore template (base.html)
      $('main .container .row').
          html(_.template($('#empty_search_template').html())());
    }
  }

  /**
   * Retrieve search results
   */
  function getSearchResults() {
    if (!end_of_results && !is_active_request) {
      is_active_request = true;

      $.ajax('/search/' + currentPage + '/', {
        method: 'GET',
        // data: $('#mainform').serializeArray(),
        success: function(response) {
          is_active_request = false;
          render_search(response);
          if (response.length) {
            currentPage++;
          }
          else {
            end_of_results = true;
            $(window).unbind('scroll', searchLazyLoad);
          }
        },
        error: function() {
          is_active_request = false;
        },
      });
    }
  }

  function postSearchResults() {
    if (!end_of_results && !is_active_request) {
      is_active_request = true;
      $.ajax('/search/', {
        method: 'POST',
        data: $('#mainform').serializeArray(),
        success: function(response) {
          is_active_request = false;
          render_search(response);
          if (response.length) {
            currentPage++;
          }
          else {
            end_of_results = true;
            $(window).unbind('scroll', searchLazyLoad);
          }
        },
        error: function() {
          is_active_request = false;
        },
      });
    }
  }

  /**
   * Lazy load search result on scroll
   */
  function searchLazyLoad() {
    if ($(window).scrollTop() + $(window).height() >=
        $(document).height() - 250) {
      getSearchResults();
    }
  }

  /**
   * Apply logic to form
   */
  $('#mainform').on('submit', function(e) {
    var d = new Date();
    d.setTime(d.getTime() + (24 * 60 * 60 * 1000));
    var expires = 'expires=' + d.toUTCString();
    document.cookie = 'select-category=None;' +
        expires + ';path=/';
    history.pushState({filter: $('#mainform').serializeArray()}, 'search')

    // clear previous data
    currentPage = 0;
    currentSearchData = [];
    end_of_results = false;
    $(window).unbind('scroll', searchLazyLoad);
    $(window).scroll(searchLazyLoad);

    // sessionStorage.setItem(JSON.stringify())

    // clear main container
    $('main .container .row').html('');

    // scroll to top
    $('body,html').animate({scrollTop: 0}, 0);

    // results
    postSearchResults();

    // prevent actual submit
    return false;
  });

  $(window).scroll(searchLazyLoad);

});