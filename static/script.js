// --- Главный плеер ---
// --- Главный плеер ---
const trackList=document.getElementById('trackList');
const player=document.getElementById('player');
const playPauseBtn=document.getElementById('playPause');
const prevBtn=document.getElementById('prev');
const nextBtn=document.getElementById('next');
const progress=document.getElementById('progress');
const currentTimeEl=document.getElementById('currentTime');
const durationEl=document.getElementById('duration');

let tracks=[],currentIndex=0,audio=new Audio(),isPlaying=false;

if(trackList){tracks=Array.from(trackList.children);tracks.forEach((li,i)=>li.addEventListener('click',()=>{currentIndex=i;playTrack();}));}

function playTrack(){audio.src=tracks[currentIndex].dataset.src;audio.play();isPlaying=true;playPauseBtn.textContent='⏸️';player.classList.remove('hidden');}
if(playPauseBtn)playPauseBtn.addEventListener('click',()=>{if(isPlaying){audio.pause();playPauseBtn.textContent='▶️';}else{audio.play();playPauseBtn.textContent='⏸️';}isPlaying=!isPlaying;});
if(prevBtn)prevBtn.addEventListener('click',()=>{currentIndex=(currentIndex-1+tracks.length)%tracks.length;playTrack();});
if(nextBtn)nextBtn.addEventListener('click',()=>{currentIndex=(currentIndex+1)%tracks.length;playTrack();});
audio.addEventListener('timeupdate',()=>{if(!audio.duration)return;const percent=(audio.currentTime/audio.duration)*100;if(progress)progress.value=percent;if(currentTimeEl)currentTimeEl.textContent=formatTime(audio.currentTime);if(durationEl)durationEl.textContent=formatTime(audio.duration);});
if(progress)progress.addEventListener('input',()=>{audio.currentTime=(progress.value/100)*audio.duration;});

// --- Плеер рекомендаций ---
const recTrackList=document.getElementById('recTrackList');
const recPlayer=document.getElementById('recPlayer');
const recPlayPauseBtn=document.getElementById('recPlayPause');
const recPrevBtn=document.getElementById('recPrev');
const recNextBtn=document.getElementById('recNext');
const recProgress=document.getElementById('recProgress');
const recCurrentTimeEl=document.getElementById('recCurrentTime');
const recDurationEl=document.getElementById('recDuration');

let recTracks=[],recIndex=0,recAudio=new Audio(),recIsPlaying=false;

if(recTrackList){recTracks=Array.from(recTrackList.children);recTracks.forEach((li,i)=>li.addEventListener('click',()=>{recIndex=i;playRecTrack();}));}

function playRecTrack(){recAudio.src=recTracks[recIndex].dataset.src;recAudio.play();recIsPlaying=true;recPlayPauseBtn.textContent='⏸️';recPlayer.classList.remove('hidden');}
if(recPlayPauseBtn)recPlayPauseBtn.addEventListener('click',()=>{if(recIsPlaying){recAudio.pause();recPlayPauseBtn.textContent='▶️';}else{recAudio.play();recPlayPauseBtn.textContent='⏸️';}recIsPlaying=!recIsPlaying;});
if(recPrevBtn)recPrevBtn.addEventListener('click',()=>{recIndex=(recIndex-1+recTracks.length)%recTracks.length;playRecTrack();});
if(recNextBtn)recNextBtn.addEventListener('click',()=>{recIndex=(recIndex+1)%recTracks.length;playRecTrack();});
recAudio.addEventListener('timeupdate',()=>{if(!recAudio.duration)return;const percent=(recAudio.currentTime/recAudio.duration)*100;if(recProgress)recProgress.value=percent;if(recCurrentTimeEl)recCurrentTimeEl.textContent=formatTime(recAudio.currentTime);if(recDurationEl)recDurationEl.textContent=formatTime(recAudio.duration);});
if(recProgress)recProgress.addEventListener('input',()=>{recAudio.currentTime=(recProgress.value/100)*recAudio.duration;});

function formatTime(sec){if(isNaN(sec))return '0:00';const m=Math.floor(sec/60);const s=Math.floor(sec%60);return `${m}:${s<10?'0':''}${s}`;}
