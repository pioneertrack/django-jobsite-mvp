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
});