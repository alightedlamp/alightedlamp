$(document).ready(function() {

    $(".delete-post").click(function() {
        console.log("Made it here");
        $("#confirm-modal").css("display", "block");
    });

    $(".btn-close").click(function() {
        $("#confirm-modal").css("display", "none");
    });

    window.onclick = function(event) {
        if (event.target == $("#confirm-modal")) {
            $("#confirm-modal").css("display", "none");
        }
    }

});