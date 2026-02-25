let sessionId = null;

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
        console.error("Session start failed:", err);
    }
}

// ---------------- TEXT ----------------
async function sendText() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();

    if (!text || !sessionId) return;

    addMessage(text, "user");
    input.value = "";

    // typing indicator
    const typingId = addMessage("Viridian is typing...", "bot typing");

    try {
        const res = await fetch("/send_text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                text: text
            })
        });

        const data = await res.json();

        removeMessage(typingId);

        if (data.reply) {
            addMessage(data.reply, "bot");
        } else {
            addMessage("⚠️ No reply from server", "bot");
        }
    } catch (err) {
        removeMessage(typingId);
        addMessage("⚠️ Server error", "bot");
        console.error(err);
    }
}

// ---------------- UI ----------------
function addMessage(text, sender) {
    const chat = document.getElementById("chatbox");
    const msg = document.createElement("div");
    msg.className = sender;
    msg.innerText = text;

    const id = Date.now();
    msg.dataset.id = id;

    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
    return id;
}

function removeMessage(id) {
    const chat = document.getElementById("chatbox");
    const el = chat.querySelector(`[data-id="${id}"]`);
    if (el) el.remove();
}

// ---------------- VOICE (STUBS FOR NOW) ----------------
function startRecording() {
    addMessage("🎤 Voice recording started (not implemented yet)", "bot");
}

function stopRecording() {
    addMessage("🛑 Voice recording stopped (not implemented yet)", "bot");
}

// ---------------- SESSION SUMMARY ----------------
async function endSession() {
    addMessage("🧠 Therapist summary will be generated here (coming soon)", "bot");
}


// ---------------- INIT ----------------
window.onload = startSession;
