$(document).ready(function () {
    try {
        if (document.getElementById("selectAction").value == "")
            document.getElementById("go").setAttribute("disabled", "");
        else {
            document.getElementById("go").removeAttribute("disabled");
        }
    }
    catch(err){}
})

function goto_Action(object) {
    window.location.href = object.options[object.selectedIndex].value;
}

function toggleGO() {
    if(document.getElementById("selectAction").value == "")
            document.getElementById("go").setAttribute("disabled", "");
    else {
        document.getElementById("go").removeAttribute("disabled");
    }
}