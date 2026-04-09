// Tab switching
function showTab(name) {
    document.getElementById('upload-tab').classList.toggle('hidden', name !== 'upload');
    document.getElementById('live-tab').classList.toggle('hidden', name !== 'live');
    document.querySelectorAll('.tab').forEach((t, i) =>
        t.classList.toggle('active', (i === 0) === (name === 'upload')));
}

// File input
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const detectBtn = document.getElementById('detect-btn');
let selectedFile = null;

fileInput.addEventListener('change', e => setFile(e.target.files[0]));
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('over'));
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('over');
    setFile(e.dataTransfer.files[0]);
});

function setFile(file) {
    if (!file) return;
    selectedFile = file;
    document.getElementById('file-name').textContent = file.name;
    detectBtn.disabled = false;
}

// Run detection
async function runDetection() {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('video', selectedFile);

    document.getElementById('progress').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    detectBtn.disabled = true;

    try {
        const res = await fetch('/detect', { method: 'POST', body: formData });
        const data = await res.json();
        document.getElementById('progress').classList.add('hidden');

        if (data.error) {
            showResults(`<span style="color:#ef4444">Error: ${data.error}</span>`);
        } else {
            showResults(`
        <strong>Done!</strong><br>
        Frames processed: ${data.frames}<br>
        Total detections: ${data.total_detections}<br>
        <a href="${data.download_url}" download>Download annotated video</a>
      `);
        }
    } catch (err) {
        document.getElementById('progress').classList.add('hidden');
        showResults(`<span style="color:#ef4444">Network error: ${err.message}</span>`);
    }
    detectBtn.disabled = false;
}

function showResults(html) {
    const el = document.getElementById('results');
    el.innerHTML = html;
    el.classList.remove('hidden');
}

// Live stream
let streaming = false;
function toggleStream() {
    const img = document.getElementById('stream-img');
    const btn = event.target;
    if (!streaming) {
        img.src = '/stream';
        btn.textContent = 'Stop Stream';
        streaming = true;
    } else {
        img.src = '';
        btn.textContent = 'Start Stream';
        streaming = false;
    }
}