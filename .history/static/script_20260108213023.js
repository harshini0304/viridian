let session_id = null;
let mediaRecorder;
let audioChunks = [];

async function startSession() {
    let res = await fetch("/start_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "Harshini" })
    });

    let data = await res.json();
    session_id = data.session_id;
}

async function sendText() {
    if (!session_id) await startSession();

    let input = document.getElementById("userInput");
    let text = input.value;

    let res = await fetch("/send_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: session_id, text: text })
    });

    let data = await res.json();

    let chat = document.getElementById("chatbox");
    chat.innerHTML += `<div><b>You:</b> ${text}</div>`;
    chat.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;

    input.value = "";
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = e => {
                audioChunks.push(e.data);
            };
        });
}

function stopRecording() {
    mediaRecorder.stop();
}

function endSession() {
    fetch("/end_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: session_id })
    })
    .then(res => res.json())
    .then(data => {
        alert("Session Summary: " + JSON.stringify(data));
    });
}

window.onload = startSession;
