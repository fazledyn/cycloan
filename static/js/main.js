function checkOwnerSubmission() {

    if (document.getElementById('photo').value == "") {
        alert("You must select a photo")
        return false;
    }
    else if (document.getElementById('password').value.length < 8) {
        alert("Password must be 8 characters long")
        return false;
    }
    else if (document.getElementById('password_confirm').value != document.getElementById('password').value) {
        alert("Passwords do not match")
        return false;    
    }
    else if (document.getElementById('lat').value == "") {
        alert("You must select location on map.")
        return false;
    }
    return true;
}

function checkCustomerSubmission() {
    if (document.getElementById('photo').value == "") {
        alert("You must select a photo")
        return false;
    }
    else if (document.getElementById('password').value.length < 8) {
        alert("Password must be 8 characters long")
        return false;
    }
    else if (document.getElementById('password_confirm').value != document.getElementById('password').value) {
        alert("Passwords do not match")
        return false;    
    }
    else if (document.getElementById('document').value == "") {
        alert("No document selected. You must select a document")
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
};

function checkMapLocation() {
    if (document.getElementById('lat').value == "") {
        alert("Select your location on map")
        return false;
    }
    return true;
}