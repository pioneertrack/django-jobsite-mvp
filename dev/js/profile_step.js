var settings = require('./config');

require("jquery");
require("imports-loader?jQuery=jquery,$=jquery,this=>window!./jquery.nice-select.js");
require("smartwizard/dist/js/jquery.smartWizard.js");

var DDService = require("bootstrap-dropdown-selector");

var ddPrimaryService = new DDService({'rootModuleSelector' : '.primaryroles', 'inputTargetName' : "primaryroles"});
var ddMajors = new DDService({'inputTargetName' : 'major', 'rootModuleSelector' : '.primarymajorMod'});
var ddHours = new DDService({'inputTargetName' : 'numberhoursinput', 'rootModuleSelector' : '.hoursavailableMod'});
var ddStartup = new DDService({'inputTargetName' : 'hasstartup', 'rootModuleSelector' : '.hasstartupToRegister'});
var ddCalAffil = new DDService({'inputTargetName' : 'calaffiliation', 'rootModuleSelector' : '.calaffiliation'});
// Now set dropdowns
var allDropdowns = [ddPrimaryService, ddMajors, ddHours, ddStartup];
ddPrimaryService.listenForDropDown();
ddMajors.listenForDropDown();
ddHours.listenForDropDown();
ddStartup.listenForDropDown();
ddCalAffil.listenForDropDown();

import ComponentStateChanger from './lib/view-controllers/component-state-changer.js';

var cu = new ComponentStateChanger();
var profileImageView = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER);
var cancelButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_CANCEL);
var uploadButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_UPBUTTON);



function validateFields (stepId, goToStep) {
  $(stepId + " .required").each(function() {
    if ($(this).val() == null || $(this).val() === "") {

      $(this).closest(".form-group").find("p").css("color", "red");
      if (goToStep) {
        // console.log($(this).closest('.step-section').attr("id") + " is this step");
      }
    }
  });
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
    // else {
    //     $(this).closest(".form-group").find("label").css('color', "black");
    //     $(settings.selectors.POSITION_CHECK_SELECTOR).each(function() {
    //
    //     });
    // }
  })
}



$(document).ready(function(){


  $('select.select-input').niceSelect();
  $('select.select-input').bind('change', function(e) {
      $(this).prev().text($(this).children('option[value="' + $(this).val() + '"]').text())
  });

  $(settings.selectors.LOADING_IMAGE).css("display", "none");
  var form_data = window.localStorage.getItem(settings.localStorageKeys.PROFILE_FORM_DATA) ?
    JSON.parse(window.localStorage.getItem(settings.localStorageKeys.PROFILE_FORM_DATA)) : null
  if (form_data !== null) {
    $(form_data).each(function (key, item) {
        if (item.name == 'csrfmiddlewaretoken') {
          return;
        }
        var input = $('input[name="' + item.name + '"][value="' + item.value + '"]');
        if (input.length > 0 ) {
          switch (input.prop('type')) {
            case 'text':
            case 'select':
              input.val(item.value); break;
            case 'checkbox':
              input.prop('checked', true)
          }
        } else if ($('textarea[name="' + item.name + '"]').length > 0 ) {
          $('textarea[name="' + item.name + '"]').text(item.value)
        }
      }
    )
  }

  // Jump to first anchor

  notLookingCheckBoxes();
  /* Since the forms have been updated, reset the dropdown labels */
  ddPrimaryService.resetDropDowns();
  ddMajors.resetDropDowns();
  ddHours.resetDropDowns();
  ddStartup.resetDropDowns();
  ddCalAffil.resetDropDowns();



  validateFields(".missing-data", true);
  $('#smartwizard').smartWizard();
  $("#smartwizard").on("leaveStep", function(e, anchorObject, stepNumber, stepDirection) {
      var form_data = JSON.stringify($('#profile_form').serializeArray())

      window.localStorage.setItem(settings.localStorageKeys.PROFILE_FORM_DATA, form_data);

      if (stepDirection === "forward") {
          if (! allinputsFilled("#step-" + (stepNumber + 1) + " " + ".required")) {
            validateFields("#step-" + (stepNumber+1));
            return false;
          }

       }
       var nextStep;
       if (stepDirection === "forward") nextStep = stepNumber + 1;
       else nextStep = stepNumber - 1;
       window.localStorage.setItem(settings.localStorageKeys.CURRENT_STEP, "step-" + (nextStep + 1))
       return true;
    });
});


//utility func, see if any empty inputs
function allinputsFilled (selector) {
  var allFilled = true;

  $(selector).each (function(index) {
    if ($(this).attr("type") == "checkbox" && ! $("input[name='" + $(this).attr("name") + "']:checked").val())
    {
        $("input[name='" + $(this).attr("name") + "']").closest(".form-group").find("label").css("color", "red");
        allFilled = false;
    }
    if ($(this).val() == null || $(this).val() === "") {
      allFilled = false;
    }
  });
  return allFilled;
}


$( document ).ready(function () {
  // console.log();
  $(settings.selectors.FINISH_PROFILE_BUTTON).click(function() {
    if (! allinputsFilled(".required")) {
      validateFields(".missing-data", true);
      event.preventDefault();
    }
  });
})

// IMAGE UPLOAD


// Profile image watcher
import ImageUploader from './lib/view-controllers/image-instant-upload';
var iu = new ImageUploader(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_INPUT, false);


iu.addHook(iu.ON_IMAGE_ADDED,  function (f) {
  var fd = new FormData();
  fd.append("profileimage", f[0]);

  $.ajax ({
    type: 'POST',
     data: fd,
     url : settings.routes.PROFILE_STEP_IMAGE_UPLOAD,
     async: true,
     processData : false,
     contentType: false,
          cache: false,
     success: function (data) {

      }
    });
});

iu.addHook(iu.ON_IMAGE_LOADED,  function (str) {
  // set image

  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER + " img.image-holder").attr("src", str);
  window.localStorage.setItem(settings.localStorageKeys.PROFILE_IMAGE_DATA, str);
  cu.setState(profileImageView);



// Save image
  // var formData = new FormData($("form"));

  // Save image to server

});

var savedImageStr = window.localStorage.getItem(settings.localStorageKeys.PROFILE_IMAGE_DATA);
if (savedImageStr != null) {
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER + " img.image-holder").attr("src", savedImageStr);
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_INPUT).removeClass("required");
  cu.setState(profileImageView);

}

/* driver code */
$(settings.selectors.DELETE_ICON).click(function () {
  iu.deleteFiles();
  window.localStorage.removeItem(settings.localStorageKeys.PROFILE_IMAGE_DATA);
  cu.setState(uploadButton);
});

// On add  startup
$(settings.selectors.ADD_STARTUP_BUTTON).click(function() {
  $(settings.selectors.STARTUP_PROFILE_FORM_VAL).val("yes");
  $("form").submit();
})
