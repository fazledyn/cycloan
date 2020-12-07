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