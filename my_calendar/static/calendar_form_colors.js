const colors = document.getElementsByClassName("colors");

Array.prototype.slice.call(colors).forEach(function(color) {
    color.onclick = function() {
        let old = document.getElementsByClassName("active")[0];
        old.className = "colors";
        this.className += " active";
        input.value = this.getAttribute("name");
    };
});
