let sessionId = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

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

// ---------------- TEXT CHAT ----------------
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
    if (data.reply) addMessage(data.reply, "bot");
}

// ---------------- VOICE RECORDING ----------------
async function startRecording() {
    if (isRecording) return;

    addMessage("🎤 Listening… you can speak now.", "bot");

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    isRecording = true;

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
        addMessage("🔴 Processing your voice…", "bot");

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", audioBlob);
        formData.append("session_id", sessionId);

        const res = await fetch("/upload_audio", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.transcript) {
            addMessage(data.transcript, "user");
            addMessage(data.reply, "bot");
        }
    };

    mediaRecorder.start();
}

function stopRecording() {
    if (!mediaRecorder || !isRecording) return;
    isRecording = false;
    mediaRecorder.stop();
}

// ---------------- SESSION SUMMARY ----------------
async function endSession() {
    addMessage("🧠 Generating therapist summary…", "bot");

    const res = await fetch("/end_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId })
    });

    const data = await res.json();
    addMessage(`📊 Session Summary:\n${data.summary}`, "bot");
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
