// Actual website footage; all acquisition and persistence use an isolated database.
const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const {spawn,execFileSync}=require('node:child_process');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'artifacts/submission-v05');
const story=JSON.parse(fs.readFileSync(path.join(__dirname,'story.json'),'utf8'));
const port=8015,base=`http://127.0.0.1:${port}/api`,pid='RNL-014';
const body={cutoff:90,rate_ml_h:650,equipment:'research',profile:'constant'};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const child=spawn(path.join(root,'.venv/Scripts/python.exe'),['-m','video.serve_capture',path.join(out,'filming.sqlite'),String(port)],{cwd:root,windowsHide:true,stdio:'pipe'});
let stderr='';child.stderr.on('data',x=>stderr+=x);
async function post(url,data={}){const r=await fetch(`${base}${url}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!r.ok)throw Error(`${url}: ${await r.text()}`);return r.json();}
const prefix=`/patients/${pid}`;
(async()=>{let browser;try{
 for(let i=0;i<100;i++){try{if((await fetch(`${base}/health`)).ok)break;}catch{}await wait(100);}
 browser=await chromium.launch({headless:true});
 const ids=[...new Set(story.map(s=>s.clip).filter(Boolean))];
 const manifest={};const errors=[];
 for(const id of ids){
  const dst=path.join(out,`footage-${id}.webm`),poster=path.join(out,`screen-${id}.png`);
  const sig=crypto.createHash('sha256').update(fs.readFileSync(__filename)).update(fs.readFileSync(path.join(root,'src/AdaptiveMeasurement.tsx'))).digest('hex');
  const receipt=dst+'.json';
  if(fs.existsSync(dst)&&fs.existsSync(poster)&&fs.existsSync(receipt)&&JSON.parse(fs.readFileSync(receipt)).signature===sig){manifest[id]=JSON.parse(fs.readFileSync(receipt));console.log('Cached footage',id);continue;}
  await post(`${prefix}/measurements/reset`);
  const afterCO=['after-co','ranking','outcomes','acquire-rbv','decision-value','resources','audit','correction','save'];
  const afterRBV=['audit','correction','save'];
  if(afterCO.includes(id))await post(`${prefix}/measurements`,{...body,channel:'cardiac_output'});
  if(afterRBV.includes(id))await post(`${prefix}/measurements`,{...body,channel:'relative_blood_volume'});
  const context=await browser.newContext({viewport:{width:1600,height:900},recordVideo:{dir:path.join(out,'raw-footage'),size:{width:1600,height:900}}});
  const recordingStart=Date.now();const page=await context.newPage();page.setDefaultTimeout(30000);console.log('Filming',id);page.on('pageerror',e=>errors.push(`${id}: ${e.message}`));
  await page.route('**/api/**',async route=>{const u=new URL(route.request().url());u.port=String(port);const r=await route.fetch({url:u.toString()});await route.fulfill({response:r});});
  await page.goto('http://127.0.0.1:5174/workspace?view=investigation&patient=RNL-014&minute=90');
  const ready=()=>page.waitForFunction(()=>document.querySelector('.evidence-journey')?.getAttribute('aria-busy')==='false'&&document.querySelectorAll('.journey-families>button').length===4);
  await ready();
  await page.addStyleTag({content:'.sidebar{display:none!important}.main-shell{margin-left:0!important}.toast{display:none!important}html{scroll-behavior:smooth}.evidence-journey>.panel{scroll-margin-top:12px}.adaptive-plan{scroll-margin-top:12px}.film-cursor{position:fixed;z-index:999999;width:26px;height:26px;border:3px solid #c09546;border-radius:50%;pointer-events:none;background:#dfb85c44;transform:translate(-50%,-50%)}'});
  await page.evaluate(()=>{const c=document.createElement('div');c.className='film-cursor';document.body.append(c);document.addEventListener('mousemove',e=>{c.style.left=e.clientX+'px';c.style.top=e.clientY+'px';});});
  let selector={workspace:'.journey-intro',history:'#journey-memory','history-details':'#journey-memory',physiology:'#journey-physiology',families:'#journey-compare','planner-before':'.adaptive-plan','acquire-co':'.adaptive-plan','after-co':'.adaptive-plan',ranking:'.adaptive-ranking',outcomes:'.adaptive-outcomes','acquire-rbv':'.adaptive-plan','decision-value':'.journey-acquire',resources:'.journey-resources',audit:'#journey-audit',correction:'#journey-audit',save:'#journey-audit',observed:'.release-result',limitations:'.journey-caution',policy:'.release-result:last-of-type','current-event':'.journey-intro',stale:'.journey-intro',transport:'.longitudinal'}[id];
  if(id==='policy')selector='.release-result:has-text("Independent holdout")';
  if(id==='transport')selector='section:has(> div > h2:text-is("Carry a state across several sessions."))';
  if(id==='transport')await page.getByRole('button',{name:'Run conditional transport',exact:true}).evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));
  else await page.locator(selector).first().evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));
  const inPoint=Date.now();await wait(900);
  if(id==='history-details'){await page.locator('#journey-memory summary').click();await page.locator('#journey-memory table').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));}
  if(id==='physiology'){await page.locator('.physiology-node').nth(0).click();await wait(1300);await page.locator('.physiology-node').nth(3).click();}
  if(id==='families'){await page.locator('.journey-families>button').nth(2).click();await wait(1300);await page.locator('.journey-families>button').nth(3).click();}
  if(id==='acquire-co'||id==='acquire-rbv'){
   await page.getByRole('button',{name:'Acquire next discriminator',exact:true}).click();
   await page.waitForFunction(v=>document.querySelector('.adaptive-observed')?.textContent.includes(v),id==='acquire-co'?'3.74':'85 %');
   await ready();await page.locator('.adaptive-plan').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));
  }
  if(id==='ranking'){await page.locator('.adaptive-ranking summary').click();await page.locator('.adaptive-ranking table').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));}
  if(id==='resources'){
   await page.getByRole('combobox',{name:'Equipment configuration',exact:true}).selectOption('basic');await wait(1400);
   await page.getByRole('combobox',{name:'Equipment configuration',exact:true}).selectOption('research');await wait(1400);
   await page.getByRole('combobox',{name:'Failure probability',exact:true}).selectOption('1');await ready();await page.locator('.adaptive-plan').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));
  }
  if(id==='correction'){
   await page.getByText('Append a correction without rewriting the original evidence',{exact:true}).click();
   await page.getByRole('spinbutton',{name:'Corrected observation value'}).fill('85.1');
   await page.getByRole('textbox',{name:'Correction reason'}).fill('Synthetic demonstration: verified transcription correction.');
   await page.getByRole('button',{name:'Append correction',exact:true}).click();await ready();await page.locator('.journey-updates').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));
  }
  if(id==='save'){
   await page.getByRole('textbox',{name:'Review note / symptoms / handover context'}).fill('Synthetic review: volume leads, cardiac remains plausible; no clinical action.');
   await page.getByRole('button',{name:'Save review note',exact:true}).click();await ready();
   await page.getByRole('button',{name:'Save immutable comparison',exact:true}).click();await ready();
  }
  if(id==='current-event'){
   await page.locator('#clock').evaluate(e=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,95);e.dispatchEvent(new Event('input',{bubbles:true}));});
   await page.locator('.journey-authority.current_event').waitFor();await page.locator('.journey-authority').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));
  }
  if(id==='stale'){await page.locator('#patient').selectOption('RNL-032');await page.locator('.journey-authority.stale').waitFor();await page.locator('.journey-authority').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));}
  if(id==='transport'){await page.getByRole('button',{name:'Run conditional transport',exact:true}).click();await page.getByText(/Mass-balance numerical error/).waitFor();}
  await wait(1200);await page.screenshot({path:poster});
  const elapsed=(Date.now()-inPoint)/1000;await wait(Math.max(500,(12-elapsed)*1000));
  const file=page.video();await page.close();await context.close();fs.copyFileSync(await file.path(),dst);
  const data={id,file:path.basename(dst),poster:path.basename(poster),trim_start:(inPoint-recordingStart)/1000,signature:sig,source:'Actual local interface; isolated fictional-patient database'};
  fs.writeFileSync(receipt,JSON.stringify(data,null,2));manifest[id]=data;fs.writeFileSync(path.join(out,'footage.json'),JSON.stringify(manifest,null,2));console.log('Captured',id);
 }
 await post(`${prefix}/measurements/reset`);const before=await post(`${prefix}/investigation`,body);
 await post(`${prefix}/measurements`,{...body,channel:'cardiac_output'});const afterCO=await post(`${prefix}/investigation`,body);
 await post(`${prefix}/measurements`,{...body,channel:'relative_blood_volume'});const afterRBV=await post(`${prefix}/investigation`,body);
 fs.writeFileSync(path.join(out,'film-data.json'),JSON.stringify({before,afterCO,afterRBV},null,2));
 fs.writeFileSync(path.join(out,'capture-checks.json'),JSON.stringify({javascript_errors:errors,clips:ids.length,passed:errors.length===0&&!stderr.includes('Traceback')},null,2));
 if(errors.length)throw Error(errors.join('\n'));
}finally{if(browser)await browser.close();try{execFileSync('taskkill',['/pid',String(child.pid),'/T','/F'],{windowsHide:true,stdio:'ignore'});}catch{}}})().catch(e=>{console.error(e);process.exitCode=1;});
