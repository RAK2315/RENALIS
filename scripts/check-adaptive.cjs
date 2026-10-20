const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const {spawn,execFileSync}=require('node:child_process');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'..');const out=path.join(root,'artifacts/qa/adaptive');fs.mkdirSync(out,{recursive:true});
const port=8012;const base=`http://127.0.0.1:${port}`;
const child=spawn(path.join(root,'.venv/Scripts/python.exe'),['-m','video.serve_capture',path.join(out,`qa-${Date.now()}.sqlite`),String(port)],{cwd:root,windowsHide:true,stdio:'pipe'});
let serverErrors='';child.stderr.on('data',d=>serverErrors+=d);
(async()=>{
 let browser;
 try{
  for(let n=0;n<100;n++){try{if((await fetch(`${base}/api/health`)).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
  browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1050}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/**',async route=>{try{const url=new URL(route.request().url());url.port=String(port);const r=await route.fetch({url:url.toString()});await route.fulfill({response:r});}catch{await route.abort();}});
  const ready=()=>page.waitForFunction(()=>document.querySelector('.evidence-journey')?.getAttribute('aria-busy')==='false'&&!!document.querySelector('.adaptive-plan'));
  await page.goto('http://127.0.0.1:5173/workspace?view=investigation&patient=RNL-014&minute=90');await ready();
  const panel=page.getByRole('region',{name:'Adaptive measurement planner'});
  await panel.getByRole('heading',{name:'Next discriminator: Noninvasive cardiac output'}).waitFor();
  await panel.getByRole('button',{name:'Acquire next discriminator',exact:true}).click();
  await panel.getByRole('heading',{name:'Next discriminator: Relative blood volume'}).waitFor();await ready();
  assert.match(await panel.innerText(),/Observed: 3.74 L\/min/);
  assert.match(await panel.innerText(),/Why did cardiac output leave two explanations/);
  assert.match(await panel.innerText(),/51.7%/);assert.match(await panel.innerText(),/46.2%/);
  assert.equal(await page.getByRole('spinbutton',{name:'Manual research observation',exact:true}).inputValue(),'');
  await panel.getByText('Why this channel rather than the alternatives?',{exact:true}).click();
  assert.match(await panel.locator('tbody tr').first().innerText(),/Relative blood volume.*0.39378/s);
  await panel.getByText('Why this channel rather than the alternatives?',{exact:true}).click();
  for(const width of [1440,1024,768,390,320]){
   await page.setViewportSize({width,height:1050});
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`Overflow at ${width}`);
   await panel.screenshot({path:path.join(out,`after-co-${width}.png`)});
  }
  await page.setViewportSize({width:1440,height:1050});
  await page.getByRole('combobox',{name:'Equipment configuration',exact:true}).selectOption('basic');
  await page.waitForFunction(()=>document.querySelector('.adaptive-plan')?.getAttribute('data-status')==='no_discriminator');await ready();
  assert.equal(await panel.getByRole('button',{name:'Acquire next discriminator',exact:true}).count(),0);
  await page.getByRole('combobox',{name:'Equipment configuration',exact:true}).selectOption('research');
  await panel.getByRole('heading',{name:'Next discriminator: Relative blood volume'}).waitFor();await ready();
  await page.getByRole('combobox',{name:'Failure probability',exact:true}).selectOption('1');
  await page.waitForFunction(()=>document.querySelector('.adaptive-plan')?.getAttribute('data-status')==='no_discriminator');await ready();
  await page.getByRole('combobox',{name:'Failure probability',exact:true}).selectOption('0');
  await panel.getByRole('heading',{name:'Next discriminator: Relative blood volume'}).waitFor();await ready();
  await panel.getByRole('button',{name:'Acquire next discriminator',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.adaptive-observed')?.textContent.includes('Observed: 85 % of start'));await ready();
  assert.match(await panel.innerText(),/66.9%/);assert.match(await panel.innerText(),/31.8%/);
  assert.match(await panel.innerText(),/has not identified a unique cause/);
  assert.equal(await page.getByRole('spinbutton',{name:'Manual research observation',exact:true}).inputValue(),'');
  assert.match(await page.locator('.journey-comparison').innerText(),/comparison remains unresolved/);
  await panel.screenshot({path:path.join(out,'after-rbv.png')});
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export this investigation',exact:true}).click();
  await (await download).saveAs(path.join(out,'investigation.json'));
  const saved=JSON.parse(fs.readFileSync(path.join(out,'investigation.json'),'utf8'));
  assert.deepEqual(saved.evidence.map(e=>e.value),[3.74,85]);assert.equal(saved.discrimination_plan.latest_evidence.value,85);
  assert.deepEqual(errors,[]);assert.doesNotMatch(serverErrors,/Traceback/);
  fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify({passed:true,checks:['actual CO 3.74 acquisition','automatic RBV selection','computed explanations and alternatives','actual RBV 85 acquisition','honest unresolved result','equipment/failure abstention','five responsive sizes','exported adaptive plan'],javascript_errors:errors},null,2));
  console.log('Adaptive measurement browser checks passed: actual two-step acquisition, no manual values, five responsive sizes.');
 }finally{if(browser)await browser.close();if(process.platform==='win32'){try{execFileSync('taskkill',['/pid',String(child.pid),'/T','/F'],{windowsHide:true,stdio:'ignore'});}catch{}}else child.kill();}
})().catch(e=>{console.error(e);process.exitCode=1;});
