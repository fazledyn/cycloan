function checkPhotoSelected() {
    if (document.getElementById("photo").value == "") {
        alert("No photo selected. You must select a photo.");
        document.querySelector("#photo").value = "";
        return false;
    }
    return true;
}


function checkDocumentSelected() {
    if (document.getElementById("document").value == "") {
        alert("No document uploaded. You must upload your document.");
        document.querySelector("#document").value = "";
        return false;
    }
    return true;
}

function checkDate() {
    var date_first = new Date(document.getElementById('start_datetime').value);
    var date_last = new Date(document.getElementById('end_datetime').value);
    var current = new Date();

    if ( (date_first < current) || (date_last < current) ) {
        alert("Start or End Date can't be from past.");
        document.getElementById('start_datetime').value = "";
        return false;
    }

    if (date_first > date_last) {
        alert("End date can't be before Start Date.")
        document.getElementById('start_datetime').value = "";
        document.getElementById('end_datetime').value = "";
        return false;
    }
    return true;
}

function checkPasswordLength() {
    var password = document.getElementById('password').value
    var password2 = document.getElementById('password_confirm').value

    if ( (password.length < 8) || (password2.length < 8) ) {
        alert("Password length must be 8 characters or long.");
        document.getElementById('password').value = ""
        document.getElementById('password_confirm').value = ""
        return false;
    }
    return true;
}