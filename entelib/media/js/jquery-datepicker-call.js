function showKal(f) {
    /*
      http://stackoverflow.com/questions/1646590/jquery-datepicker-default-date
    */
    // var myDate = new Date($("#dd").attr('value'));
    component = $('.datepicker')
    // component = f
    component.datepicker({
        numberOfMonths: 2,
        showButtonPanel: true,
        changeMonth: true,
        changeYear: true,
        showOtherMonths: true,
        selectOtherMonths: true,
        showWeek: true,
        firstDay: 1,
        // defaultDate: myDate,
        dateFormat: 'yy-mm-dd'
    });
}
