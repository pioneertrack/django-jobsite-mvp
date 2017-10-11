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

  var currentPage = 0;
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
            $('main .container .row').append(person({'item': item._source}));
            break;
          case 'startup_document':
            $('main .container .row').append(startup({'item': item._source}));
            break;
          case 'job_document':
            $('main .container .row').append(job({'item': item._source}));
            break;
        }
      });

      cutText();

    } else if (currentPage == '0') {
      // underscore template (base.html)
      $('main .container').
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
          if (Object.keys(response).length) {
            currentPage++;
          }
          else {
            end_of_results = true;
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
    // clear previous data
    currentPage = 0;
    currentSearchData = [];
    end_of_results = false;

    // clear main container
    $('main .container').html('');

    // "redirect" to mainpage
    // history.pushState({}, 'Home', '/');

    // scroll to top
    $('body,html').animate({scrollTop: 0}, 0);

    // results
    getSearchResults();

    // prevent actual submit
    return false;
  });

  $(window).scroll(function() {
    searchLazyLoad();
  });

});