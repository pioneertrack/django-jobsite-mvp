$(function () {

    $('input#select-both-profiles').on('change', function () {
        console.log($(this).is(":checked"));
        $('input#id_is_founder, input#id_is_individual').prop('checked', $(this).is(":checked"));
    });

    $('ul#cd-navigation ul.list li').on('click', function () {
        window.location.href = $(this).attr('data-value');
    });

    $('button#disable-account').on('click', function () {
        if (confirm('Are you sure you want to disable your account?')) {
            $(this).parent().find('form').submit();
        }
    });

    $('button#enable-account').on('click', function () {
        if (confirm('Are you sure you want to enable your account?')) {
            $(this).parent().find('form').submit();
        }
    });

    $(".first div.nice-select ul.list").mCustomScrollbar({
        theme: "3d-thick-dark",
        scrollInertia: 300
    });

    // browser window scroll (in pixels) after which the "back to top" link is shown
    var offset = 300,
        //duration of the top scrolling animation (in ms)
        scroll_top_duration = 500,
        //grab the "back to top" link
        $back_to_top = $('.cd-top');

    //hide or show the "back to top" link
    $(window).scroll(function () {
        ( $(this).scrollTop() > offset ) ? $back_to_top.addClass('cd-is-visible') : $back_to_top.removeClass('cd-is-visible cd-fade-out');
    });

    //smooth scroll to top
    $back_to_top.on('click', function (event) {
        event.preventDefault();
        $('body,html').animate({
                scrollTop: 0
            }, scroll_top_duration
        );
    });

    if (!Modernizr.input.placeholder) {
        $('[placeholder]').focus(function () {
            var input = $(this);
            if (input.val() == input.attr('placeholder')) {
                input.val('');
            }
        }).blur(function () {
            var input = $(this);
            if (input.val() == '' || input.val() == input.attr('placeholder')) {
                input.val(input.attr('placeholder'));
            }
        }).blur();
        $('[placeholder]').parents('form').submit(function () {
            $(this).find('[placeholder]').each(function () {
                var input = $(this);
                if (input.val() == input.attr('placeholder')) {
                    input.val('');
                }
            })
        });
    }

    $("#connect").on('click', function () {
        console.log('clicked')
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
                    }, 1000)
                })
            },
            allowOutsideClick: false
        }).then(function (text) {
            $.ajax({
                type: "POST",
                url: "/connect/",
                data: {
                    'text': text,
                    'user_page_id': user_page_id,
                },
                success: function (data) {
                    console.log('email sent');
                    swal({
                        type: 'success',
                        title: 'Your message is on its way!',
                        html: 'We have contacted ' + name + ". We hope you hear back soon."
                    })
                },
                error: function (xhr, textStatus, errorThrown) {
                    swal({
                        type: 'error',
                        title: 'Something went wrong on our end',
                        html: 'Please try again'
                    })
                }
            });

        })
    });

    $("#selector").on('change', function (e) {
        var class_to_show = $(this).val();
        var blocs_to_show = $('.cd-search-nav.tags .tags.' + class_to_show + ', .cd-search-nav.first .selects.' + class_to_show);

        $('.cd-search-nav.tags .tags').removeClass('is-visible');
        $('.cd-search-nav.first .selects').removeClass('is-visible');

        blocs_to_show.addClass('is-visible');
    });

    $("#selector").trigger('change');

    $("#view_type").on('change', function (e) {
        if ($(this).prop('checked')) {
            $('.job-card:first').parents('.container').addClass('list');
        } else {
            $('.job-card:first').parents('.container').removeClass('list');
        }
    });

    setTimeout(function () {
        $('.message').fadeOut('slow');
    }, 3500);

    $('#searchbutton').on('click', function (e) {
        $.ajax('/search/', {
            method: "POST",
            data: $('#mainform').serialize(),
            success: function (response) {
                var compiled = _.template($("#item_template").html());
                $('main .container').html(compiled({"data": response}));
            }
        });

        return false;
    });

});
