$(document).ready(function(){
    var checkScroll = function(){
        var scroll = $(window).scrollTop();
        if (scroll > 200) {
            $('.navbar').css('background' , '#FFB819');
        } else {
            $('.navbar').css('background' , 'transparent');
        }
    };
    
    checkScroll();

    $(window).scroll(checkScroll);

    var navHeight = $('.navbar').height();
    
    $('.navbar-brand, #navbarSupportedContent a').on('click', function(event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top - navHeight - 50
            }, 1000);
        }
    });

    $('.carousel').carousel({
        interval: 3000,
    });
});