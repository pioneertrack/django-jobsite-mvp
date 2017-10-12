/**
* @author Jack Considine <jackconsidine3@gmail.com>
* @package
* 2017-09-28
*/


//TODO change from constructor args to options
require ("jquery");
/**
 * State changer VC. Manages view states ie when one view is visible the other's are all
 * invisible
 * @return {[type]} [description]
 */
export default function () {
  /**
   * List of views (jquery selectors) that should be modified to be invisible on state change
   * @type {Array}
   */
  var currentViews = [];

  /**
   * [addState description]
   * @type {[type]}
   */
  var currentlyVisibleView;

  /**
   * adds a state to the state pager which will be initialized to visible
   * @param  {string} stateSelector jquery selector for this new state
   * @param  {string} visibilityType what class to add to make this visible
   * @param  {Function} cbOnChange callback function for when this state is added
   * @return {int} the index that this view is in the current views attribute
   */
  this.addState = function (stateSelector, visibilityType, cbOnChange) {
    visibilityType = visibilityType || "block";
    $(stateSelector).css("display", visibilityType);
    if (!cbOnChange) {
      cbOnChange = function () {}; // do nothing
    }
    cbOnChange();

    hideCurrent();
    currentlyVisibleView = stateSelector;
    var stateData = {selector : stateSelector, visibilityType : visibilityType, cbFunc : cbOnChange};
    currentViews.push(stateData);
    return currentViews.length - 1;
  }

  /**
   * helper function for hiding the current set view
   * @return {void}
   */
  function hideCurrent () {
    if (currentlyVisibleView != null) $(currentlyVisibleView).css("display", "none");
  }

  /**
   * modifies the state that is visible by indexing the currentViews attribute and setting that view to
   * visible
   * @param  {[type]} viewSelectorIndex [description]
   * @return {[type]}                   [description]
   */
  this.setState = function (viewSelectorIndex) {
    hideCurrent();
    if (currentViews.length > viewSelectorIndex && viewSelectorIndex >= 0 && currentViews[viewSelectorIndex] != null) {
      currentlyVisibleView = currentViews[viewSelectorIndex].selector;
      $(currentlyVisibleView).css("display", currentViews[viewSelectorIndex].visibilityType);
      currentViews[viewSelectorIndex].cbFunc();
    }
  }

}
