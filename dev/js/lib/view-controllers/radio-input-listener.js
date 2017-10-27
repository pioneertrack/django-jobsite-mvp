/**
* @author Jack Considine <jackconsidine3@gmail.com>
* @package
* 2017-09-29
*/
/**
 * A view-controller for listening to a change in radiobuttons
 * @param  {string} radiobuttonName the 'name' in the input tag
 * @return
 */
export default function (radiobuttonName) {
  var jqSelector = "input[name='"+radiobuttonName+"']";
  var jqSelectedSelector = "input[name='"+radiobuttonName+"']:checked";
  var callbacks = [];

  /**
   * add hook for when input changes
   * @param  {Function} newCb the function , that takes argument new val, that will be triggered on a input change
   * @param  {boolean} invokeNow if this hook should be run right now
   * @return {void}
   */
  this.addOnChangedFunction = function (newCb, invokeNow) {
    callbacks.push(newCb);
    if (invokeNow) newCb($(jqSelectedSelector).val());
  }


  $(jqSelector).on("change", function () {
      // Get the value of the radio button
      var newVal = $(jqSelectedSelector).val();
      setTimeout(function() {
        for (var i=0; i<callbacks.length; i++) {
          callbacks[i].apply(null, [newVal]);
        }
      }, 5);
  });
}
