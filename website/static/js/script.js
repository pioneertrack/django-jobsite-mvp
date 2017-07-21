jQuery(document).ready(function($){

  $('.cd-search-nav.first select.filter').niceSelect();

  showDropdown = function (element) {
      var event;
      event = document.createEvent('MouseEvents');
      event.initMouseEvent('mousedown', true, true, window);
      element.dispatchEvent(event);
  };

  $(document).on('mouseenter', '#selector', function(e) {
    var dropdown = document.getElementById('selector');
    showDropdown(dropdown);
  })

  // $(document).on('click', '#selector', function(e) {
  //   console.log('click');
  // })

  $(document).on('click', 'span.tag span[data-role="remove"]', function(e) {
    var data_value = $(this).parent().data('value');
    var data_name = $(this).parent().data('name');
    var selector = $("#selector").val();
    var tags = $(`#tags_${selector}`);
    var select = $(`select[name="${data_name}"]`);
    var filter_input = $(`#filter_${selector}`);

    if (tags.children().length === 1) {
      tags.parent().removeClass('selected');
      $('.messages.tags').removeClass('tags');
    }
    $(this).parent().remove();
    tags.children('.outer').each(function(i) {
        var tag = $(this);
        if (tag.offset().left + tag.outerWidth() < tags.offset().left + tags.outerWidth()) {
          tag.removeClass('outer');
        }
    });
    select.children(`option[value="${data_value}"]`).prop('selected', false);
    select.next().find(`li[data-value="${data_value}"]`).removeClass('selected');

    //Remove data about tags from associated hidden field
    var str = `["${data_name}","${data_value}","${$(this).parent().text()}"]`;
    var value = filter_input.val();
    value = value.replace(str, '');
    value = value.replace(',,', ',');
    if (value.length > 0 && value[0] == ',') {
      value = value.substr(1);
    }
    if (value.length > 0 && value[value.length - 1] == ',') {
      value = value.substr(0, value.length -1);
    }
    filter_input.val(value);
  })

  $('.cd-search-nav.first select.filter option').bind('option_change.nice_select', function(e) {
    var selector = $("#selector").val();
    var tags = $(`#tags_${selector}`);
    var filter_input = $(`#filter_${selector}`);
    var data_value = $(this).val();
    var data_name = $(this).parent().attr('name');
    var data_class = $(this).parent().data('class');
    if ($(this).prop('selected')) {
      tags.parent().addClass('selected');
      if ($('.messages').hasClass('tags') === false) {
        $('.messages').addClass('tags');
      }
      var tag = $(`<span class="tag label ${data_class}"></span>`)
      .attr('data-value', data_value)
      .attr('data-name', data_name)
      .text($(this).text());
      tag.append('<span data-role="remove"></span>');
      tag.prependTo(tags);
      $(tags.children(':not(.outer)').get().reverse()).each(function (i) {
        var tag = $(this);
        if (tag.offset().left + tag.outerWidth() > tags.offset().left + tags.outerWidth()) {
          tag.addClass('outer');
        }
      })
      //To store order of tags in filter
      var punctuation = filter_input.val().length > 0 ? ',' : '';
      filter_input.val(`["${data_name}","${data_value}","${$(this).text()}"]${punctuation}` + filter_input.val());
    } else {
      if (tags.children().length === 1) {
        tags.parent().removeClass('selected');
        $('.messages.tags').removeClass('tags');
      }
      tags.find(`.tag[data-value="${data_value}"][data-name="${data_name}"]`).remove();
      tags.children('.outer').each(function(i) {
        var tag = $(this);
        if (tag.offset().left + tag.outerWidth() < tags.offset().left + tags.outerWidth()) {
          tag.removeClass('outer');
        }
      });
      var str = `["${data_name}","${data_value}","${$(this).text()}"]`;
      var value = filter_input.val();
      value = value.replace(str, '');
      value = value.replace(',,', ',');
      if (value.length > 0 && value[0] == ',') {
        value = value.substr(1);
      }
      if (value.length > 0 && value[value.length - 1] == ',') {
        value = value.substr(0, value.length -1);
      }
      filter_input.val(value);
    }
  })

	$('.selected-value').text($('#selector').val());
	// browser window scroll (in pixels) after which the "back to top" link is shown
	var offset = 300,
		//duration of the top scrolling animation (in ms)
		scroll_top_duration = 500,
		//grab the "back to top" link
		$back_to_top = $('.cd-top');

	//hide or show the "back to top" link
	$(window).scroll(function(){
		( $(this).scrollTop() > offset ) ? $back_to_top.addClass('cd-is-visible') : $back_to_top.removeClass('cd-is-visible cd-fade-out');
	});
	//smooth scroll to top
	$back_to_top.on('click', function(event){
		event.preventDefault();
		$('body,html').animate({
			scrollTop: 0 ,
		 	}, scroll_top_duration
		);
	});
	$('.cd-dropdown-trigger').on('click', function(event){
		event.preventDefault();
		toggleNav();
	});

	//close meganavigation
	$('.cd-dropdown .cd-close').on('click', function(event){
		event.preventDefault();
		toggleNav();
	});

	//on mobile - open submenu
	$('.has-children').children('a').on('click', function(event){
		//prevent default clicking on direct children of .has-children
		event.preventDefault();
		var selected = $(this);
		selected.next('ul').removeClass('is-hidden').end().parent('.has-children').parent('ul').addClass('move-out');
	});

	//on desktop - differentiate between a user trying to hover over a dropdown item vs trying to navigate into a submenu's contents
	var submenuDirection = ( !$('.cd-dropdown-wrapper').hasClass('open-to-left') ) ? 'right' : 'left';
	$('.cd-dropdown-content').menuAim({
        activate: function(row) {
        	$(row).children().addClass('is-active').removeClass('fade-out');
        	if( $('.cd-dropdown-content .fade-in').length == 0 ) $(row).children('ul').addClass('fade-in');
        },
        deactivate: function(row) {
        	$(row).children().removeClass('is-active');
        	if( $('li.has-children:hover').length == 0 || $('li.has-children:hover').is($(row)) ) {
        		$('.cd-dropdown-content').find('.fade-in').removeClass('fade-in');
        		$(row).children('ul').addClass('fade-out')
        	}
        },
        exitMenu: function() {
        	$('.cd-dropdown-content').find('.is-active').removeClass('is-active');
        	return true;
        },
        submenuDirection: submenuDirection,
    });

	//submenu items - go back link
	$('.go-back').on('click', function(){
		var selected = $(this),
			visibleNav = $(this).parent('ul').parent('.has-children').parent('ul');
		selected.parent('ul').addClass('is-hidden').parent('.has-children').parent('ul').removeClass('move-out');
	});

	function toggleNav(){
		var navIsVisible = ( !$('.cd-dropdown').hasClass('dropdown-is-active') ) ? true : false;
		$('.cd-dropdown').toggleClass('dropdown-is-active', navIsVisible);
		$('.cd-dropdown-trigger').toggleClass('dropdown-is-active', navIsVisible);
		if( !navIsVisible ) {
			$('.cd-dropdown').one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend',function(){
				$('.has-children ul').addClass('is-hidden');
				$('.move-out').removeClass('move-out');
				$('.is-active').removeClass('is-active');
			});
		}
	}
	if(!Modernizr.input.placeholder){
		$('[placeholder]').focus(function() {
			var input = $(this);
			if (input.val() == input.attr('placeholder')) {
				input.val('');
		  	}
		}).blur(function() {
		 	var input = $(this);
		  	if (input.val() == '' || input.val() == input.attr('placeholder')) {
				input.val(input.attr('placeholder'));
		  	}
		}).blur();
		$('[placeholder]').parents('form').submit(function() {
		  	$(this).find('[placeholder]').each(function() {
				var input = $(this);
				if (input.val() == input.attr('placeholder')) {
			 		input.val('');
				}
		  	})
		});
	}

	$("#connect").on('click', function(){
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
	      setTimeout(function() {
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
						'user': user,
				},
				success: function(data) {
						console.log('email sent');
						swal({
					    type: 'success',
					    title: 'Your message is on its way!',
					    html: 'We have contacted ' + name +". We hope you hear back soon."
					  })
				},
				error: function(xhr, textStatus, errorThrown) {
					swal({
						type: 'error',
						title: 'Something went wrong on our end',
						html: 'Please try again'
					})
				}
			});

		})
	})

  $("#selector").on('change', function(e) {
    var class_to_show = $(this).val();
    var blocs_to_show = $(`.cd-search-nav.first .tags.${class_to_show}, .cd-search-nav.first .selects.${class_to_show}`);

    $('.cd-search-nav.first .tags').removeClass('is-visible');
    $('.cd-search-nav.first .selects').removeClass('is-visible');

    blocs_to_show.addClass('is-visible');

    if ($(this).val() === 'jobs') {
      $('.cd-dropdown-content.people').hide();
      $('.cd-dropdown-content.jobs').show();
    } else {
      $('.cd-dropdown-content.jobs').hide();
      $('.cd-dropdown-content.people').show();
    }
  });

	$("#selector").trigger('change');
	
	$("#view_type").on('change', function(e) {
    if ($(this).prop('checked')) {
      $('.job-card:first').parents('.container').addClass('list');
    } else {
      $('.job-card:first').parents('.container').removeClass('list');
    }
  });

});

(function($) {

    $.fn.menuAim = function(opts) {
        // Initialize menu-aim for all elements in jQuery collection
        this.each(function() {
            init.call(this, opts);
        });

        return this;
    };

    function init(opts) {
        var $menu = $(this),
            activeRow = null,
            mouseLocs = [],
            lastDelayLoc = null,
            timeoutId = null,
            options = $.extend({
                rowSelector: "> li",
                submenuSelector: "*",
                submenuDirection: "right",
                tolerance: 75,  // bigger = more forgivey when entering submenu
                enter: $.noop,
                exit: $.noop,
                activate: $.noop,
                deactivate: $.noop,
                exitMenu: $.noop
            }, opts);

        var MOUSE_LOCS_TRACKED = 3,  // number of past mouse locations to track
            DELAY = 300;  // ms delay when user appears to be entering submenu

        /**
         * Keep track of the last few locations of the mouse.
         */
        var mousemoveDocument = function(e) {
                mouseLocs.push({x: e.pageX, y: e.pageY});

                if (mouseLocs.length > MOUSE_LOCS_TRACKED) {
                    mouseLocs.shift();
                }
            };

        /**
         * Cancel possible row activations when leaving the menu entirely
         */
        var mouseleaveMenu = function() {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }

                // If exitMenu is supplied and returns true, deactivate the
                // currently active row on menu exit.
                if (options.exitMenu(this)) {
                    if (activeRow) {
                        options.deactivate(activeRow);
                    }

                    activeRow = null;
                }
            };

        /**
         * Trigger a possible row activation whenever entering a new row.
         */
        var mouseenterRow = function() {
                if (timeoutId) {
                    // Cancel any previous activation delays
                    clearTimeout(timeoutId);
                }

                options.enter(this);
                possiblyActivate(this);
            },
            mouseleaveRow = function() {
                options.exit(this);
            };

        /*
         * Immediately activate a row if the user clicks on it.
         */
        var clickRow = function() {
                activate(this);
            };

        /**
         * Activate a menu row.
         */
        var activate = function(row) {
                if (row == activeRow) {
                    return;
                }

                if (activeRow) {
                    options.deactivate(activeRow);
                }

                options.activate(row);
                activeRow = row;
            };

        /**
         * Possibly activate a menu row. If mouse movement indicates that we
         * shouldn't activate yet because user may be trying to enter
         * a submenu's content, then delay and check again later.
         */
        var possiblyActivate = function(row) {
                var delay = activationDelay();

                if (delay) {
                    timeoutId = setTimeout(function() {
                        possiblyActivate(row);
                    }, delay);
                } else {
                    activate(row);
                }
            };

        /**
         * Return the amount of time that should be used as a delay before the
         * currently hovered row is activated.
         *
         * Returns 0 if the activation should happen immediately. Otherwise,
         * returns the number of milliseconds that should be delayed before
         * checking again to see if the row should be activated.
         */
        var activationDelay = function() {
                if (!activeRow || !$(activeRow).is(options.submenuSelector)) {
                    // If there is no other submenu row already active, then
                    // go ahead and activate immediately.
                    return 0;
                }

                var offset = $menu.offset(),
                    upperLeft = {
                        x: offset.left,
                        y: offset.top - options.tolerance
                    },
                    upperRight = {
                        x: offset.left + $menu.outerWidth(),
                        y: upperLeft.y
                    },
                    lowerLeft = {
                        x: offset.left,
                        y: offset.top + $menu.outerHeight() + options.tolerance
                    },
                    lowerRight = {
                        x: offset.left + $menu.outerWidth(),
                        y: lowerLeft.y
                    },
                    loc = mouseLocs[mouseLocs.length - 1],
                    prevLoc = mouseLocs[0];

                if (!loc) {
                    return 0;
                }

                if (!prevLoc) {
                    prevLoc = loc;
                }

                if (prevLoc.x < offset.left || prevLoc.x > lowerRight.x ||
                    prevLoc.y < offset.top || prevLoc.y > lowerRight.y) {
                    // If the previous mouse location was outside of the entire
                    // menu's bounds, immediately activate.
                    return 0;
                }

                if (lastDelayLoc &&
                        loc.x == lastDelayLoc.x && loc.y == lastDelayLoc.y) {
                    // If the mouse hasn't moved since the last time we checked
                    // for activation status, immediately activate.
                    return 0;
                }

                // Detect if the user is moving towards the currently activated
                // submenu.
                //
                // If the mouse is heading relatively clearly towards
                // the submenu's content, we should wait and give the user more
                // time before activating a new row. If the mouse is heading
                // elsewhere, we can immediately activate a new row.
                //
                // We detect this by calculating the slope formed between the
                // current mouse location and the upper/lower right points of
                // the menu. We do the same for the previous mouse location.
                // If the current mouse location's slopes are
                // increasing/decreasing appropriately compared to the
                // previous's, we know the user is moving toward the submenu.
                //
                // Note that since the y-axis increases as the cursor moves
                // down the screen, we are looking for the slope between the
                // cursor and the upper right corner to decrease over time, not
                // increase (somewhat counterintuitively).
                function slope(a, b) {
                    return (b.y - a.y) / (b.x - a.x);
                };

                var decreasingCorner = upperRight,
                    increasingCorner = lowerRight;

                // Our expectations for decreasing or increasing slope values
                // depends on which direction the submenu opens relative to the
                // main menu. By default, if the menu opens on the right, we
                // expect the slope between the cursor and the upper right
                // corner to decrease over time, as explained above. If the
                // submenu opens in a different direction, we change our slope
                // expectations.
                if (options.submenuDirection == "left") {
                    decreasingCorner = lowerLeft;
                    increasingCorner = upperLeft;
                } else if (options.submenuDirection == "below") {
                    decreasingCorner = lowerRight;
                    increasingCorner = lowerLeft;
                } else if (options.submenuDirection == "above") {
                    decreasingCorner = upperLeft;
                    increasingCorner = upperRight;
                }

                var decreasingSlope = slope(loc, decreasingCorner),
                    increasingSlope = slope(loc, increasingCorner),
                    prevDecreasingSlope = slope(prevLoc, decreasingCorner),
                    prevIncreasingSlope = slope(prevLoc, increasingCorner);

                if (decreasingSlope < prevDecreasingSlope &&
                        increasingSlope > prevIncreasingSlope) {
                    // Mouse is moving from previous location towards the
                    // currently activated submenu. Delay before activating a
                    // new menu row, because user may be moving into submenu.
                    lastDelayLoc = loc;
                    return DELAY;
                }

                lastDelayLoc = null;
                return 0;
            };

        /**
         * Hook up initial menu events
         */
        $menu
            .mouseleave(mouseleaveMenu)
            .find(options.rowSelector)
                .mouseenter(mouseenterRow)
                .mouseleave(mouseleaveRow)
                .click(clickRow);

        $(document).mousemove(mousemoveDocument);

    };
})(jQuery);
