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
// ---------------- VOICE ----------------
function startRecording() {

    if (!("webkitSpeechRecognition" in window)) {
        addMessage("❌ Speech recognition not supported", "bot");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;

    let finalTranscript = "";

    addMessage("🎤 Listening… speak now", "bot");

    recognition.onresult = (event) => {

        let interimTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            let transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        // ONLY send when speech is FINAL
        if (finalTranscript.length > 0) {
            addMessage(finalTranscript, "user");
            sendToBot(finalTranscript);
            finalTranscript = "";
        }
    };

    recognition.onerror = () => {
        addMessage("⚠️ Voice recognition failed", "bot");
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