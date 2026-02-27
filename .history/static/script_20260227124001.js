let sessionId = null;
let recognition = null;

// ---------------- SESSION ----------------
async function startSession() {
    const res = await fetch("/start_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "guest" })
    });

    const data = await res.json();
    sessionId = data.session_id;
}

// ---------------- TEXT SEND ----------------
async function sendText() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();

    if (!text || !sessionId) return;

    addMessage(text, "user");
    input.value = "";

    await sendToBot(text);
}

// ---------------- VOICE ----------------
function startRecording() {

    if (!("webkitSpeechRecognition" in window)) {
        addMessage("❌ Speech recognition not supported", "bot");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    const listeningMsg = addMessage("🎤 Listening… speak now", "system");

    recognition.onresult = (event) => {

        const transcript = event.results[0][0].transcript;

        listeningMsg.remove();  // 🔥 remove listening message

        addMessage(transcript, "user");
        sendToBot(transcript);
    };

    recognition.onerror = () => {
        listeningMsg.remove();
        addMessage("⚠️ Voice recognition failed", "bot");
    };

    recognition.onend = () => {
        listeningMsg.remove();
    };

    recognition.start();
}

function stopRecording() {
    if (recognition) recognition.stop();
}

// ---------------- BOT CALL ----------------
async function sendToBot(text) {

    const typing = addMessage("Viridian is typing…", "bot");

    const res = await fetch("/send_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: sessionId,
            text: text
        })
    });

    const data = await res.json();

    typing.remove();

    if (data.reply) {
        addMessage(data.reply, "bot");
    }
}

// ---------------- SUMMARY ----------------
async function endSession() {

    const msg = addMessage("🧠 Generating therapist summary…", "bot");

    const res = await fetch("/end_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId })
    });

    const data = await res.json();

    msg.remove();

    if (data.summary) {
        addMessage(data.summary, "bot");
    } else {
        addMessage("⚠️ Failed to generate summary", "bot");
    }
}

// ---------------- UI ----------------
function addMessage(text, sender) {
    const chat = document.getElementById("chatbox");
    const div = document.createElement("div");
    div.className = sender;

    div.style.whiteSpace = "pre-line"; // ← important for summary formatting
    div.innerText = text;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

window.onload = startSession;