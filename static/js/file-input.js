const fileInput = document.querySelector("input#file-form");

fileInput.onchange = () => {
    const selectFile = fileInput.files[0];
    console.log(selectFile)

    const User_pick = document.querySelector(".logo-pick img");
    console.log("UserPick: " + User_pick)
    User_pick.setAttribute('src',
        URL.createObjectURL(selectFile))

}