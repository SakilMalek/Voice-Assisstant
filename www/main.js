$(document).ready(function () {
    $('.text').textillate({
        loop: true,
        sync: true,
        in: { effect: "bounceIn" },
        out: { effect: "bounceOut" }
    });

    // Check if SiriWave already exists before creating it
    if (!siriWave) {
       var siriWave = new SiriWave({
            container: document.getElementById("siri-container"),
            width: 800,
            height: 200,
            style: "ios9",
            amplitude: 1,
            speed: 0.30,
            autostart: true
        });
    }

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: { effect: "fadeInUp", sync: true },
        out: { effect: "fadeOutUp", sync: true }
    });

    // Mic button click event
    $("#MicBtn").click(function () { 
        eel.playAssistantSound();
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        
        // Updated Eel function call with promise handling
        eel.allCommands(1)().then(function(result) {
            console.log("Command processed:", result);
        }).catch(function(err) {
            console.error("Error processing command:", err);
        });
    });
});