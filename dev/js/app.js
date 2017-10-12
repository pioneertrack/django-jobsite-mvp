var settings = require('./config');
import ImageUploader from './lib/view-controllers/image-instant-upload';
import ComponentStateChanger from './lib/view-controllers/component-state-changer.js';
var iu = new ImageUploader(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_INPUT, null);


var cu = new ComponentStateChanger();
var loadingState = new ComponentStateChanger();

var loadingIndicator = loadingState.addState(settings.selectors.PROFILE_RELOAD_PAGE_INDICATOR);
loadingState.addState(settings.selectors.FORM_WRAPPER);



var profileImageView = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER);
var cancelButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_CANCEL);
var uploadButton = cu.addState(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_UPBUTTON);

var DDService = require("bootstrap-dropdown-selector");

var ddPrimaryService = new DDService();
var ddMajors = new DDService();
var ddHours = new DDService();


ddPrimaryService.listenForDropDown({'rootModuleSelector' : '.primaryroles', 'inputTargetName' : "primaryroles"});
ddMajors.listenForDropDown({'inputTargetName' : 'major', 'rootModuleSelector' : '.primarymajorMod'});
ddMajors.listenForDropDown({'inputTargetName' : 'numhours', 'rootModuleSelector' : '.hoursavailableMod'});
// ddHours.listenForDropDown({'inputTargetName' : 'numhours'});

iu.addHook(iu.ON_IMAGE_ADDED,  function () {

});

iu.addHook(iu.ON_IMAGE_LOADED,  function (str) {
  // set image
  $(settings.selectors.PROFILE_BREADCRUMBS_PROPIC_WRAPPER + " img.image-holder").attr("src", str);
  cu.setState(profileImageView);
});


/* driver code */
$(settings.selectors.DELETE_ICON).click(function () {
  cu.setState(uploadButton);
  iu.deleteFiles();
});



// Listen for click on
$(settings.selectors.PROFILE_BREADCRUMBS_MENU + " " + settings.selectors.PROFILE_BREADCRUMBS_ENABLED_MENU_ITEM).click(function() {
  loadingState.setState(loadingIndicator);
  $.get(settings.routes.PROFILE_STEP_UPDATE_ROUTE + ($( this ).index() + 1), function(resp) {
    // Reload page
    if (resp.success != true) return;

    var loc = window.location;
    window.location = loc.protocol + '//' + loc.host + loc.pathname + loc.search;

  });
})
