
require("jquery");
/**
 * Service for saving the contents of a form, as well as filling out a form with existing contents
 */
export default {
  getSerializedForm : function(formSelector) {
    var saveFormItems = {text : {}, checkboxes : []};
    $(formSelector + " input[type='text'], input[type='hidden'], textarea").each(function () {
      if ($( this ).val() != null && $( this ).val()  !== "" && $( this ).attr('name') != null) {
        if ($( this ).attr('name')  === "csrfmiddlewaretoken") return; // skip middleware
        saveFormItems["text"][$( this ).attr('name')] = $( this ).val();
      }
    });

    // Also save all the check boxes
    $(formSelector + " input:checked").each(function() {
      saveFormItems["checkboxes"].push($( this ).attr('name'));
    });

    return saveFormItems;
  },

  setFormFromSerialized : function (serialized, formSelector) {
    if (serialized["text"] == null) return;
    for (var key in serialized["text"]) {
      if (serialized["text"].hasOwnProperty(key)) {
        $(formSelector + " input[name='"+key+"'], textarea[name='"+key+"']").val(serialized["text"][key]);
      }
    }
    console.log(serialized);

    for (var i=0; i<serialized["checkboxes"].length; i++) {
      $(formSelector + " input[type='checkbox'][name='"+ serialized["checkboxes"][i] +"']").prop('checked', true);
    }

  }




}
