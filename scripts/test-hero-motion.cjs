// Offline lifecycle checks: no browser, network, credentials or publication.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(new URL('../assets/js/hero-motion.js', 'file://' + __filename), 'utf8');
function fixture(reduced = false, reject = false) {
  const events = {}, classes = new Set();
  const video = {paused:true,src:'',classList:{add:x=>classes.add(x),remove:x=>classes.delete(x)},getAttribute:()=>video.src,
    load(){},async play(){if(reject)throw Error('blocked');video.paused=false;events.playing?.();},pause(){video.paused=true;events.pause?.();},addEventListener:(e,f)=>events[e]=f};
  const button = {hidden:true,setAttribute:(k,v)=>button[k]=v,addEventListener:(e,f)=>button[e]=f};
  const preference = {matches:reduced,addEventListener:(e,f)=>preference.change=f};
  const document = {hidden:false,querySelector:s=>s==='#motion'?video:button,addEventListener:(e,f)=>document[e]=f};
  let observer;
  const context = {document,matchMedia:()=>preference,window:{IntersectionObserver:true},IntersectionObserver:class{constructor(f){observer=f;}observe(){}}};
  vm.runInNewContext(source,context);
  return {video,button,preference,document,events,classes,intersect:visible=>observer([{isIntersecting:visible}])};
}
(async()=>{
  let f=fixture(); assert.equal(f.video.paused,false); assert.equal(f.button['aria-pressed'],'true'); assert.equal(f.button.hidden,false);
  f.button.click(); assert.equal(f.video.paused,true); assert.equal(f.button.textContent,'Play background');
  f.document.hidden=true;f.document.visibilitychange();f.document.hidden=false;f.document.visibilitychange();assert.equal(f.video.paused,true);
  f.button.click();assert.equal(f.video.paused,false);
  f.intersect(false);assert.equal(f.video.paused,true);f.intersect(true);assert.equal(f.video.paused,false);
  f.document.hidden=true;f.document.visibilitychange();assert.equal(f.video.paused,true);f.document.hidden=false;f.document.visibilitychange();assert.equal(f.video.paused,false);
  f=fixture(true);assert.equal(f.video.src,'');assert.equal(f.video.paused,true);assert.equal(f.classes.has('ready'),false);
  f.button.click();assert.equal(f.video.paused,false);assert.equal(f.video.src,'assets/video/active-edge-navy-cyan-loop.mp4');
  f.preference.change();assert.equal(f.video.paused,true);assert.equal(f.classes.has('ready'),false);
  f.preference.matches=false;f.preference.change();assert.equal(f.video.paused,false);
  f=fixture(false,true);await Promise.resolve();await Promise.resolve();assert.equal(f.video.paused,true);assert.equal(f.button.textContent,'Play background');
  f.events.error();assert.equal(f.button.disabled,true);assert.equal(f.classes.has('ready'),false);
  console.log('PASS: autoplay, pause/resume, manual pause retention, offscreen/hidden pause, reduced-motion no-fetch, preference change, blocked autoplay, media failure');
})().catch(error=>{console.error(error);process.exit(1);});
