$(".calendar-checkbox").change(function() {
    const eventsClass = this.id;
    console.log(eventsClass);
    let events;
    if(this.checked) {
        events = document.getElementsByClassName(eventsClass);
        console.log(events);
        for (let i = 0; i < events.length; i++) {
            events[i].style.display = 'block';
        }
    } else {
        events = document.getElementsByClassName(eventsClass);
        for (let i = 0; i < events.length; i++) {
            events[i].style.display = 'none';
        }
    }
});
