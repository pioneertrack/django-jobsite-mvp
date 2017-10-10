$(function() {
  if ($('#profileform .set #funding').size() == 0) {

    $('#profileform .set .forminstance').formset({
      prefix: 'experience_set',
      deleteCssClass: 'remove',
      deleteText: '[&mdash;] remove',
      addCssClass: 'add-another',
      addText: '[+] Add work experience',
    });

    $('[id*="currently_working"]').each(function(e) {
      var regexp = /-currently_working/;
      var id = $(this).prop('id').replace(regexp, '');
      if ($(this).prop('checked')) {
        $('#' + id + '-end_date').hide();
      }
    });

    $(document).on('change', '[id*="currently_working"]', function(e) {
      var regexp = /-currently_working/;
      var id = $(this).prop('id').replace(regexp, '');
      if ($(this).prop('checked')) {
        $('#' + id + '-end_date').hide();
        $('#' + id + '-end_date').val(null);
      } else {
        var dt = new Date();
        $('#' + id + '-end_date').show();
        $('#' + id + '-end_date').val(new Intl.DateTimeFormat('en-US',  {month: '2-digit', day: '2-digit', year: '2-digit'}).format(dt));
      }
    });

  }

  $('[name="positions"]').change(function(e) {
    if ($(this).val() == '5') {
      $('[name="positions"]:checked').each(function() {
        if ($(this).val() !== '5') {
          $(this).prop('checked', false)
        }
      })
    } else {
      $('[name="positions"][value="5"]').prop('checked', false)
    }
  })

  $('#profileform .set #funding').formset({
    prefix: 'funding_set',
    deleteCssClass: 'remove',
    deleteText: '[&mdash;] remove',
    addCssClass: 'add-another',
    addText: '[+] Add funding round',
    formCssClass: 'dynamic-form1',
  });

  $('#profileform .set #jobs').formset({
    prefix: 'job_set',
    deleteCssClass: 'remove',
    deleteText: '[&mdash;] remove',
    addCssClass: 'add-another',
    addText: '[+] Add job opening',
    formCssClass: 'dynamic-form2',
  });

  function replaceValidationUI( form ) {
    // Suppress the default bubbles
    form.addEventListener( "invalid", function( event ) {
        event.preventDefault();
    }, true );

    // Support Safari, iOS Safari, and the Android browser—each of which do not prevent
    // form submissions by default
    form.addEventListener( "submit", function( event ) {
        if ( !this.checkValidity() ) {
            event.preventDefault();
        }
    });

    var submitButton = form.querySelector( "input[type=submit]" );
    submitButton.addEventListener( "click", function( event ) {
        var invalidFields = form.querySelectorAll( ":invalid" ),
            errorMessages = form.querySelectorAll( ".error-message" ),
            parent;

        // Remove any existing messages
        for ( var i = 0; i < errorMessages.length; i++ ) {
            errorMessages[ i ].parentNode.removeChild( errorMessages[ i ] );
        }

        for ( var i = 0; i < invalidFields.length; i++ ) {
            parent = invalidFields[ i ].parentNode;
            parent.insertAdjacentHTML( "afterbegin", "<div class='error-message'>" +
                invalidFields[ i ].validationMessage +
                "</div>" );
        }
        if ($('[name=positions]:checked').size() == 0) {
          $('[name=positions]').parent().parent().prepend("<div class='error-message'>This field is requred</div>")
        }

        // If there are errors, give focus to the first invalid field
        if ( invalidFields.length > 0 ) {
            invalidFields[ 0 ].focus();
        }
    });
  }

  // Replace the validation UI for all forms
  var forms = document.querySelectorAll( "form" );
  for ( var i = 0; i < forms.length; i++ ) {
      replaceValidationUI( forms[ i ] );
  }
});