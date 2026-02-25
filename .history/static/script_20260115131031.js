let sessionId = null;
let mediaRecorder;
let audioChunks = [];

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
async function sendText() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    if (!text || !sessionId) return;

    addMessage(text, "user");
    input.value = "";

    const res = await fetch("/send_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, text })
    });

    const data = await res.json();

    if (data.reply) {
        addMessage(data.reply, "bot");
    }
}

// ---------------- VOICE ----------------
async function startRecording() {
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    addMessage("🎙 Listening...", "system");

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
}

async function stopRecording() {
    if (!mediaRecorder) return;

    mediaRecorder.stop();

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", audioBlob);
        formData.append("session_id", sessionId);

        const res = await fetch("/upload_audio", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.text) {
            addMessage(data.text, "user");
        }
        if (data.reply) {
            addMessage(data.reply, "bot");
        }
    };
}

// ---------------- UI ----------------
function addMessage(text, sender) {
    if (!text) return;

    const chat = document.getElementById("chatbox");
    const msg = document.createElement("div");
    msg.className = sender;
    msg.innerText = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

window.onload = startSession;
