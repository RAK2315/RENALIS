const { chromium } = require(process.env.RENALIS_PLAYWRIGHT_PATH || 'playwright');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');

(async()=>{
  const browser=await chromium.launch({headless:true});
  const output=path.resolve('artifacts/qa');fs.mkdirSync(output,{recursive:true});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1100}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.request.post('http://127.0.0.1:5173/api/patients/RNL-014/measurements/reset');
    await page.goto('http://127.0.0.1:5173/workspace');
    await page.getByRole('button',{name:'Mechanism lab',exact:true}).click();
    await page.getByRole('heading',{name:'Same pressure. Different explanations.'}).waitFor();
    async function ready(){await page.waitForFunction(()=>document.querySelector('.mechanism-lab')?.getAttribute('aria-busy')==='false'&&document.querySelectorAll('.family-card').length===4);}
    async function range(id,value){await page.locator(id).evaluate((e,v)=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,v);e.dispatchEvent(new Event('input',{bubbles:true}));},value);await ready();}
    await ready();
    assert.match(await page.locator('.comparison-state').innerText(),/comparison remains unresolved/);
    assert.match(await page.locator('.no-measurement').innerText(),/No available measurement/);
    const downloadEvent=page.waitForEvent('download');
    await page.getByRole('button',{name:'Export evidence',exact:true}).click();
    const download=await downloadEvent;
    const downloaded=path.join(output,'mechanism-evidence.json');await download.saveAs(downloaded);
    const exported=JSON.parse(fs.readFileSync(downloaded,'utf8'));
    assert.equal(exported.families.length,4);
    assert.equal(exported.revision.length,16);
    assert.equal(exported.available_channels.length,3);
    assert.ok(exported.observations.every(r=>r.minute<=90));
    await page.screenshot({path:path.join(output,'mechanisms-desktop.png'),fullPage:true});
    await page.getByLabel('Relative blood volume',{exact:true}).uncheck();
    await page.getByLabel('Noninvasive cardiac output',{exact:true}).uncheck();
    await ready();
    assert.match(await page.locator('.no-measurement').innerText(),/No available measurement/);
    await page.getByLabel('Repeat cuff BP',{exact:true}).uncheck();await ready();
    assert.equal(await page.locator('.candidate-panel tbody tr').count(),0);
    await page.getByLabel('Relative blood volume',{exact:true}).check();
    await page.getByLabel('Noninvasive cardiac output',{exact:true}).check();
    await page.getByLabel('Repeat cuff BP',{exact:true}).check();await ready();
    await page.getByRole('button',{name:'Simulate Noninvasive cardiac output at +0 minutes',exact:true}).click();
    await page.locator('.measurement-evidence article').waitFor();await ready();
    assert.equal(await page.locator('.measurement-evidence article').count(),1);
    assert.match(await page.locator('.measurement-evidence').innerText(),/3.74 L\/min/);
    const supports=await page.locator('.family-card-top strong').allTextContents();
    assert.ok(Math.max(...supports.map(parseFloat))>Math.min(...supports.map(parseFloat)));
    await page.getByRole('button',{name:'Save comparison',exact:true}).click();
    await page.locator('.saved-lab-run').first().waitFor();
    await page.locator('.saved-lab-run').first().getByRole('button',{name:/Inspect original run/}).click();
    await page.locator('.immutable-report').waitFor();
    assert.match(await page.locator('.immutable-report').innerText(),/1 released observations/);
    await page.getByRole('button',{name:'Reset lab observations'}).click();await ready();
    await page.locator('.measurement-evidence').waitFor({state:'detached'});
    assert.match(await page.locator('.immutable-report').innerText(),/1 released observations/);
    await page.getByRole('button',{name:'Close report',exact:true}).click();
    await range('#clock',80);
    await page.getByRole('button',{name:'Simulate Relative blood volume at +5 minutes',exact:true}).click();
    await page.waitForFunction(()=>document.querySelector('#clock').value==='85');await ready();
    assert.match(await page.locator('.measurement-evidence').innerText(),/Minute 85/);
    await page.getByRole('button',{name:'Reset lab observations'}).click();await ready();
    await range('#clock',90);
    await page.getByText('Enter a research measurement manually',{exact:true}).click();
    await page.getByLabel('Research channel',{exact:true}).selectOption('relative_blood_volume');
    await page.locator('#manual-value').fill('120');
    await page.getByRole('button',{name:'Assimilate research observation'}).click();
    await page.locator('.lab-authority.contradicted').waitFor();await ready();
    assert.equal(await page.locator('#lab-rate').isDisabled(),true);
    assert.equal(await page.getByRole('button',{name:'Acquire synthetic measurement'}).count(),0);
    await page.getByRole('button',{name:'Reset lab observations'}).click();await ready();
    await page.getByRole('button',{name:'Run challenge suite'}).click();
    await page.locator('.challenge-results').waitFor({timeout:30000});
    assert.equal(await page.locator('.challenge-results tbody tr').count(),3);
    assert.match(await page.locator('.challenge-results').innerText(),/does not beat/);
    for(const width of [1440,1024,768,390,320]){
      await page.setViewportSize({width,height:1000});
      await page.waitForTimeout(200);
      const bounds=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
      assert.ok(bounds.scroll<=bounds.width+1,`Horizontal overflow at ${width}: ${bounds.scroll}`);
      await page.screenshot({path:path.join(output,`mechanisms-${width}.png`),fullPage:true});
      if(width===390){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,'mechanisms-mobile-top.png')});}
    }
    await page.setViewportSize({width:1440,height:1100});
    await range('#clock',120);
    await page.locator('.lab-authority.current_event').waitFor();
    assert.equal(await page.locator('#lab-rate').isDisabled(),true);
    await range('#clock',90);
    await page.locator('#patient').selectOption('RNL-032');await ready();
    await page.locator('.lab-authority.stale').waitFor();
    await page.locator('#patient').selectOption('RNL-027');await ready();
    await range('#clock',240);
    await page.locator('.lab-authority.complete').waitFor();
    assert.equal(await page.locator('.candidate-panel tbody tr').count(),0);
    assert.deepEqual(errors,[]);
    console.log('Mechanism lab: acquisition, availability, contradiction, immutable audit, challenge suite, safeguards, and 1440/1024/768/390/320px layouts passed.');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
