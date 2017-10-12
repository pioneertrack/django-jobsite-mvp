
/**
 * Module for interfacing with the local storage
 */
export default {

  /**
   * Useful for saving JSON in ls
   * @param  {string} key the localstorage key
   * @param  {object} obj the object to save
   * @return {void}
   */
  saveObjectInLocalStorage : function (key, obj) {
    localStorage.setItem(key, JSON.stringify(obj));
  },


  /**
   * Attempts to get something in localstorage throws error if not existent
   * @param  {string} key the key of the object
   * @return {void}
   */
  getObjectInLocalStorage : function (key) {
    var obj =  localStorage.getItem(key);
    if (obj == null) obj = JSON.stringify({});
    return JSON.parse(obj);
  },


  setImageDataString : function (key, dataStr) {
    localStorage.setItem(key, dataStr);
  },

  getImageDataString : function(key) {
    return localStorage.getItem(key);
  },

  unsetImageKey : function (key) {
    localStorage.removeItem(key);
  },

  setString : function (key, str) {
    localStorage.setItem(key, str);
  },

  getStringWithDefault : function (key, defaultStep) {
    var it = localStorage.getItem(key);
    return (it==null) ? defaultStep : it;
  }
}
