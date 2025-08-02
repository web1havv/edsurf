const statusDiv = document.getElementById('status');
const previewDiv = document.getElementById('preview');
const scriptPreview = document.getElementById('script-preview');
const mediaDownloads = document.getElementById('media-downloads');
const generateBtn = document.getElementById('generateBtn');

function setStatus(text, type="processing") {
    statusDiv.textContent = text;
    statusDiv.className = "status " + type;
}

generateBtn.onclick = async () => {
    setStatus("Extracting article...");
    chrome.runtime.sendMessage({action: "fetch_content"}, async (content) => {
        if (!content || !content.content) {
            setStatus("Failed to extract content.", "error");
            return;
        }
        setStatus("Sending to backend...");
        // Send to backend
        const resp = await fetch("http://localhost:8000/generate-reel", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                text: content.content,
                title: content.title
            })
        });
        if (!resp.ok) {
            setStatus("Backend error: " + (await resp.text()), "error");
            return;
        }
        setStatus("Processing...", "processing");
        const data = await resp.json();
        setStatus("Complete!", "complete");
        previewDiv.style.display = "block";
        scriptPreview.textContent = data.script;
        // Show images
        mediaDownloads.innerHTML = "";
        data.images.forEach((img, i) => {
            const imgEl = document.createElement("img");
            imgEl.src = "data:image/png;base64," + img;
            imgEl.style.width = "100%";
            mediaDownloads.appendChild(imgEl);
        });
        // Audio download
        if (data.audio_url) {
            const a = document.createElement("a");
            a.href = "http://localhost:8000" + data.audio_url;
            a.textContent = "Download Audio";
            a.className = "download-btn";
            a.download = "reel_audio.wav";
            mediaDownloads.appendChild(a);
        }
        // Video download
        if (data.video_url) {
            const a = document.createElement("a");
            a.href = "http://localhost:8000" + data.video_url;
            a.textContent = "Download Video";
            a.className = "download-btn";
            a.download = "reel_video.mp4";
            mediaDownloads.appendChild(a);
        }
    });
}; 