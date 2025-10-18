let playlist = [];
let currentIndex = 0;
let audio = null;
let isShuffle = false;
let isRepeat = false;

function playTrack(previewUrl, name, artist, coverUrl, index = 0) {
  const playerBar = document.getElementById('player-bar');
  const info = document.getElementById('player-info');
  const cover = document.getElementById('player-cover');
  const audioEl = document.getElementById('player-audio');

  playlist = Array.from(document.querySelectorAll('.track-button')).map(btn => ({
    previewUrl: btn.dataset.url,
    name: btn.dataset.name,
    artist: btn.dataset.artist,
    cover: btn.dataset.cover
  }));

  currentIndex = index;

  cover.src = coverUrl;
  info.innerHTML = `<strong>${name}</strong><br><span>${artist}</span>`;
  audioEl.src = previewUrl;
  playerBar.classList.add('active');

  audio = audioEl;
  audio.play();
}

function playPause() {
  if (audio.paused) audio.play();
  else audio.pause();
}

function nextTrack() {
  currentIndex = isShuffle ? Math.floor(Math.random() * playlist.length)
                           : (currentIndex + 1) % playlist.length;
  const track = playlist[currentIndex];
  playTrack(track.previewUrl, track.name, track.artist, track.cover, currentIndex);
}

function prevTrack() {
  currentIndex = isShuffle ? Math.floor(Math.random() * playlist.length)
                           : (currentIndex - 1 + playlist.length) % playlist.length;
  const track = playlist[currentIndex];
  playTrack(track.previewUrl, track.name, track.artist, track.cover, currentIndex);
}

function toggleShuffle() {
  isShuffle = !isShuffle;
  document.getElementById('shuffle-btn').classList.toggle('active', isShuffle);
}

function toggleRepeat() {
  isRepeat = !isRepeat;
  document.getElementById('repeat-btn').classList.toggle('active', isRepeat);
}

document.addEventListener('DOMContentLoaded', () => {
  const audioEl = document.getElementById('player-audio');
  audioEl.addEventListener('ended', () => {
    if (isRepeat) audioEl.play();
    else nextTrack();
  });
});
