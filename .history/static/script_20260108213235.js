let sessionId = null;

// ---------------- SESSION ----------------
async function startSession() {
    const res = await fetch("/start_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "guest" })
    });

    const data = await res.json();
    sessionId = data.session_id;
    console.log("Session started:", sessionId);
}

// ---------------- TEXT ----------------
async function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();

    if (!text || !sessionId) return;

    addMessage(text, "user");
    input.value = "";

    const res = await fetch("/send_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: sessionId,
            text: text
        })
    });

    const data = await res.json();

    if (data.reply) {
        addMessage(data.reply, "bot");
    } else {
        addMessage("⚠️ No reply from server", "bot");
    }
}

// ---------------- UI ----------------
function addMessage(text, sender) {
    const chat = document.getElementById("chatbox");
    const msg = document.createElement("div");
    msg.className = sender;
    msg.innerText = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

window.onload = startSession;
