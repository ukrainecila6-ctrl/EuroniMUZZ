// Player v2: delegated play buttons, playlist from parent list, progress, shuffle, repeat
(() => {
  const playerBar = document.getElementById('player-bar');
  const coverEl = document.getElementById('player-cover');
  const titleEl = document.getElementById('player-title');
  const artistEl = document.getElementById('player-artist');
  const btnPlay = document.getElementById('btn-play');
  const btnNext = document.getElementById('btn-next');
  const btnPrev = document.getElementById('btn-prev');
  const btnRepeat = document.getElementById('btn-repeat');
  const btnShuffle = document.getElementById('btn-shuffle');
  const progressBg = document.getElementById('player-progress-bg');
  const progressBar = document.getElementById('player-progress');
  const timeEl = document.getElementById('player-time');
  const audio = document.getElementById('player-audio');

  let playlist = [];
  let index = 0;
  let repeat = false;
  let shuffle = false;

  function showPlayer() { playerBar.classList.remove('hidden'); }
  function hidePlayer() { playerBar.classList.add('hidden'); }

  document.addEventListener('click', function(e){
    const btn = e.target.closest('.play-btn');
    if (!btn) return;
    const trackItem = btn.closest('.track-item');
    if (!trackItem) return;
    const url = trackItem.dataset.preview;
    if (!url) { alert('Превью недоступно'); return; }
    const name = trackItem.dataset.title || '';
    const artist = trackItem.dataset.artist || '';
    const cover = trackItem.dataset.cover || '';
    const parent = trackItem.parentElement;
    const items = Array.from(parent.querySelectorAll('.track-item'));
    playlist = items.map(it => ({ url: it.dataset.preview, name: it.dataset.title, artist: it.dataset.artist, cover: it.dataset.cover })).filter(t => t.url);
    index = items.indexOf(trackItem);
    if (index < 0) index = 0;
    start();
  });

  function start() {
    if (!playlist.length) return;
    const t = playlist[index];
    audio.src = t.url;
    coverEl.src = t.cover || '';
    titleEl.textContent = t.name || '';
    artistEl.textContent = t.artist || '';
    showPlayer();
    audio.play().catch(()=>{});
    btnPlay && (btnPlay.textContent = '⏸');
  }

  btnPlay && btnPlay.addEventListener('click', () => {
    if (!audio.src) return;
    if (audio.paused) { audio.play(); btnPlay.textContent='⏸'; } else { audio.pause(); btnPlay.textContent='▶'; }
  });
  btnNext && btnNext.addEventListener('click', () => {
    if (!playlist.length) return;
    index = shuffle ? Math.floor(Math.random()*playlist.length) : (index+1)%playlist.length;
    start();
  });
  btnPrev && btnPrev.addEventListener('click', () => {
    if (!playlist.length) return;
    index = shuffle ? Math.floor(Math.random()*playlist.length) : (index-1+playlist.length)%playlist.length;
    start();
  });
  btnRepeat && btnRepeat.addEventListener('click', ()=> { repeat=!repeat; btnRepeat.classList.toggle('active', repeat); });
  btnShuffle && btnShuffle.addEventListener('click', ()=> { shuffle=!shuffle; btnShuffle.classList.toggle('active', shuffle); });

  audio.addEventListener('timeupdate', ()=> {
    if (!audio.duration) return;
    const pct = (audio.currentTime/audio.duration)*100;
    progressBar.style.width = pct + '%';
    timeEl.textContent = formatTime(audio.currentTime) + ' / ' + formatTime(audio.duration);
  });

  progressBg && progressBg.addEventListener('click', (e)=> {
    if (!audio.duration) return;
    const rect = progressBg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = Math.min(Math.max(0, x/rect.width),1);
    audio.currentTime = pct * audio.duration;
  });

  audio.addEventListener('ended', ()=> {
    if (repeat) { audio.currentTime = 0; audio.play(); return; }
    if (!playlist.length) return;
    index = shuffle ? Math.floor(Math.random()*playlist.length) : (index+1)%playlist.length;
    start();
  });

  function formatTime(s){ if(!s||isNaN(s)) return '0:00'; const m=Math.floor(s/60); const sec=Math.floor(s%60).toString().padStart(2,'0'); return `${m}:${sec}`; }

  window.EuroniPlayer = { getPlaylist: ()=>playlist, getState: ()=>({index,repeat,shuffle}) };
})();
