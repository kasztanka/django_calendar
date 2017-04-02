const all_day = document.getElementById("id_all_day")
const start_hour = document.getElementById("id_start_hour")
const end_hour = document.getElementById("id_end_hour")
const timezone = document.getElementById("id_timezone")
const elements = [start_hour, end_hour, timezone]
if (all_day.checked) {
    for (var i = 0; i < elements.length; i++) {
            elements[i].disabled = true;
        }
}
all_day.onclick = function() {
    if (all_day.checked) {
        for (var i = 0; i < elements.length; i++) {
            elements[i].disabled = true;
        }
    }
    else {
        for (var i = 0; i < elements.length; i++) {
            elements[i].disabled = false;
        }
    }
}
function enableInputs() {
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = false;
    }
}
