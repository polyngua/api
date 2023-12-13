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

            recorder.addEventListener("stop", async () => {
                let tracks = stream.getTracks();
                tracks.forEach(track => track.stop())

                const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});

                // Create a FormData object to hold the audio file
                let formData = new FormData();
                formData.append('recording', audioBlob);

                console.log("now sending request");

                let messageID;
                let messageContent;
                let messageAudio;

                // Use fetch to send the audio file to your server
                await fetch(`http://localhost:8000/conversations/${conversationId}/messages/audio`, {
                    method: 'POST',
                    body: formData
                })
                .then(async response => {
                    response = await response.json();

                    console.log("response from server after post to audio:");
                    console.log(response)

                    messageID = response.id;
                    messageContent = response.content;
                    })
                .catch((error) => {
                    console.error('Error:', error);
                    // Handle error - notify the user
                });

                console.log("Message ID: " + messageID);
                console.log("Message content: " + messageContent);

                await fetch(`http://localhost:8000/conversations/${conversationId}/messages/${messageID}/audio`, {
                    method: 'GET'
                })
                .then(async response => {
                    messageAudio = await response.blob();
                })
                    .catch(error => {
                        console.log("There was a problem receiving the file.")
                    })

                // Create a URL for the blob
                const audioUrl = URL.createObjectURL(messageAudio);

                // Create an audio element and set its source to the blob URL
                const audio = new Audio(audioUrl);

                // Play the audio
                audio.play();
            });

            recorder.start(200);
        }, );
}

// Function to stop recording
async function stopRecording() {
    if (recorder && recorder.state !== 'inactive') {
        recorder.stop();
    }
}