document.addEventListener("DOMContentLoaded", () => {
  const audio = document.getElementById("audio");
  const playPauseBtn = document.getElementById("playpause");
  const prevBtn = document.getElementById("prev-track");
  const nextBtn = document.getElementById("next-track");
  const playerArt = document.getElementById("player-art");
  const playerTitle = document.getElementById("player-title");
  const playerArtist = document.getElementById("player-artist");
  const playerContainer = document.getElementById("player-container");
  const progress = document.getElementById("progress");
  const currentTimeEl = document.getElementById("current-time");
  const durationEl = document.getElementById("duration");

  let playlist = Array.from(document.querySelectorAll(".card"));
  let currentIndex = -1;

  function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? "0" + secs : secs}`;
  }

  // === Запуск трека ===
  function playTrack(index) {
    if (index < 0 || index >= playlist.length) return;
    const card = playlist[index];
    const preview = card.dataset.preview;
    if (!preview) return;

    audio.src = preview;
    playerArt.src = card.dataset.artwork;
    playerTitle.textContent = card.dataset.title;
    playerArtist.textContent = card.dataset.artist;

    playerContainer.classList.remove("hidden");
    audio.load(); // Загружаем новый трек

    audio.addEventListener("loadedmetadata", () => {
      progress.max = Math.floor(audio.duration);
      durationEl.textContent = formatTime(audio.duration);
    });

    audio.play().catch(err => console.log("Ошибка при воспроизведении:", err));
    playPauseBtn.textContent = "⏸";
    currentIndex = index;
  }

  // === Навешиваем клики по карточкам ===
  playlist.forEach((card, index) => {
    const playButton = card.querySelector(".play-btn");
    if (playButton && !playButton.classList.contains("disabled")) {
      playButton.addEventListener("click", (e) => {
        e.stopPropagation();
        playTrack(index);
      });
    }
  });

  // === Управление кнопками ===
  playPauseBtn.addEventListener("click", () => {
    if (audio.paused) {
      audio.play();
      playPauseBtn.textContent = "⏸";
    } else {
      audio.pause();
      playPauseBtn.textContent = "▶";
    }
  });

  nextBtn.addEventListener("click", () => {
    if (playlist.length > 0)
      playTrack((currentIndex + 1) % playlist.length);
  });

  prevBtn.addEventListener("click", () => {
    if (playlist.length > 0)
      playTrack((currentIndex - 1 + playlist.length) % playlist.length);
  });

  // === Обновляем прогресс ===
  audio.addEventListener("timeupdate", () => {
    if (!isNaN(audio.duration)) {
      progress.value = Math.floor(audio.currentTime);
      currentTimeEl.textContent = formatTime(audio.currentTime);
    }
  });

  // === Перемотка ===
  progress.addEventListener("input", () => {
    audio.currentTime = progress.value;
  });

  // === Автоматический переход на следующий трек ===
  audio.addEventListener("ended", () => {
    playTrack((currentIndex + 1) % playlist.length);
  });
});
