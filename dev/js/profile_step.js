var settings = require('./config');

require("jquery");
require("smartwizard/dist/js/jquery.smartWizard.js");


var DDService = require("bootstrap-dropdown-selector");

var ddPrimaryService = new DDService({'rootModuleSelector' : '.primaryroles', 'inputTargetName' : "primaryroles"});
var ddMajors = new DDService({'inputTargetName' : 'major', 'rootModuleSelector' : '.primarymajorMod'});
var ddHours = new DDService({'inputTargetName' : 'numhours', 'rootModuleSelector' : '.hoursavailableMod'});
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
import UrlLocationService from './services/urlLocationService.js';
import LocalStorageService from './services/localStorageCacheService.js';
import FormSavingService from './services/formSavingService.js';

var cu = new ComponentStateChanger();
var profileImageView = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER);
var cancelButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_CANCEL);
var uploadButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_UPBUTTON);







$(document).ready(function(){


  // Jump to first anchor
  FormSavingService.setFormFromSerialized(LocalStorageService.getObjectInLocalStorage(settings.localStorageKeys.PROFILE_FORM_DATA), "form");

  /* Since the forms have been updated, reset the dropdown labels */
  ddPrimaryService.resetDropDowns();
  ddMajors.resetDropDowns();
  ddHours.resetDropDowns();
  ddStartup.resetDropDowns();
  ddCalAffil.resetDropDowns();



  UrlLocationService.jumptToAnchor(LocalStorageService.getStringWithDefault(settings.localStorageKeys.CURRENT_STEP, "step-1"));
  $('#smartwizard').smartWizard({"useURLhash" : true});
  $("#smartwizard").on("leaveStep", function(e, anchorObject, stepNumber, stepDirection) {
      //todo remove
      LocalStorageService.saveObjectInLocalStorage(settings.localStorageKeys.PROFILE_FORM_DATA, FormSavingService.getSerializedForm("form"));
      if (stepDirection === "forward") {
          if (! allinputsFilled("#step-" + (stepNumber + 1) + " " + ".required")) {
            alert("please fill out all fields!");
            return false;
          }

       }
       var nextStep;
       if (stepDirection === "forward") nextStep = stepNumber + 1;
       else nextStep = stepNumber - 1;
       LocalStorageService.setString(settings.localStorageKeys.CURRENT_STEP, "step-" + (nextStep + 1))
       return true;
    });
});


//utility func, see if any empty inputs
function allinputsFilled (selector) {
  var allFilled = true;
  $(selector).each (function(index) {

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
      alert ("Please make sure you've completed all requirements on every step");
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
  console.log(f[0]);
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
  LocalStorageService.setImageDataString(settings.localStorageKeys.PROFILE_IMAGE_DATA, str);
  cu.setState(profileImageView);



// Save image
  // var formData = new FormData($("form"));

  // Save image to server

});

var savedImageStr = LocalStorageService.getImageDataString(settings.localStorageKeys.PROFILE_IMAGE_DATA);
if (savedImageStr != null) {
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER + " img.image-holder").attr("src", savedImageStr);
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_INPUT).removeClass("required");
  cu.setState(profileImageView);

}



/* driver code */
$(settings.selectors.DELETE_ICON).click(function () {
  iu.deleteFiles();
  LocalStorageService.unsetImageKey(settings.localStorageKeys.PROFILE_IMAGE_DATA);
  cu.setState(uploadButton);
});



// On add  startup
$(settings.selectors.ADD_STARTUP_BUTTON).click(function() {
  $(settings.selectors.STARTUP_PROFILE_FORM_VAL).val("yes");
  $("form").submit();
})
