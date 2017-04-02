forms.forEach(function(form_id) {
    let form = document.getElementById(form_id);
    if (form != null) form.style.display = 'none';
});

function formDisplay(form_id, button_id, text) {
    form = document.getElementById(form_id);
    button = document.getElementById(button_id);
    if (form.style.display !== 'none') {
        form.style.display = 'none';
        button.innerHTML = text;
    }
    else {
        form.style.display = 'block';
        button.innerHTML = "Hide edition";
    }
};
