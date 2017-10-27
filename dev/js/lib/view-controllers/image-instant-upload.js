/**
* @author Jack Considine <jackconsidine3@gmail.com>
* @package
* 2017-09-28
*/

require("jquery");


export default function (inputHandle, requiredInputSelector) {
  var self = this;
  // initialize listener

  $(inputHandle).on("change", function () {
    // upload file


    var files = $(inputHandle)[0].files;
      callHooks(self.ON_IMAGE_ADDED, [files]);
    if (files.length === 0) return;
    setRequiredInput(true); //mark that the picture is loaded for the validator
    var reader = new FileReader();
    reader.addEventListener("load", function () {

      onFileLoadedToBase64(reader.result);
    }, false);

    reader.readAsDataURL(files[0]);
  });


  /**
   * Function triggered
   * @param  {[type]} base64String [description]
   * @return {[type]}              [description]
   */
  function onFileLoadedToBase64 (base64String) {
    callHooks(self.ON_IMAGE_LOADED, [base64String]);
  }
  /**
   * Invokes any hooks that have been set for the point in the lifecycle
   * @param  {string} key the hooks to invoke
   * @return {}     [description]
   */
  function callHooks (key, args) {
    if (hooks[key] == null) return;
    args = args || [];
    for (var i=0; i<hooks[key].length; i++) {
      console.log(JSON.stringify(hooks[key][i]));
      hooks[key][i].apply(null, args);
    }
   }

  /**
   * On file added
   * @type {String}
   */
  this.ON_IMAGE_ADDED = "onImageAdded";
  /**
   * After image sent to server
   * @type {String}
   */
  this.ON_IMAGE_LOADED = "onImageLoaded";
  /**
   * On server response from the message
   * @type {String}
   */
  this.ON_IMAGE_RESPONSE = "onServerResponse";
  /**
   * functions that are called at different points in the imageuploader lifecycle
   * @type {Object}
   */
  var hooks = {};



  /**
   * Adds a hook that will be called at hkey time in the lifecycle
   * @param  {string} hkey the key corresponding to the point in the lifecycle. Should be a constant static variable
   * @param  {Array} hargs array of arguments to call with this function
   * @param  {Function} hfunction function to be run
   * @return {void}
   */
  this.addHook = function (hkey, hfunction) {
    if (hooks[hkey] == null) hooks[hkey] = []; // init
    hooks[hkey].push(hfunction);

  }

  /**
   * Deletes the currently uploaded file
   * @return {void}
   */
  this.deleteFiles = function () {
    $(inputHandle).val( "" );
    setRequiredInput(false);
    // remove form input

  }


  /**
  * Toggles the value of the input that represents whether or not the profile is set (for form validation, to trigger a required error if )
  * @param {boolean} pictureSet true if picture is being set
  */
  function setRequiredInput (pictureSet) {
    if (requiredInputSelector == null) return;
    $(requiredInputSelector).val( (pictureSet) ? "set" : "" );

  }
}
