const DOG_COOLDOWN_MS = 10 * 1000;

let camera_on = false;
let last_dog = 0;
let total = 0;
let pi = 0;
let controller;

function toggleCamera() {
    const btn = document.getElementById('camera-btn');
    const iframe = document.getElementById('camera-feed');
    iframe.src = camera_on ? '' : 'http://192.168.10.5:9000/mjpg';
    btn.style.backgroundImage = camera_on ? "url('imgs/camera-icon.png')" : "url('imgs/camera-icon-closed.png')";
    btn.title = camera_on ? "Turn Camera On" : "Turn Camera Off";
    if (!camera_on) { startStream(); } else { stopStream(); }

    camera_on = !camera_on;
}

function startStream() {
    controller = new AbortController();
    const signal = controller.signal;

    fetch('http://localhost:8080/detections', {
        method: 'POST',
        signal: signal
    })
    .then(response => {
        const score = document.getElementById('score-div');
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log("Stream ended.");
                    return;
                }
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const jsonString = line.slice(6);
                        try {
                            if (jsonString === 'dog' || jsonString == 'cat') {
                                const now = Date.now();
                                if (now - last_dog > DOG_COOLDOWN_MS) {
                                    last_dog = now;

                                    showDogModal().then((confirmed) => {
                                        if (confirmed == 'nad') {
                                            nad();
                                        } else {
                                            total++;
                                            if (confirmed) {
                                                console.log("Pi beat Dog.");
                                                pi++;
                                            } else {
                                                console.log("Dog beat Pi.");
                                            }

                                            score.innerHTML = (((pi*100)/total).toFixed(2)).toString() + "%";
                                        }
                                    });
                                } else {
                                    console.log("Dog detected but in cooldown.");
                                }
                            }
                        } catch (err) {
                            console.error("Failed to parse JSON:", err);
                        }
                    }
                });

                read();
            });
        }

        read();
    })
    .catch(err => {
        if (err.name === 'AbortError') {
            console.log("Stream aborted.");
        } else {
            console.error("Stream error:", err);
        }
    });
}

function stopStream() {
    if (controller) {
        console.log('Stopping Stream')
        controller.abort();
        controller = null;
    }
}

function showDogModal() {
    return new Promise((resolve) => {
        const modal = document.getElementById('dog-modal');
        const yesBtn = document.getElementById('yes-button');
        const noBtn = document.getElementById('no-button');
        const nadBtn = document.getElementById('nad-button');

        modal.style.display = 'flex';

        const cleanup = () => {
            modal.style.display = 'none'; 
            yesBtn.removeEventListener('click', onYes);
            noBtn.removeEventListener('click', onNo);
            nadBtn.removeEventListener('click', onNad);
        };

        const onYes = () => {
            cleanup();
            resolve(true);
        };

        const onNo = () => {
            cleanup();
            resolve(false);
        };

        const onNad = () => {
            cleanup();
            resolve('nad');
        };

        yesBtn.addEventListener('click', onYes);
        noBtn.addEventListener('click', onNo);
        nadBtn.addEventListener('click', onNad);
    });
}

function mad() {
    const fn = document.getElementById('fn');
    let curFN = fn.innerHTML.slice(5);
    let newFN = parseInt(curFN) + 1
    fn.innerHTML = "FN - " + newFN.toString();
}

function nad() {
    const fp = document.getElementById('fp');
    let curFP = fp.innerHTML.slice(5);
    let newFP = parseInt(curFP) + 1
    fp.innerHTML = "FP - " + newFP.toString();
}
