function displayOfEvents(calendar, color) {
    let square, events;
    square = document.getElementById(calendar);
    if (square.style.backgroundColor !== 'transparent') {
        square.style.backgroundColor = 'transparent';
        events = document.getElementsByClassName(calendar);
        for (var i = 0; i < events.length; i++) {
            events[i].style.display = 'none';
        }
    }
    else {
        square.style.backgroundColor = color;
        events = document.getElementsByClassName(calendar);
        for (var i = 0; i < events.length; i++) {
            events[i].style.display = 'block';
        }
    }
};
