'use strict';
const video = document.querySelector('#motion');
const button = document.querySelector('#motion-toggle');
const preference = matchMedia('(prefers-reduced-motion: reduce)');
let userPaused = false;
let inView = true;
button.hidden = false;
function refresh() {
  const playing = !video.paused;
  button.textContent = playing ? 'Pause background' : 'Play background';
  button.setAttribute('aria-pressed', String(playing));
}
async function play() {
  if (!video.getAttribute('src')) {
    video.src = 'assets/video/active-edge-navy-cyan-loop.mp4';
    video.load();
  }
  try { await video.play(); } catch { refresh(); }
}
video.addEventListener('playing', () => { video.classList.add('ready'); refresh(); });
video.addEventListener('pause', refresh);
video.addEventListener('error', () => { video.classList.remove('ready'); button.textContent = 'Background unavailable'; button.disabled = true; });
button.addEventListener('click', () => {
  if (video.paused) { userPaused = false; play(); }
  else { userPaused = true; video.pause(); }
});
preference.addEventListener('change', () => {
  if (preference.matches) { video.pause(); video.classList.remove('ready'); }
  else if (!userPaused && !document.hidden && inView) play();
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) video.pause();
  else if (!preference.matches && !userPaused && inView) play();
});
if ('IntersectionObserver' in window) {
  new IntersectionObserver(entries => {
    inView = entries[0].isIntersecting;
    if (!inView) video.pause();
    else if (!preference.matches && !userPaused && !document.hidden) play();
  }).observe(video);
}
if (!preference.matches) play();
refresh();
