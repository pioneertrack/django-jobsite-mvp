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

  // underscore template for person (base.html)
  var person = _.template($("#search_person_template").html());
  var startup = _.template($("#search_startup_template").html());
  var job = _.template($("#search_job_template").html());

  var currentPage = 0;
  var currentSearchData = [];
  var end_of_results = false;
  var is_active_request = false;

  /**
   * Renders search results in main container
   * @param data Object
   */
  function render_search(data) {
    if (Object.keys(data.items).length) {

      Object.keys(data.items).forEach(function(key) {
        switch (data.category) {
          case 'people':
            $('main .container').append(person({"item": data.items[key]}));
            break;
          case 'startups':
            $('main .container').append(startup({"item": data.items[key]}));
            break;
          case 'jobs':
            $('main .container').append(job({"item": data.items[key]}));
            break;
        }
      });

      cutText();

    } else if (currentPage == '0') {
      // underscore template (base.html)
      $('main .container').
          html(_.template($("#empty_search_template").html())());
    }
  }

  /**
   * Retrieve search results
   */
  function getSearchResults() {
    if (!end_of_results && !is_active_request) {
      is_active_request = true;
      $.ajax('/api/search/' + currentPage + '/', {
        method: "POST",
        data: $('#mainform').serializeArray(),
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
        }
      });
    }
  }

  /**
   * Lazy load search result on scroll
   */
  function searchLazyLoad() {
    if (location.pathname == '/') {
      if ($(window).scrollTop() + $(window).height() >=
          $(document).height() - 250) {
        getSearchResults();
      }
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
    history.pushState({}, 'Home', '/');

    // scroll to top
    $('body,html').animate({scrollTop: 0}, 0);

    // results
    getSearchResults();

    // prevent actual submit
    return false;
  });
})