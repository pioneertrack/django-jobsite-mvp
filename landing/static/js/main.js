$(document).ready(function () {

  var checkScroll = function () {
    var scroll = $(window).scrollTop()
    var lower = 200
    var upper = 400

    if (scroll > lower && scroll <= upper) {
      $('.navbar').
        css('background', 'rgba(255,184,25,' +
          ((scroll - lower) / lower).toString() + ')')
    } else if (scroll > upper) {
      $('.navbar').css('background', 'rgb(255,184,25)')
    } else {
      $('.navbar').css('background', 'transparent')
    }
  }

  checkScroll()

  $(window).scroll(checkScroll)

  var navHeight = $('.navbar').height()

  $('.navbar-brand, #navbarSupportedContent a').on('click', function (event) {
    if (this.hash !== '') {
      event.preventDefault()
      var hash = this.hash
      $('html, body').animate({
        scrollTop: $(hash).offset().top - navHeight - 50,
      }, 1000)
    }
  })

  $('.carousel').carousel({
    interval: 5000,
  })
})