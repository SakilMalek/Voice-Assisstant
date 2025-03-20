$(document).ready(function () {
  /*** 🟢 Cache frequently used DOM elements ***/
  const $text = $(".text");
  const $siriMessage = $(".siri-message");
  const $micBtn = $("#MicBtn");
  const $oval = $("#Oval");
  const $siriWave = $("#SiriWave");
  const $chatbox = $("#chatbox");
  const $sendBtn = $("#SendBtn");

  /*** 🟢 Initialize text animations using Textillate.js ***/
  function initializeTextAnimations() {
    $text.textillate({
      loop: true,  // Keep looping the animation
      sync: true,  // Synchronize all letters
      in: { effect: "bounceIn" },  // Entrance animation
      out: { effect: "bounceOut" },  // Exit animation
    });

    $siriMessage.textillate({
      loop: true,
      sync: true,
      in: { effect: "fadeInUp", sync: true },  // Fade-in effect
      out: { effect: "fadeOutUp", sync: true },  // Fade-out effect
    });
  }

  /*** 🟢 Initialize SiriWave animation ***/
  function initializeSiriWave() {
    if (!window.siriWave) {  // Prevent duplicate initialization
      window.siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,  // Set width of the wave
        height: 200,  // Set height of the wave
        style: "ios9",  // SiriWave style
        amplitude: 1,  // Wave height intensity
        speed: 0.3,  // Wave speed
        autostart: true,  // Start animation automatically
      });
    }
  }

  /*** 🟢 Handle Mic button click ***/
  function handleMicButtonClick() {
    eel.playAssistantSound();  // Play assistant sound
    $oval.attr("hidden", true);  // Hide oval animation
    $siriWave.attr("hidden", false);  // Show SiriWave animation

    eel
      .allCommands(1)()  // Execute voice command processing
      .then((result) => console.log("Command processed:", result))
      .catch((err) => console.error("Error processing command:", err));
  }

  /*** 🟢 Handle keyboard shortcut (Ctrl + J) ***/
  function handleKeyboardShortcut(e) {
    if (e.key === "j" && e.metaKey) {  // Check if user pressed Ctrl + J
      eel.playAssistantSound();
      $oval.attr("hidden", true);
      $siriWave.attr("hidden", false);
      eel.allCommands()();  // Trigger voice command processing
    }
  }

  /*** 🟢 Play assistant (send message) ***/
  function playAssistant(message) {
    if (message.trim() !== "") {  // Ensure message is not empty
      $oval.attr("hidden", true);
      $siriWave.attr("hidden", false);
      eel.allCommands(message);  // Send message to backend
      $chatbox.val("");  // Clear chatbox input
      toggleButtonsVisibility("");  // Reset button visibility
    }
  }

  /*** 🟢 Toggle Mic and Send buttons visibility ***/
  function toggleButtonsVisibility(message) {
    if (message.length === 0) {
      $micBtn.attr("hidden", false);  // Show Mic button
      $sendBtn.attr("hidden", true);  // Hide Send button
    } else {
      $micBtn.attr("hidden", true);  // Hide Mic button
      $sendBtn.attr("hidden", false);  // Show Send button
    }
  }

  /*** 🟢 Handle Send button click ***/
  function handleSendButtonClick() {
    const message = $chatbox.val();
    playAssistant(message);  // Process the message
  }

  /*** 🟢 Handle Enter key press in chatbox ***/
  function handleChatboxKeyPress(e) {
    if (e.which === 13) {  // Check if Enter key was pressed
      const message = $chatbox.val();
      playAssistant(message);
    }
  }

  /*** 🟢 Initialize event listeners ***/
  function initializeEventListeners() {
    $micBtn.click(handleMicButtonClick);  // Handle Mic button click
    $(document).on("keyup", handleKeyboardShortcut);  // Handle keyboard shortcut (Ctrl + J)
    $chatbox.on("keyup", () => toggleButtonsVisibility($chatbox.val()));  // Toggle buttons on typing
    $sendBtn.click(handleSendButtonClick);  // Handle Send button click
    $chatbox.keypress(handleChatboxKeyPress);  // Handle Enter key press
  }

  /*** 🟢 Main initialization function ***/
  function initialize() {
    initializeTextAnimations();  // Start text animations
    initializeSiriWave();  // Initialize SiriWave
    initializeEventListeners();  // Attach event listeners
  }

  /*** 🟢 Start the application ***/
  initialize();
});
