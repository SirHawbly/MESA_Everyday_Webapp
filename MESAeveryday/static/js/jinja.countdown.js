$('#clock1').countdown($('span#clock1').attr('data-date-string-one'), function(event) {
    $(this).html(event.strftime('%D days %H:%M:%S'));
});

$('#clock2').countdown($('span#clock2').attr('data-date-string-two'), function(event) {
    $(this).html(event.strftime('%D days %H:%M:%S'));
});

$('#clock3').countdown($('span#clock3').attr('data-date-string-three'), function(event) {
    $(this).html(event.strftime('%D days %H:%M:%S'));
});
