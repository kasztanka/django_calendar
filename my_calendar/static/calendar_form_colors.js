const colors = document.getElementsByClassName("color-box");

Array.prototype.slice.call(colors).forEach(function(color) {
    color.onclick = function() {
        let old = document.getElementsByClassName("active-color-box")[0];
        old.classList.remove("active-color-box");
        this.classList.add("active-color-box");
        input.value = this.getAttribute("name");
    };
});
