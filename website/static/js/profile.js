$(function() {
  if ($('#profileform .set #funding').size() == 0) {

    $('#profileform .set .forminstance').formset({
      prefix: 'experience_set',
      deleteCssClass: 'remove',
      deleteText: '[&mdash;] remove',
      addCssClass: 'add-another',
      addText: '[+] Add work experience',
    });

    // $('[id*="currently_working"]').each(function(e) {
    //   var regexp = /-currently_working/;
    //   var id = $(this).prop('id').replace(regexp, '');
    //   if ($(this).prop('checked')) {
    //     $('#' + id + '-end_date').hide();
    //   }
    // });

    // $(document).on('change', '[id*="currently_working"]', function(e) {
    //   var regexp = /-currently_working/;
    //   var id = $(this).prop('id').replace(regexp, '');
    //   if ($(this).prop('checked')) {
    //     $('#' + id + '-end_date').hide();
    //     $('#' + id + '-end_date').val('');
    //   } else {
    //     var dt = new Date();
    //     $('#' + id + '-end_date').show();
    //     $('#' + id + '-end_date').val(new Intl.DateTimeFormat('en-US').format(dt));
    //   }
    // });

  }

  $('#profileform .set #funding').formset({
    prefx: 'founder_set1',
    deleteCssClass: 'remove',
    deleteText: '[&mdash;] remove',
    addCssClass: 'add-another',
    addText: '[+] Add funding round',
    formCssClass: 'dynamic-form1',
  });

  $('#profileform .set #jobs').formset({
    prefix: 'founder_set2',
    deleteCssClass: 'remove',
    deleteText: '[&mdash;] remove',
    addCssClass: 'add-another',
    addText: '[+] Add job opening',
    formCssClass: 'dynamic-form2',
  });
});