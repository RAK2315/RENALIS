const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const {spawn}=require('node:child_process');
const fs=require('node:fs');
const path=require('node:path');
const net=require('node:net');
const root=path.resolve(__dirname,'..');
const out=path.join(root,'artifacts','video','assets');fs.mkdirSync(out,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function freePort(){const server=net.createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));const port=server.address().port;await new Promise(r=>server.close(r));return port;}
(async()=>{
  const port=await freePort();
  const db=path.join(root,'artifacts','video',`capture-${Date.now()}.sqlite`);
  const api=spawn(path.join(root,'.venv','Scripts','python.exe'),['-m','video.serve_capture',db,String(port)],{cwd:root,windowsHide:true,stdio:['ignore','ignore','pipe']});
  let apiError='';api.stderr.on('data',b=>apiError+=b.toString());
  const browser=await chromium.launch({headless:true});
  const meta={};
  try{
    let up=false;for(let i=0;i<60;i++){try{const r=await fetch(`http://127.0.0.1:${port}/api/health`);if(r.ok){up=true;break;}}catch{}await sleep(250);}if(!up)throw Error(apiError||'Isolated filming API did not start.');
    const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1.5});
    await page.route('**/api/**',async route=>{const u=new URL(route.request().url());u.port=String(port);const r=await route.fetch({url:u.toString()});await route.fulfill({response:r});});
    async function save(id,targets={}){
      await page.evaluate(()=>scrollTo(0,0));await page.evaluate(()=>document.fonts.ready);await sleep(250);
      const info=await page.evaluate(()=>({cssWidth:innerWidth,cssHeight:document.documentElement.scrollHeight}));
      const boxes={};for(const [key,selector] of Object.entries(targets)){const b=await page.locator(selector).first().boundingBox();if(b)boxes[key]=b;}
      // Capture complete individual elements. The film contains these images
      // at their natural aspect ratio rather than scrolling a full-page crop.
      for(const [key,selector] of Object.entries(targets)){
        const element=page.locator(selector).first();
        if(boxes[key]){
          await element.screenshot({path:path.join(out,`${id}--${key}.png`),animations:'disabled'});
          boxes[key].asset=`${id}--${key}`;
        }
      }
      await page.evaluate(()=>scrollTo(0,0));
      await page.screenshot({path:path.join(out,`${id}.png`),fullPage:true,animations:'disabled'});meta[id]={...info,targets:boxes};console.log(`Captured ${id} (${info.cssWidth} × ${info.cssHeight} CSS px)`);
    }
    await page.goto('http://127.0.0.1:5173/');await page.locator('.hero-chart svg[role=img]').waitFor();
    await save('landing',{cta:'.hero-actions .site-button',hero:'.landing-hero',workflow:'.workflow-section',proof:'.evidence-landing'});
    await page.goto('http://127.0.0.1:5173/workspace?view=cockpit&patient=RNL-014&minute=90');
    await page.waitForFunction(()=>document.querySelector('.cockpit')&&!document.querySelector('.cockpit').classList.contains('updating')&&!document.querySelector('.scenario-panel .button').disabled);
    await save('workspace',{balance:'.physiology-panel',chart:'.forecast-panel',rate:'.scenario-input',sidebar:'.sidebar'});
    await page.locator('#rate').evaluate(e=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,1100);e.dispatchEvent(new Event('input',{bubbles:true}));});
    await page.getByRole('button',{name:'Step down at +15m',exact:true}).click();await sleep(600);
    await page.waitForFunction(()=>!document.querySelector('.scenario-panel .button').disabled);
    await save('workspace-alternative',{rate:'.scenario-input',chart:'.forecast-panel'});
    await page.getByRole('button',{name:'Mechanism lab',exact:true}).click();
    async function labReady(){await page.waitForFunction(()=>document.querySelector('.mechanism-lab')?.getAttribute('aria-busy')==='false'&&document.querySelectorAll('.family-card').length===3);}
    await labReady();
    await save('mechanisms',{families:'.family-grid',chart:'.mechanism-plot-panel',measure:'.measurement-panel',acquire:'.recommended-measurement .button',candidates:'.candidate-panel'});
    await page.getByRole('button',{name:'Acquire synthetic measurement',exact:true}).click();await page.locator('.measurement-evidence article').waitFor();await labReady();
    await save('updated',{families:'.family-grid',audit:'.measurement-evidence',support:'.support-panel'});
    await page.getByRole('button',{name:'Save comparison',exact:true}).click();await page.locator('.saved-lab-run').first().waitFor();
    await page.locator('.saved-lab-run').first().getByRole('button',{name:/Inspect original run/}).click();await page.locator('.immutable-report').waitFor();
    await save('saved',{report:'.immutable-report'});
    await page.getByRole('button',{name:'Reset lab observations',exact:true}).click();await labReady();await page.locator('.measurement-evidence').waitFor({state:'detached'});
    await page.getByText('Enter a research measurement manually',{exact:true}).click();
    await page.locator('#manual-channel').selectOption('relative_blood_volume');await page.locator('#manual-value').fill('120');await page.getByRole('button',{name:'Assimilate research observation',exact:true}).click();await page.locator('.lab-authority.contradicted').waitFor();await labReady();
    await save('contradiction',{banner:'.lab-authority.contradicted',families:'.family-grid',audit:'.measurement-evidence'});
    await page.goto('http://127.0.0.1:5173/research');await page.locator('.research-stat-row').waitFor();await page.locator('.source-library article').first().waitFor();await page.locator('.project-resources a').first().waitFor();
    await save('research',{method:'#method',results:'#evidence',sources:'#sources',resources:'#resources'});
    const results=await (await fetch(`http://127.0.0.1:${port}/api/demo-example`)).json();meta.demoResult=results;
    const measured=await (await fetch(`http://127.0.0.1:${port}/api/patients/RNL-014/lab-runs/1`)).json();meta.measuredResult=measured.result;
    fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify(meta,null,2));
    console.log('Capture complete. Real production API and synthetic acquisition; main workspace database untouched.');
  }finally{await browser.close();api.kill();}
})().catch(e=>{console.error(e);process.exitCode=1;});
