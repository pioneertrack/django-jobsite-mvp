$(function() {
  if ($('#profileform .set #funding').size() == 0) {
    $('#profileform .set .forminstance').formset({
      prefix: 'experience_set',
      deleteCssClass: 'remove',
      deleteText: '[&mdash;] remove',
      addCssClass: 'add-another',
      addText: '[+] Add work experience',
    });
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