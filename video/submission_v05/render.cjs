// Deterministic 24fps motion graphics. Cache every 30s scene and each 5m chapter.
const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const {spawn,execFileSync}=require('node:child_process');const {once}=require('node:events');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'artifacts/submission-v05');
const python=path.join(root,'.venv-video/Scripts/python.exe');
const ffmpeg=execFileSync(python,['-c','import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8',windowsHide:true}).trim();
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const fps=24;const html=fs.readFileSync(path.join(__dirname,'composition.html'));
const sceneDir=path.join(out,'scenes');fs.mkdirSync(sceneDir,{recursive:true});
const timelinePath=path.join(out,'timeline.json');
const scenes=JSON.parse(fs.readFileSync(fs.existsSync(timelinePath)?timelinePath:path.join(__dirname,'story.json'),'utf8'));
const cues=fs.existsSync(path.join(out,'captions.json'))?JSON.parse(fs.readFileSync(path.join(out,'captions.json'),'utf8')):[];
const progressPath=path.join(out,'progress.json');const progress=fs.existsSync(progressPath)?JSON.parse(fs.readFileSync(progressPath,'utf8')):{scenes:{},chapters:{}};
function checkpoint(){progress.updated_at=new Date().toISOString();fs.writeFileSync(progressPath,JSON.stringify(progress,null,2));}
function valid(file,receipt,signature){try{const r=JSON.parse(fs.readFileSync(receipt));return r.signature===signature&&fs.statSync(file).size===r.bytes&&r.frames===720;}catch{return false;}}
function run(args){return new Promise((res,rej)=>{const p=spawn(ffmpeg,['-y','-hide_banner','-loglevel','error',...args],{windowsHide:true,stdio:['ignore','ignore','pipe']});let err='';p.stderr.on('data',x=>err+=x);p.on('error',rej);p.on('exit',code=>code===0?res():rej(Error(err)));});}
(async()=>{let browser;try{
 browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 async function page(){const p=await browser.newPage({viewport:{width:1920,height:1080}});p.on('pageerror',e=>{throw e;});await p.goto('http://127.0.0.1:5176/video/submission_v05/composition.html');await p.waitForFunction(()=>window.__ready);return p;}
 if(process.argv.includes('--preview')){const p=await page();for(const s of scenes){await p.evaluate(t=>window.renderFrame(t),s.start+15);await p.screenshot({path:path.join(out,`preview-${s.id}.png`)});}await p.evaluate(()=>window.renderFrame(6));await p.screenshot({path:path.join(out,'poster.png')});console.log('Forty composition previews ready.');return;}
 const chapterArg=process.argv.indexOf('--chapter');const chapter=chapterArg>=0?Number(process.argv[chapterArg+1]):null;
 const queue=scenes.filter(s=>!chapter||s.chapter===chapter);
 if(scenes.length!==40||!queue.every(s=>s.beats))throw Error('Assemble the selected chapter narration timings before rendering.');
 async function worker(number){const p=await page();try{while(queue.length){const s=queue.shift();const dst=path.join(sceneDir,`scene-${s.id}.mp4`),receipt=dst+'.json';
  const poster=s.clip?fs.readFileSync(path.join(out,`screen-${s.clip}.png`)):Buffer.from('');
  const signature=hash(Buffer.concat([html,poster,Buffer.from(JSON.stringify([s,cues.filter(c=>c.scene===s.id),scenes[Number(s.id)-2]||null]))]));
  if(valid(dst,receipt,signature)){console.log('Reused scene',s.id);progress.scenes[s.id]={status:'complete',signature};checkpoint();continue;}
  const proc=spawn(ffmpeg,['-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-r',String(fps),'-threads','2','-movflags','+faststart',dst],{windowsHide:true,stdio:['pipe','ignore','pipe']});
  let err='';proc.stderr.on('data',x=>err+=x);let ended=false;const completion=new Promise((resolve,reject)=>{proc.on('error',reject);proc.on('exit',code=>{ended=true;code===0?resolve():reject(Error(err));});});proc.stdin.on('error',()=>{});
  for(let frame=0;frame<720;frame++){if(ended)throw Error(err||'Encoder stopped');const jpeg=await p.evaluate(t=>window.encodeFrame(t),s.start+frame/fps);if(!proc.stdin.write(Buffer.from(jpeg,'base64')))await once(proc.stdin,'drain');if(frame===360)console.log(`Worker ${number}: scene ${s.id} halfway`);}
  proc.stdin.end();await completion;
  const r={signature,frames:720,fps,width:1920,height:1080,duration:30,bytes:fs.statSync(dst).size};fs.writeFileSync(receipt,JSON.stringify(r,null,2));progress.scenes[s.id]={status:'complete',...r};checkpoint();console.log('Completed scene',s.id);
 }}finally{await p.close();}}
 await Promise.all(Array.from({length:Number(process.env.RENALIS_RENDER_WORKERS||4)},(_,i)=>worker(i+1)));
 const footage=JSON.parse(fs.readFileSync(path.join(out,'footage.json'),'utf8'));
 for(const ch of chapter?[chapter]:[1,2,3,4]){
  const list=scenes.filter(s=>s.chapter===ch),parts=path.join(out,`chapter-${ch}-parts.txt`);
  const picturePath=path.join(out,`chapter-${String(ch).padStart(2,'0')}-picture.mp4`);
  const deliveredPath=path.join(out,`RENALIS_Chapter_${ch}_5min.mp4`);
  const recipe=hash(JSON.stringify({version:1,scenes:list.map(s=>progress.scenes[s.id].signature),footage:list.filter(s=>s.clip).map(s=>[footage[s.clip],hash(fs.readFileSync(path.join(out,footage[s.clip].file)))]),audio:hash(fs.readFileSync(path.join(out,`chapter-${String(ch).padStart(2,'0')}-soundtrack.wav`)))}));
  if(progress.chapters[ch]?.recipe===recipe&&fs.existsSync(deliveredPath)&&fs.existsSync(picturePath)&&progress.chapters[ch].picture===hash(fs.readFileSync(picturePath))){console.log('Reused complete five-minute chapter',ch);continue;}
  fs.writeFileSync(parts,list.map(s=>`file 'scenes/scene-${s.id}.mp4'`).join('\n'));
  const base=path.join(out,`chapter-${ch}-base.mp4`);await run(['-f','concat','-safe','0','-i',parts,'-c','copy',base]);
  let args=['-i',base],filters=[],input=1,last='0:v';
  for(const s of list.filter(s=>s.clip)){
   const f=footage[s.clip],start=s.start-(ch-1)*300+8;
   args.push('-ss',String(f.trim_start||0),'-i',path.join(out,f.file));
   filters.push(`[${input}:v]trim=duration=12,scale=1080:608:flags=lanczos,fps=24,setsar=1,tpad=stop_mode=clone:stop_duration=22,setpts=PTS-STARTPTS+${start}/TB[clip${input}]`);
   filters.push(`[${last}][clip${input}]overlay=x=752:y=240:eof_action=pass:enable='between(t,${start},${start+21.55})'[v${input}]`);last=`v${input}`;input++;
  }
  const silent=path.join(out,`chapter-${String(ch).padStart(2,'0')}-picture.mp4`);
  if(filters.length)args.push('-filter_complex',filters.join(';'),'-map',`[${last}]`);else args.push('-map','0:v');
  await run([...args,'-an','-t','300','-c:v','libx264','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-r','24','-threads','4',silent]);
  await run(['-i',silent,'-i',path.join(out,`chapter-${String(ch).padStart(2,'0')}-soundtrack.wav`),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-t','300','-movflags','+faststart',path.join(out,`RENALIS_Chapter_${ch}_5min.mp4`)]);
  progress.chapters[ch]={status:'complete',seconds:300,recipe,picture:hash(fs.readFileSync(silent))};checkpoint();console.log('Completed five-minute chapter',ch);
 }
 if(!chapter){const parts=path.join(out,'chapters.txt');fs.writeFileSync(parts,[1,2,3,4].map(ch=>`file 'chapter-${String(ch).padStart(2,'0')}-picture.mp4'`).join('\n'));
  const final=path.join(out,'RENALIS_Team_Sigmoid_20min.mp4');
  await run(['-f','concat','-safe','0','-i',parts,'-i',path.join(out,'soundtrack.wav'),'-i',path.join(out,'captions.srt'),'-map','0:v','-map','1:a','-map','2:s','-c:v','copy','-c:a','aac','-b:a','192k','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000','-c:s','mov_text','-metadata','title=RENALIS — Team Sigmoid','-metadata','artist=Rehaan, JSS University, Noida','-movflags','+faststart','-t','1200',final]);
  progress.final={status:'complete',file:path.basename(final),sha256:hash(fs.readFileSync(final))};checkpoint();console.log('Joined final 20-minute film.');
 }
}finally{if(browser)await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
