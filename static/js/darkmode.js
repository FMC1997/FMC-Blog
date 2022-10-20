//For iframes
const iframes = document.getElementsByTagName('iframe');

let darkMode = localStorage.getItem('darkMode')
const darkModeToggle = document.querySelector('#darkMode-toggle')

const enableDarkMode = () => {
    document.body.classList.add("darkMode");
    for (let number = 0; number < iframes.length; number++) {
        iframes[number].contentDocument.body.classList.add("darkMode");
        console.log(number)
    }

    localStorage.setItem('darkMode', 'enabled');
}

const disableDarkMode = () => {
    document.body.classList.remove("darkMode");
    for (let number = 0; number < iframes.length; number++) {
        iframes[number].contentDocument.body.classList.remove("darkMode");
    }
    localStorage.setItem('darkMode', null);
}

if (darkMode === 'enabled') {
    enableDarkMode()
}

darkModeToggle.addEventListener('click', () => {
    let darkMode = localStorage.getItem('darkMode')
    if (darkMode !== 'enabled') {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
})
