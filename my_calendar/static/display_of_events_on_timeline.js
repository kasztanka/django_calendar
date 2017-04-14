$(".calendar-checkbox").change(function() {
    const eventsClass = this.id;
    let events = $('.' + eventsClass);
    if(this.checked) {
        events.show("scale", duration = "slow");
    } else {
        events.hide("scale", duration = "slow");
    }
});
