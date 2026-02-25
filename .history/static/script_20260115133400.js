let sessionId = null;
let recognition = null;
let listeningMsg = null;
let isSending = false;

// ---------------- SESSION ----------------
async function startSession() {
    try {
        const res = await fetch("/start_session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: "guest" })
        });

        const data = await res.json();
        sessionId = data.session_id;
        console.log("Session started:", sessionId);
    } catch (err) {
        console.error("Session start failed", err);
        addMessage("⚠️ Could not start session", "bot");
    }
}

// ---------------- TEXT ----------------
async function sendText() {
    if (!sessionId || isSending) return;

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
        addMessage("❌ Speech recognition not supported in this browser", "bot");
        return;
    }

    if (recognition) recognition.stop();

    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    listeningMsg = addMessage("🎤 Listening… speak now", "bot", true);

    recognition.onresult = async (event) => {
        recognition.stop();

        const transcript = event.results[0][0].transcript.trim();
        if (listeningMsg) listeningMsg.remove();

        if (!transcript) {
            addMessage("⚠️ I didn’t catch that", "bot");
            return;
        }

        addMessage(transcript, "user");
        await sendToBot(transcript);
    };

    recognition.onerror = () => {
        recognition.stop();
        if (listeningMsg) listeningMsg.remove();
        addMessage("⚠️ Could not understand audio", "bot");
    };

    recognition.start();
}

function stopRecording() {
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
    if (listeningMsg) {
        listeningMsg.remove();
        listeningMsg = null;
    }
}

// ---------------- BOT PIPELINE ----------------
async function sendToBot(text) {
    if (!sessionId || isSending) return;
    isSending = true;

    const typing = addMessage("Viridian is typing…", "bot", true);

    try {
        const res = await fetch("/send_text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                text: text
            })
        });

        if (!res.ok) throw new Error("Server error");

        const data = await res.json();
        typing.remove();

        if (data.reply) {
            addMessage(data.reply, "bot");
        } else {
            addMessage("⚠️ No reply from server", "bot");
        }
    } catch (err) {
        typing.remove();
        console.error(err);
        addMessage("⚠️ Something went wrong. Please try again.", "bot");
    } finally {
        isSending = false;
    }
}

// ---------------- SUMMARY ----------------
async function endSession() {
    if (!sessionId) return;

    const msg = addMessage("🧠 Generating therapist summary…", "bot", true);

    try {
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
            addMessage("⚠️ Summary not available yet", "bot");
        }
    } catch {
        msg.remove();
        addMessage("⚠️ Failed to generate summary", "bot");
    }
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
