const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const {spawn,execFileSync}=require('node:child_process');
const {once}=require('node:events');
const path=require('node:path');const fs=require('node:fs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'artifacts','video');
const python=path.join(root,'.venv','Scripts','python.exe');
const ffmpeg=execFileSync(python,['-c','import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8',windowsHide:true}).trim();
const timeline=JSON.parse(fs.readFileSync(path.join(out,'timeline.json'),'utf8'));
const total=Math.round(timeline.duration*timeline.fps);
if(timeline.revision!==2)throw Error('Prepare the v2 narration timeline before rendering.');
const previews=process.argv.includes('--preview');
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});try{
  async function page(){const p=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});p.on('pageerror',e=>{throw e;});await p.goto('http://127.0.0.1:5173/video/composition.html');await p.waitForFunction(()=>window.__ready,null,{timeout:60000});return p;}
  if(previews){const p=await page();for(const s of timeline.scenes){const moment=s.start+Math.min(s.duration*.46,5);await p.evaluate(t=>window.renderFrame(t),moment);await p.screenshot({path:path.join(out,`frame-${s.id}.png`)});console.log(`Preview ${s.id} @ ${moment.toFixed(2)}s`);}await p.evaluate(()=>window.renderFrame(3));await p.screenshot({path:path.join(out,'poster.png')});await p.close();return;}
  const workers=3,chunk=Math.ceil(total/workers);
  await Promise.all(Array.from({length:workers},async(_,worker)=>{const start=worker*chunk,end=Math.min(total,start+chunk);if(start>=end)return;const p=await page();const destination=path.join(out,`part-${worker}.mp4`);
    const args=['-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate',String(timeline.fps),'-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',destination];
    const encoder=spawn(ffmpeg,args,{windowsHide:true,stdio:['pipe','ignore','pipe']});let err='';encoder.stderr.on('data',b=>err+=b.toString());let exited=false;const completed=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('close',code=>{exited=true;code===0?resolve():reject(Error(err||`Encoder ${worker}: ${code}`));});});
    encoder.stdin.on('error',()=>{});
    try{for(let i=start;i<end;i++){if(exited)throw Error(err||'Encoder exited early');await p.evaluate(t=>window.renderFrame(t),i/timeline.fps);const frame=await p.screenshot({type:'jpeg',quality:94,animations:'disabled'});if(!encoder.stdin.write(frame))await once(encoder.stdin,'drain');if((i-start)%300===0)console.log(`Worker ${worker+1}: ${i-start}/${end-start} frames`);}encoder.stdin.end();await completed;console.log(`Worker ${worker+1} complete.`);}catch(e){encoder.kill();throw e;}finally{await p.close();}
  }));
  fs.writeFileSync(path.join(out,'parts.txt'),Array.from({length:workers},(_,i)=>`file 'part-${i}.mp4'`).join('\n')+'\n');
  execFileSync(ffmpeg,['-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',path.join(out,'parts.txt'),'-i',path.join(out,'soundtrack.wav'),'-i',path.join(out,'renalis-explainer.srt'),'-map','0:v:0','-map','1:a:0','-map','2:s:0','-c:v','copy','-c:a','aac','-b:a','192k','-c:s','mov_text','-disposition:s:0','0','-af','loudnorm=I=-16:TP=-1.5:LRA=8','-metadata','title=RENALIS — A clearer next question','-metadata','comment=Synthetic research demonstration. Synthetic narration; original generated score.','-metadata:s:s:0','language=eng','-movflags','+faststart','-t',String(timeline.duration),path.join(out,'renalis-explainer.mp4')],{windowsHide:true,stdio:'inherit'});
  execFileSync(ffmpeg,['-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',path.join(out,'parts.txt'),'-i',path.join(out,'original-score.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','loudnorm=I=-22:TP=-2:LRA=8','-movflags','+faststart','-t',String(timeline.duration),path.join(out,'renalis-music-only.mp4')],{windowsHide:true,stdio:'inherit'});
  fs.copyFileSync(path.join(__dirname,'player.html'),path.join(out,'player.html'));
  console.log(`Finished: ${path.join(out,'renalis-explainer.mp4')} (${timeline.duration.toFixed(2)}s, 1920×1080, ${timeline.fps}fps)`);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
