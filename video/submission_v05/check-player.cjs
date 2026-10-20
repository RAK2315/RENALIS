const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const out=path.resolve(__dirname,'../../artifacts/submission-v05'),base='http://127.0.0.1:5176';
(async()=>{let browser;try{
 const range=await fetch(`${base}/artifacts/submission-v05/RENALIS_Team_Sigmoid_20min.mp4`,{headers:{Range:'bytes=0-1023'}});
 assert.equal(range.status,206,'Asset server must support HTTP byte ranges for seeking');
 assert.equal((await range.arrayBuffer()).byteLength,1024);
 browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1050}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(`${base}/artifacts/submission-v05/player.html`);
 await page.waitForFunction(()=>document.querySelector('video').readyState>=1,null,{timeout:60000});
 const meta=await page.locator('video').evaluate(v=>({seconds:v.duration,width:v.videoWidth,height:v.videoHeight}));
 assert.ok(Math.abs(meta.seconds-1200)<.1);assert.equal(meta.width,1920);assert.equal(meta.height,1080);
 await page.locator('video').evaluate(v=>{v.muted=true;});
 for(const t of [0,300,600,900]){
  await page.locator(`[data-time="${t}"]`).click();await page.waitForFunction(t=>Math.abs(document.querySelector('video').currentTime-t)<3,t,{timeout:60000});
  await page.locator('video').evaluate(v=>v.pause());
 }
 await page.locator('video').evaluate(v=>{v.currentTime=405;});
 await page.waitForFunction(()=>Math.abs(document.querySelector('video').currentTime-405)<1&&document.querySelector('video').readyState>=2&&!document.querySelector('video').seeking);
 await page.locator('video').evaluate(v=>v.play());
 await page.waitForFunction(()=>document.querySelector('video').currentTime>=407,null,{timeout:30000});
 await page.locator('video').evaluate(v=>v.pause());
 await page.locator('video').screenshot({path:path.join(out,'player-video-proof.png')});
 for(const width of [1440,768,390]){
  await page.setViewportSize({width,height:1050});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`Overflow ${width}`);
 }
 await page.setViewportSize({width:1440,height:1050});await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,'player-proof.png')});
 const links=await page.locator('a[href]').evaluateAll(xs=>xs.map(a=>({label:a.textContent,url:a.href})));
 const results=[];for(const l of links){const r=await fetch(l.url,{method:'HEAD'});assert.equal(r.status,200,l.label);results.push({label:l.label,status:r.status});}
 const waiting=page.waitForEvent('download');await page.getByRole('link',{name:'GitHub source ZIP',exact:true}).click();const d=await waiting;assert.equal(await d.failure(),null);
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'player-checks.json'),JSON.stringify({passed:true,meta,http_range_seeking:true,playback_advanced:true,chapter_buttons:[0,300,600,900],viewports:[1440,768,390],links:results,javascript_errors:errors},null,2));
 console.log('Final player metadata, seeking, downloads, links and responsive checks passed.');
}finally{if(browser)await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
