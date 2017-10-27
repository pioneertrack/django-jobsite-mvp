var settings = require('./config');

require("jquery");
require("imports-loader?jQuery=jquery,$=jquery,this=>window!./jquery.nice-select.js");
require("jquery-mousewheel")($);
require('malihu-custom-scrollbar-plugin')($);
require("smartwizard/dist/js/jquery.smartWizard.js");

import ComponentStateChanger from './lib/view-controllers/component-state-changer.js';

var cu = new ComponentStateChanger();
var profileImageView = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER);
var cancelButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_CANCEL);
var uploadButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_UPBUTTON);



function validateFields (stepId, goToStep) {
  $(stepId + " input.required, " + stepId + " textarea.required, " + stepId + " select.required").each(function() {
    if ($(this).val() == null || $(this).val() === "") {
      $(this).closest(".form-group").find("p").css("color", "red");
    } else {
      $(this).closest(".form-group").find("p").removeAttr('style');
    }
  });
  $('input[type="checkbox"].required').each( function () {
    var input = $('input[name="' + $(this).attr("name") + '"][type="checkbox"]:first');
    if ($('input[name="' + $(this).attr("name") + '"][type="checkbox"]:checked').length === 0) {
      input.closest(".form-group").find("p").css("color", "red");
    } else {
      input.closest(".form-group").find("p").removeAttr('style');
    }
  })
}

//utility func, see if any empty inputs
function allinputsFilled (selector) {
  var allFilled = true;

  $(selector).each (function(index) {
    if ($(this).attr("type") == "checkbox" && ! $("input[name='" + $(this).attr("name") + "']:checked").val()) {
        allFilled = false;
    }
    if ($(this).val() === null || $(this).val() === "") {
      allFilled = false;
    }
  });
  return allFilled;
}

function notLookingCheckBoxes () {

  function isThisNotLooking ($this) {
    return ("notlooking" === $this.parent().text().replace(/\s+/g,' ').trim().replace(" ", "").toLowerCase());
  }

  function removeChecks ($this) {
    var foundIt = false;
    if (isThisNotLooking($this)) {
      foundIt = true
      $this.closest(".form-group").find("label").css('color', "gray");
      $(settings.selectors.POSITION_CHECK_SELECTOR).prop("checked", false);
      $this.prop("checked", true);
      $(settings.selectors.POSITION_CHECK_SELECTOR).checked = true;
      $this.parent().css("color", "black");
    }
    return foundIt;
  }

  $(settings.selectors.POSITION_CHECK_SELECTOR +  ":checked").each(function() {
    removeChecks($(this));
  });


  $(settings.selectors.POSITION_CHECK_SELECTOR).on("click", function() {
    if (!removeChecks($(this))) {
    $(this).closest(".form-group").find("label").css('color', "black");
      $( settings.selectors.POSITION_CHECK_SELECTOR ).each(function() {

        if (isThisNotLooking($(this))) {
            $(this).prop("checked", false);
        }
      });
    }
  })
}



$(document).ready(function(){

  $(settings.selectors.LOADING_IMAGE).css("display", "none");
  var form_data = localStorage.getItem(settings.localStorageKeys.PROFILE_FORM_DATA) ?
    JSON.parse(localStorage.getItem(settings.localStorageKeys.PROFILE_FORM_DATA)) : null

  if (form_data !== null) {
    $(form_data).each(function (key, item) {
        if (item.name == 'csrfmiddlewaretoken') {
          return;
        }
        var input = $('input[name="' + item.name + '"][value="' + item.value + '"]');
        if (input.length > 0 ) {
          switch (input.prop('type')) {
            case 'text':
              input.val(item.value); break;
            case 'checkbox':
              input.prop('checked', true);
          }
        } else if ($('textarea[name="' + item.name + '"]').length > 0 ) {
          $('textarea[name="' + item.name + '"]').text(item.value);
        } else if ($('select[name="' + item.name + '"]').length > 0 ) {
          $('select[name="' + item.name + '"]').val(item.value);
        }
      }
    )
  }

  $('select.select-input').niceSelect();
  $(".nice-select ul.list").mCustomScrollbar({
        theme: "3d-thick-dark",
        scrollInertia: 100,
  });

  notLookingCheckBoxes();

  var current_step = localStorage.getItem(settings.localStorageKeys.CURRENT_STEP) ?
    localStorage.getItem(settings.localStorageKeys.CURRENT_STEP) : '0';
  current_step = parseInt(current_step.match(/\d+/));

  $('#smartwizard').smartWizard({
    showStepURLhash: false,
    selected: current_step,
  });

  $("#smartwizard").on("leaveStep", function(e, anchorObject, stepNumber, stepDirection) {
      history.pushState({}, null, window.location.href.split('#')[0]);
      var form_data = JSON.stringify($('#profile_form').serializeArray())
      localStorage.setItem(settings.localStorageKeys.PROFILE_FORM_DATA, form_data);

      validateFields("#step-" + stepNumber);
      if (stepDirection === "forward") {
        var stepId = "#step-" + stepNumber;
        var selector = stepId + " input.required, " + stepId + " textarea.required, " + stepId + " select.required";
        if (allinputsFilled(selector) === false) {
            return false;
          }
       }
       var nextStep;
       if (stepDirection === "forward") nextStep = stepNumber + 1;
       else nextStep = stepNumber - 1;
       localStorage.setItem(settings.localStorageKeys.CURRENT_STEP, "step-" + nextStep)
       return true;
    });

  $(settings.selectors.ADD_STARTUP_BUTTON).click(function () {
    var selector = 'input.required, textarea.required, select.required'
    if (!allinputsFilled(selector)) {
      validateFields('.missing-data', true)
      event.preventDefault()
    }
    if ($('[name="image"]').val().length > 0) {
      $('[name="image"]').val('')
    }
    $('[name="image_decoded"]').
      val(localStorage.getItem(settings.localStorageKeys.PROFILE_IMAGE_DATA))
    $(settings.selectors.STARTUP_PROFILE_FORM_VAL).val('yes')
    $('#profile_form').submit()
  });

  $(settings.selectors.FINISH_PROFILE_BUTTON).click(function () {
    var selector = 'input.required, textarea.required, select.required'
    if (!allinputsFilled(selector)) {
      validateFields('.missing-data', true)
      event.preventDefault()
    }
    if ($('[name="image"]').val().length > 0) {
      $('[name="image"]').val('')
    }
    $('[name="image_decoded"]').
      val(localStorage.getItem(settings.localStorageKeys.PROFILE_IMAGE_DATA))
    $('#profile_form').submit()
  });

  // $('textarea.required, input.required').on('change', function() {
  //   if ($(this).val() !== null || $(this).val().length > 0) {
  //     $(this).closest(".form-group").find("p").removeAttr('style');
  //   }
  //   // $('input[type="checkbox"].required').each( function () {
  //   //   var input = $('input[name="' + $(this).attr("name") + '"][type="checkbox"]:first');
  //   //   if ($('input[name="' + $(this).attr("name") + '"][type="checkbox"]:checked').length === 0) {
  //   //     input.closest(".form-group").find("p").css("color", "red");
  //   //   } else {
  //   //     input.closest(".form-group").find("p").removeAttr('style');
  //   //   }
  //   // })
  //
  // })
});

// IMAGE UPLOAD

// Profile image watcher
import ImageUploader from './lib/view-controllers/image-instant-upload';
var iu = new ImageUploader(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_INPUT, false);

iu.addHook(iu.ON_IMAGE_LOADED,  function (str) {
  // set image
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER + " img.image-holder").attr("src", str);
  localStorage.setItem(settings.localStorageKeys.PROFILE_IMAGE_DATA, str);
  cu.setState(profileImageView);
});

var savedImageStr = localStorage.getItem(settings.localStorageKeys.PROFILE_IMAGE_DATA);
if (savedImageStr != null) {
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER + " img.image-holder").attr("src", savedImageStr);
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_INPUT).removeClass("required");
  cu.setState(profileImageView);
}

/* driver code */
$(settings.selectors.DELETE_ICON).click(function () {
  iu.deleteFiles();
  localStorage.removeItem(settings.localStorageKeys.PROFILE_IMAGE_DATA);
  cu.setState(uploadButton);
  $('input[name="image"]').addClass('required');
});
