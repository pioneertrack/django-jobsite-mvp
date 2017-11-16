$(function () {

  function cutText () {
    $('.cut-text').each(function (i) {
      len = $(this).text().length
      if (len > $(this).data('cut')) {
        $(this).text($(this).text().substr(0, $(this).data('cut')) + '...')
      }
    })
  }

  cutText()

  // ########
  // Search
  // ########

  // underscore templates
  var person = startup = job = null
  if (window.location.pathname === '/search/') {
    var person = _.template($('#search_person_template').html())
    var startup = _.template($('#search_startup_template').html())
    var job = _.template($('#search_job_template').html())
  }

  var currentPage = 1
  var currentSearchData = []
  var end_of_results = false
  var is_active_request = false

  /**
   * Renders search results in main container
   * @param data Object
   */
  function render_search (data) {
    if (data.length > 0) {

      data.forEach(function (item) {
        switch (item._type) {
          case 'people_document':
            $('main .container .row').append(person({'data': item}))
            break
          case 'startup_document':
            $('main .container .row').append(startup({'data': item}))
            break
          case 'job_document':
            $('main .container .row').append(job({'data': item}))
            break
        }
      })

      cutText()

    } else if (currentPage == '0') {
      // underscore template (base.html)
      $('main .container .row').
        html(_.template($('#empty_search_template').html())())
    }
  }

  /**
   * Retrieve search results
   */
  function getSearchResults () {
    if (!end_of_results && !is_active_request) {
      is_active_request = true

      $.ajax('/search/' + currentPage + '/', {
        method: 'GET',
        // data: $('#mainform').serializeArray(),
        success: function (response) {
          is_active_request = false
          render_search(response)
          if (response.length) {
            currentPage++
          }
          else {
            end_of_results = true
            $(window).unbind('scroll', searchLazyLoad)
            $(document).unbind('touchmove', searchLazyLoadMobile)
          }
        },
        error: function () {
          is_active_request = false
        },
      })
    }
  }

  function postSearchResults () {
    if (!end_of_results && !is_active_request) {
      is_active_request = true
      $.ajax('/search/', {
        method: 'POST',
        data: $('#mainform').serializeArray(),
        success: function (response) {
          is_active_request = false
          render_search(response)
          if (response.length) {
            currentPage++
          }
          else {
            end_of_results = true
            $(window).unbind('scroll', searchLazyLoad)
            $(document).unbind('touchmove', searchLazyLoadMobile)
          }
        },
        error: function () {
          is_active_request = false
        },
      })
    }
  }

  /**
   * Lazy load search result on scroll
   */
  function searchLazyLoadMobile () {
    if ($(window).scrollTop() + $(window).height() >=
      $(document).height() - 500) {
      getSearchResults()
    }
  }

  function searchLazyLoad () {
    if ($(window).scrollTop() + $(window).height() >=
      $(document).height() - 500) {
      getSearchResults()
    }
  }

  /**
   * Apply logic to form
   */
  $('#mainform').on('submit', function (e) {
    var search_state = {
      filter: $('#mainform').serializeArray(),
      tags_people: $('#tags_people').html(),
      tags_startups: $('#tags_startups').html(),
      tags_jobs: $('#tags_jobs').html(),
    }
    if (window.location.pathname === '/search/') {
      history.pushState({search_state: search_state}, 'search')
    } else {
      window.sessionStorage.setItem('search_state',
        JSON.stringify(search_state))
    }
  })

  if (window.location.pathname === '/search/') {
    $('#mainform').on('submit', function (e) {
      // clear previous data
      currentPage = 0
      currentSearchData = []
      end_of_results = false
      $(window).unbind('scroll', searchLazyLoad)
      $(window).scroll(searchLazyLoad)
      $(document).unbind('touchmove', searchLazyLoadMobile)
      $(document).on('touchmove', searchLazyLoadMobile)

      // clear main container
      $('main .container .row').html('')

      // scroll to top
      $('body,html').animate({scrollTop: 0}, 0)

      // results
      postSearchResults()

      // prevent actual submit
      return false
    })
  }

  $(window).scroll(searchLazyLoad)
  $(document).on('touchmove', searchLazyLoadMobile)

  if ((history.state !== null && history.state.hasOwnProperty('search_state')) ||
    window.sessionStorage.getItem('search_state') !== null) {
    if (window.sessionStorage.getItem('search_state') !== null) {
      var search_state = JSON.parse(window.sessionStorage.getItem('search_state'))
      window.sessionStorage.removeItem('search_state');
      history.pushState({search_state: search_state}, 'search')
    } else {
      var search_state = history.state.search_state
    }
    $.each(search_state.filter, function (key, item) {
      if ($('select[name="' + item.name + '"]').size() > 0) {
        $('select[name=' + item.name + '] option[value="' + item.value + '"]').
          prop('selected', true)
      } else if ($('input[name="' + item.name + '"][value="' + item.value +
          '"]').size() > 0) {
        $('input[name="' + item.name + '"][value="' + item.value + '"]').
          prop('checked', true)
      } else {
        if ($('[name="' + item.name + '"]').size() > 0) {
          $('[name="' + item.name + '"]').val(item.value)
        }
      }

    })
    $('#tags_people').html(search_state.tags_people)
    $('#tags_startups').html(search_state.tags_startups)
    $('#tags_jobs').html(search_state.tags_jobs)
  }

  if (history.state !== null && history.state.hasOwnProperty('search_state')) {
    $('.cd-search-nav.first select.filter').niceSelect()
  }

  function fillControls () {
    var class_to_show = $('[name="select-category"]:checked').val()
    var blocs_to_show = $('.cd-search-nav.tags .tags.' + class_to_show +
      ', .cd-search-nav.first .selects.' + class_to_show)
    var tags_to_show = $('.cd-search-nav.tags .tags.' + class_to_show)

    $('.cd-search-nav.tags .tags').removeClass('is-visible')
    $('.cd-search-nav.tags .tags').removeClass('selected')
    $('.cd-search-nav.first .selects').removeClass('is-visible')

    tags_to_show.addClass('selected')
    blocs_to_show.addClass('is-visible')
  }

  fillControls();
})