module.exports.selectors = {
  "PROFILE_BREADCRUMBS_PROPIC_WRAPPER" : ".profile-image-wrapper",
  "PROFILE_BREADCRUMBS_PROPIC_CANCEL" : ".profile-image-cancel",
  "PROFILE_BREADCRUMBS_PROPIC_UPBUTTON": ".profile-image-button-wrapper",
  "PROFILE_BREADCRUMBS_PROPIC_INPUT": "#propic-upload-input",
  "DELETE_ICON" : ".delete-icon",
  "PROFILE_BREADCRUMBS_MENU" : ".profile-breadcrumbs-menu",
  "PROFILE_BREADCRUMBS_ENABLED_MENU_ITEM" : "li:not(.disabled)",
  "PROFILE_RELOAD_PAGE_INDICATOR" : ".reloading-page-wrapper",
  "FORM_WRAPPER" : ".form-wrapper",

  "PM_DROPDOWN" : ".dropdown-module .primaryroles",
  "FINISH_PROFILE_BUTTON" : ".finish-profile-button",
  "REQUIRED_IMAGE_FLAG" : ".requiredImageFlag",
  "ADD_STARTUP_BUTTON" : ".add-startup-then-finish",
  "STARTUP_PROFILE_FORM_VAL" : ".startupProfileInput",
  "LOADING_IMAGE" : ".preloader",
  "POSITION_CHECK_SELECTOR" : "input[name='positions_check[]']"
}

module.exports.routes = {
  "PROFILE_STEP_UPDATE_ROUTE" : "/profile_breadcrumbs/",
  "PROFILE_STEP_IMAGE_UPLOAD" : "/profile/step/image"
}

var bearfoundersRandomString = "sadfjlksdfasdfklsadf";

module.exports.localStorageKeys = {
  "PROFILE_FORM_DATA" : bearfoundersRandomString + "profileFormData",
  "PROFILE_IMAGE_DATA" : bearfoundersRandomString + "profileImage",
  "CURRENT_STEP" : bearfoundersRandomString + "currentStep",


}
