let sessionId = null;
let recognition = null;
let listeningMsg = null;

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

// ---------------- TEXT ----------------
async function sendText() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    if (!text) return;

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

    listeningMsg = addMessage("🎤 Listening… speak now", "bot", true);

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        listeningMsg.remove();
        addMessage(transcript, "user");
        await sendToBot(transcript);
    };

    recognition.onerror = () => {
        listeningMsg.remove();
        addMessage("⚠️ Could not understand audio", "bot");
    };

    recognition.start();
}

function stopRecording() {
    if (recognition) recognition.stop();
}

// ---------------- BOT PIPELINE ----------------
async function sendToBot(text) {
    const typing = addMessage("Viridian is typing…", "bot", true);

    const res = await fetch("/send_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, text })
    });

    const data = await res.json();
    typing.remove();
    addMessage(data.reply, "bot");
}

// ---------------- SUMMARY ----------------
async function endSession() {
    const msg = addMessage("🧠 Generating therapist summary…", "bot", true);

    const res = await fetch("/end_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId })
    });

    const data = await res.json();
    msg.remove();
    addMessage(data.summary, "bot");
}

// ---------------- UI ----------------
function addMessage(text, sender, temp = false) {
    const chat = document.getElementById("chatbox");
    const div = document.createElement("div");
    div.className = sender;
    div.innerText = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return temp ? div : null;
}

window.onload = startSession;
