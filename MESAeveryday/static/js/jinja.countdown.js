$('#clock').countdown($('span#clock').attr('data-date-string'), function(event) {
    $(this).html(event.strftime('%D days %H:%M:%S'));
});