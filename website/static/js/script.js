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

  $('ul#cd-navigation ul.list li').on('click', function () {
    window.location.href = $(this).attr('data-value')
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

  $('.first div.nice-select ul.list').mCustomScrollbar({
    theme: '3d-thick-dark',
    scrollInertia: 300,
  })

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

  if (!Modernizr.input.placeholder) {
    $('[placeholder]').focus(function () {
      var input = $(this)
      if (input.val() == input.attr('placeholder')) {
        input.val('')
      }
    }).blur(function () {
      var input = $(this)
      if (input.val() == '' || input.val() == input.attr('placeholder')) {
        input.val(input.attr('placeholder'))
      }
    }).blur()
    $('[placeholder]').parents('form').submit(function () {
      $(this).find('[placeholder]').each(function () {
        var input = $(this)
        if (input.val() == input.attr('placeholder')) {
          input.val('')
        }
      })
    })
  }

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
    $(this).
    swal({
      title: 'Send feedback to site administration',
      text: 'It\'s best to include your name, email, and/or phone number so they can contact you back',
      input: 'textarea',
      showCancelButton: true,
      confirmButtonText: 'Connect',
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
    }).then(function (text) {
      $.ajax({
        type: 'POST',
        url: '/feedback/',
        data: {
          'text': text,
        },
        success: function (data) {
          swal({
            type: 'success',
            title: 'Your message is on its way!',
            html: 'We send You feedback. We hope you hear back soon.',
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

})
