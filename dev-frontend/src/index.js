import { pipeline } from '@xenova/transformers';

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('nameModal').style.display = 'flex';
    document.getElementById("startConversation").addEventListener("click", startConversation);
    document.getElementById("sendMessage").addEventListener("click", sendMessage);
    document.getElementById("startRecording").addEventListener("click", startRecording);
    document.getElementById("stopRecording").addEventListener("click", stopRecording)
})

document.getElementById('nameModal').style.display = 'flex';

let conversationId;
let transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-tiny.en');

async function startConversation() {
    let userName = document.getElementById('userName').value;
    let response = await fetch('http://localhost:8000/conversations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: userName
        })
    });

    let data = await response.json();

    conversationId = data.id;

    alert(conversationId);

    document.getElementById('nameModal').style.display = 'none';
}

async function sendMessage() {
    let messageBox = document.getElementById('messageInput');
    let message = messageBox.value;
    messageBox.value = '';

    // Display user message
    displayMessage(message, 'user');

    // Send message to API
    let response = await fetch(`http://localhost:8000/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            content: message
        })
    });
    let data = await response.json();

    // Display assistant's reply
    displayMessage(data.reply, 'assistant');
}

function displayMessage(message, role) {
    let messagesDiv = document.getElementById('messages');
    let messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);
    messageDiv.textContent = message;
    messagesDiv.appendChild(messageDiv);
}

var recorder;

function startRecording() {
    navigator.mediaDevices.getUserMedia({audio: true})
        .then(stream => {
            recorder = new MediaRecorder(stream);

            let audioChunks = [];

            recorder.addEventListener("dataavailable", async event => {
                audioChunks.push(event.data);

                let audio = new Blob(audioChunks, {type: 'audio/wav'})
                let url = URL.createObjectURL(audio);

                let text = await transcriber(url, {return_timestamps: true});
                document.getElementById('transcription').innerText = text.text;
                console.log(text)
            });

            recorder.addEventListener("stop", () => {
                let tracks = stream.getTracks();
                tracks.forEach(track => track.stop())

                const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
                let url = URL.createObjectURL(audioBlob);

                let downloadLink = document.createElement('a');
                downloadLink.href = url;
                downloadLink.download = "recording.wav";
                downloadLink.text = "download";
                downloadLink.innerText = "download";

                document.getElementById("download").appendChild(downloadLink);
            });

            recorder.start(200);
        });
}

// Function to stop recording
async function stopRecording() {
    if (recorder && recorder.state !== 'inactive') {
        recorder.stop();
    }

    // console.log(output);
}