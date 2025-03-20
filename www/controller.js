$(document).ready(function () {

    /*** 🟢 Message Display Handlers ***/
    // Expose function to display messages via Eel
    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
        $(".siri-message li:first").text(message);  // Set message text
        $('.siri-message').textillate('start');  // Start text animation effect
    }

    /*** 🟢 Chat Message Display (Sender & Receiver) ***/
    function appendMessage(type, message) {
        var chatBox = document.getElementById("chat-canvas-body");

        if (message.trim() !== "") {  // Ensure message is not empty
            chatBox.innerHTML += `
                <div class="row justify-content-${type === "sender" ? "end" : "start"} mb-4">
                    <div class="width-size">
                        <div class="${type}_message">${message}</div>
                    </div>
                </div>`;
            
            chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll to the latest message
        }
    }

    // Expose sender and receiver message functions to Eel
    eel.expose(senderText);
    function senderText(message) { appendMessage("sender", message); }

    eel.expose(receiverText);
    function receiverText(message) { appendMessage("receiver", message); }

    /*** 🟢 UI Visibility Handlers ***/
    // Function to toggle UI visibility between elements
    function toggleVisibility(hideSelector, showSelector) {
        $(hideSelector).attr("hidden", true);
        $(showSelector).attr("hidden", false);
    }

    // Expose functions to Eel for UI changes
    eel.expose(ShowHood);
    function ShowHood() { toggleVisibility("#SiriWave", "#Oval"); }

    eel.expose(hideLoader);
    function hideLoader() { toggleVisibility("#Loader", "#FaceAuth"); }

    eel.expose(hideFaceAuth);
    function hideFaceAuth() { toggleVisibility("#FaceAuth", "#FaceAuthSuccess"); }

    eel.expose(hideFaceAuthSuccess);
    function hideFaceAuthSuccess() { toggleVisibility("#FaceAuthSuccess", "#HelloGreet"); }

    /*** 🟢 Start Page Handler ***/
    eel.expose(hideStart);
    function hideStart() {
        $("#Start").attr("hidden", true);  // Hide Start screen
        setTimeout(() => {
            $("#Oval").addClass("animate__animated animate__zoomIn").attr("hidden", false);  // Animate and show Oval
        }, 1000);
    }

});
