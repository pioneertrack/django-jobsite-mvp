$(function () {

  function setCookie (cname, cvalue, exdays) {
    var d = new Date()
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000))
    var expires = 'expires=' + d.toUTCString()
    document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/'
  }

  function getCookie (cname) {
    var name = cname + '='
    var ca = document.cookie.split(';')
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i]
      while (c.charAt(0) == ' ') {
        c = c.substring(1)
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length)
      }
    }
    return ''
  }

  if (getCookie('clear_profile')) {
    var i = 0;
    while (i < localStorage.length) {
      key = localStorage.key(i)
      if (key.search('sadfjlksdfasdfklsadf') !== -1) {
        localStorage.removeItem(key)
      } else {
        i++;
      }
    }
    setCookie('clear_profile', '', -1);
  }

  $('input#select-both-profiles').on('change', function () {
    $('input#id_is_founder, input#id_is_individual').
      prop('checked', $(this).is(':checked'))
  })

  $('button#disable-account').on('click', function () {
    if (confirm('Are you sure you want to disable your account?')) {
      $(this).parent().find('form').submit()
    }
  })

  $('button#enable-account').on('click', function () {
    if (confirm('Are you sure you want to enable your account?')) {
      $(this).parent().find('form').submit()
    }
  })

  if (typeof $().mCustomScrollbar !== 'undefined') {
    $('.first div.nice-select ul.list').mCustomScrollbar({
      theme: '3d-thick-dark',
      scrollInertia: 300,
    })
  }

  // browser window scroll (in pixels) after which the "back to top" link is shown
  var offset = 300,
    //duration of the top scrolling animation (in ms)
    scroll_top_duration = 500,
    //grab the "back to top" link
    $back_to_top = $('.cd-top')

  //hide or show the "back to top" link
  $(window).scroll(function () {
    ($(this).scrollTop() > offset)
      ? $back_to_top.addClass('cd-is-visible')
      : $back_to_top.removeClass('cd-is-visible cd-fade-out')
  })
  //smooth scroll to top
  $back_to_top.on('click', function (event) {
    event.preventDefault()
    $('body,html').animate({
        scrollTop: 0,
      }, scroll_top_duration,
    )
  })

  $.ajaxSetup({
       beforeSend: function(xhr, settings) {
           function getCookie(name) {
               var cookieValue = null;
               if (document.cookie && document.cookie != '') {
                   var cookies = document.cookie.split(';');
                   for (var i = 0; i < cookies.length; i++) {
                       var cookie = jQuery.trim(cookies[i]);
                       // Does this cookie string begin with the name we want?
                       if (cookie.substring(0, name.length + 1) == (name + '=')) {
                           cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                           break;
                       }
                   }
               }
               return cookieValue;
           }
           if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
               // Only send the token to relative URLs i.e. locally.
               xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
           }
       }
  });

  function connectRequest(text, profile_type = null) {
      $.ajax({
        type: 'POST',
        url: '/connect/',
        data: {
          'text': text,
          'profile_id': $('#profile_id').val(),
          'profile_type': profile_type,
        },
        success: function (data) {
          swal({
            type: 'success',
            title: 'Your message is on its way!',
            html: 'We have contacted ' + $('#profile_name').val() + '. We hope you hear back soon.',
          })
        },
        error: function (xhr, textStatus, errorThrown) {
          swal({
            type: 'error',
            title: 'Something went wrong on our end',
            html: 'Please try again',
          })
        },
      })
  }

  $('#connect').on('click', function () {
    swal({
      title: 'Give a description of you or your project',
      text: 'It\'s best to include your name, email, and/or phone number so they can contact you back',
      input: 'textarea',
      showCancelButton: true,
      confirmButtonText: 'Connect',
      showLoaderOnConfirm: true,
      preConfirm: function (text) {
        return new Promise(function (resolve, reject) {
          setTimeout(function () {
            if (text.length == 0) {
              reject('Please write a short description')
            } else {
              resolve()
            }
          }, 500)
        })
      },
      allowOutsideClick: false,
    }).then(function (text) {
      if ($('#select_profiles').val() == 1) {
        swal({
          text: 'Select a link to which profile to add to the message',
          showCancelButton: true,
          cancelButtonColor: '#3085d6',
          cancelButtonText: 'Startup',
          confirmButtonText: 'Individual',
          allowOutsideClick: false,
          showLoaderOnConfirm: true,
        }).then(function (value) {
          connectRequest(text, 'individual')
        },
          function (dismiss) {
            if (dismiss === 'cancel') {
              connectRequest(text, 'startup')
            }
          })
      } else {
        connectRequest(text)
      }
    })
  })

  $(document).on('click', '.feedback', function (e) {
    e.preventDefault()
    swal({
      title: 'Think We Can Improve?',
      text: 'Tell us anything! We\'ll do what we can to make Bear Founders a better platform.',
      input: 'textarea',
      inputPlaceholder: 'I think you really need an events page',
      showCancelButton: true,
      confirmButtonText: 'Send',
      showLoaderOnConfirm: true,
      preConfirm: function (text) {
        return new Promise(function (resolve, reject) {
          setTimeout(function () {
            if (text.length == 0) {
              reject('Please write a message')
            } else {
              resolve()
            }
          }, 500)
        })
      },
      allowOutsideClick: false,
    }).then(function (data) {
      $.ajax({
        type: 'POST',
        url: '/feedback/',
        data: {
          'message': data,
        },
        success: function (data) {
          swal({
            type: 'success',
            title: 'Your message is on its way!',
            html: 'Thank you! We appreciate your insights.',
          })
        },
        error: function (xhr, textStatus, errorThrown) {
          swal({
            type: 'error',
            title: 'Something went wrong on our end',
            html: 'Please try again',
          })
        },
      })
    },
    function (dismiss) {
    })
  })

  $('#view_type').on('change', function (e) {
    if ($(this).prop('checked')) {
      $('.job-card:first').parents('.container').addClass('list')
    } else {
      $('.job-card:first').parents('.container').removeClass('list')
    }
  })

  setTimeout(function () {
    $('.message').fadeOut('slow')
  }, 3500)

  $('.smooth-scroll a[href*="#"]:not([href="#"])').click(function () {
    if (location.pathname.replace(/^\//, '') ==
      this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      var target = $(this.hash)
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']')
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top,
        }, 1000)
        return false
      }
    }
  })

})
