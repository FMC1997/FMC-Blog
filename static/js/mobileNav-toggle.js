const button_toggle = document.querySelector("#nav-toggle");
const navBar = document.querySelector("nav");
navBar.style.display = "none"
button_toggle.addEventListener("click", () => {
    if (navBar.style.display === "none") {
        navBar.style.display = "flex"
        navBar.setAttribute("class", "slide-in-right")
        button_toggle.style.display = "fixed"
    } else {
        navBar.setAttribute("class", "slide-out-right")
        setTimeout(classNone, 500)
        button_toggle.style.display = "absolute"
    }
});

function classNone() {
    navBar.style.display = "none"
}