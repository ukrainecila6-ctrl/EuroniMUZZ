// --- Общий плеер ---
function setupPlayer(trackListId, playerId, playPauseId, prevId, nextId, progressId, currentTimeId, durationId) {
    const trackList = document.getElementById(trackListId);
    const player = document.getElementById(playerId);
    const playPauseBtn = document.getElementById(playPauseId);
    const prevBtn = document.getElementById(prevId);
    const nextBtn = document.getElementById(nextId);
    const progress = document.getElementById(progressId);
    const currentTimeEl = document.getElementById(currentTimeId);
    const durationEl = document.getElementById(durationId);

    if (!trackList) return;

    let tracks = Array.from(trackList.children);
    let currentIndex = 0;
    let audio = new Audio();
    let isPlaying = false;

    function playTrack() {
        audio.src = tracks[currentIndex].dataset.src;
        audio.play();
        isPlaying = true;
        playPauseBtn.textContent = '⏸️';
        player.classList.remove('hidden'); // показываем плеер при воспроизведении
    }

    tracks.forEach((li, i) => {
        li.addEventListener('click', () => {
            currentIndex = i;
            playTrack();
        });
    });

    if (playPauseBtn) playPauseBtn.addEventListener('click', () => {
        if (isPlaying) { audio.pause(); playPauseBtn.textContent = '▶️'; }
        else { audio.play(); playPauseBtn.textContent = '⏸️'; }
        isPlaying = !isPlaying;
    });

    if (prevBtn) prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + tracks.length) % tracks.length;
        playTrack();
    });

    if (nextBtn) nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % tracks.length;
        playTrack();
    });

    audio.addEventListener('timeupdate', () => {
        if (!audio.duration) return;
        const percent = (audio.currentTime / audio.duration) * 100;
        if (progress) progress.value = percent;
        if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);
        if (durationEl) durationEl.textContent = formatTime(audio.duration);
    });

    if (progress) progress.addEventListener('input', () => {
        audio.currentTime = (progress.value / 100) * audio.duration;
    });
}

// --- Вспомогательная функция ---
function formatTime(sec){
    if(isNaN(sec)) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s<10?'0':''}${s}`;
}

// --- Инициализация плееров ---
setupPlayer('trackList','player','playPause','prev','next','progress','currentTime','duration');
setupPlayer('recTrackList','recPlayer','recPlayPause','recPrev','recNext','recProgress','recCurrentTime','recDuration');
