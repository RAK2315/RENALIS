const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const assert=require('node:assert/strict');
const fs=require('fs');
const path=require('path');
(async()=>{
  const browser=await chromium.launch({headless:true});
  const output=path.resolve('artifacts/qa');fs.mkdirSync(output,{recursive:true});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1040}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto('http://127.0.0.1:5173/');
    await page.getByRole('heading',{level:1,name:/A clearer next question/}).waitFor();
    const failurePage=await browser.newPage();
    await failurePage.route('**/api/demo-example',route=>route.abort());
    await failurePage.goto('http://127.0.0.1:5173/');
    await failurePage.getByText('The computed example is currently unavailable.',{exact:true}).waitFor();
    await failurePage.unroute('**/api/demo-example');
    await failurePage.getByRole('button',{name:'Try again',exact:true}).click();
    await failurePage.locator('.hero-chart svg[role=img]').waitFor();
    await failurePage.route('**/api/**',route=>route.abort());
    await failurePage.goto('http://127.0.0.1:5173/research');
    await failurePage.locator('.research-callout[role=alert]').waitFor();
    assert.equal(await failurePage.locator('.source-library article').count(),11);
    await failurePage.close();
    await page.locator('.hero-chart svg[role=img]').waitFor();
    const hero=await (await page.request.get('http://127.0.0.1:5173/api/demo-example')).json();
    assert.ok((await page.locator('.hero-model-note').innerText()).includes(hero.families.find(f=>f.id==='volume').alternative_end_sbp.toFixed(1)));
    await page.getByRole('button',{name:'Vascular response',exact:true}).click();
    assert.ok((await page.locator('.hero-model-note').innerText()).includes(hero.families.find(f=>f.id==='vascular').alternative_end_sbp.toFixed(1)));
    await page.getByRole('button',{name:'Cardiac response',exact:true}).click();
    assert.ok((await page.locator('.hero-model-note').innerText()).includes(hero.families.find(f=>f.id==='cardiac').alternative_end_sbp.toFixed(1)));
    await page.getByRole('button',{name:'Volume / refill',exact:true}).click();
    await page.screenshot({path:path.join(output,'landing-desktop-viewport.png')});
    await page.screenshot({path:path.join(output,'landing-desktop.png'),fullPage:true});
    await page.getByRole('link',{name:'How it works',exact:true}).click();
    await page.waitForURL('**/#how-it-works');
    await page.getByRole('link',{name:'Research & evidence',exact:true}).click();
    await page.getByRole('heading',{level:1,name:/The reasoning/}).waitFor();
    await page.locator('.research-stat-row').waitFor();
    await page.getByRole('heading',{name:'History, uncertainty and the cost of evidence',exact:true}).waitFor();
    await page.waitForFunction(()=>document.querySelector('.current-release')?.textContent.includes('61,947'));
    assert.match(await page.locator('.current-release').innerText(),/0.24145/);
    await page.locator('.project-resources a').first().waitFor();
    assert.match(await page.locator('.research-stat-row').innerText(),/211/);
    assert.match(await page.locator('.research-metric-bars').innerText(),/10.679/);
    assert.match(await page.locator('.evidence-block').innerText(),/0.2656/);
    assert.equal(await page.locator('.source-library article').count(),11);
    await page.getByRole('button',{name:'Data',exact:true}).click();
    const filtered=await page.locator('.source-library .source-meta>span:first-child').allTextContents();
    assert.ok(filtered.length>0&&filtered.every(c=>c==='data'));
    await page.getByRole('button',{name:'All sources',exact:true}).click();
    await page.getByRole('searchbox',{name:'Search research sources'}).fill('nonexistent-random-qa-query');
    await page.getByRole('heading',{name:'No sources match this search.'}).waitFor();
    await page.getByRole('button',{name:'Clear filters'}).click();
    assert.equal(await page.locator('.source-library article').count(),11);
    const resources=await page.locator('.project-resources a').first().getAttribute('href');assert.ok(resources);
    const links=await page.locator('.project-resources a').evaluateAll(els=>els.map(e=>e.getAttribute('href')));
    assert.ok(links.length>=9);
    for(const link of links){const response=await page.request.get(`http://127.0.0.1:5173${link}`);assert.equal(response.status(),200,link);assert.ok((await response.body()).length>100,link);}
    await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,'research-desktop-viewport.png')});
    for(const route of ['/','/research']){
      await page.goto(`http://127.0.0.1:5173${route}`);
      if(route==='/research'){
        await page.locator('.research-stat-row').waitFor();
        await page.getByRole('heading',{name:'History, uncertainty and the cost of evidence',exact:true}).waitFor();
        await page.waitForFunction(()=>document.querySelector('.current-release')?.textContent.includes('61,947'));
        assert.match(await page.locator('.current-release').innerText(),/0.24145/);
      }
      for(const width of [1440,1024,768,390,320]){
        await page.setViewportSize({width,height:1000});await page.waitForTimeout(100);
        const size=await page.evaluate(()=>({actual:document.documentElement.scrollWidth,viewport:innerWidth}));
        assert.ok(size.actual<=size.viewport+1,`${route} overflow at ${width}: ${size.actual}`);
        if(width===390){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,`${route==='/research'?'research':'landing'}-mobile.png`)});}
      }
    }
    await page.setViewportSize({width:1440,height:1040});
    await page.goto('http://127.0.0.1:5173/');
    await page.getByRole('link',{name:'Explore the guided demo',exact:true}).click();
    await page.getByRole('region',{name:'Guided walkthrough'}).waitFor();
    await page.getByRole('heading',{name:'Meet the available patient state.'}).waitFor();
    for(const width of [390,320]){await page.setViewportSize({width,height:1000});await page.waitForTimeout(100);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));}
    await page.setViewportSize({width:1440,height:1040});
    const before=await page.request.post('http://127.0.0.1:5173/api/patients/RNL-014/mechanisms',{data:{cutoff:90,rate_ml_h:650}});
    const countBefore=(await before.json()).evidence.length;
    await page.getByRole('button',{name:'Next step',exact:true}).click();
    await page.getByRole('heading',{name:'Compare explanations before responses.'}).waitFor();
    await page.locator('.journey-families').waitFor();
    await page.reload();await page.getByRole('heading',{name:'Compare explanations before responses.'}).waitFor();
    await page.locator('.journey-families').waitFor();
    await page.waitForFunction(()=>document.querySelector('.evidence-journey')?.getAttribute('aria-busy')==='false');
    await page.getByRole('button',{name:'Show this area',exact:true}).click();
    await page.screenshot({path:path.join(output,'guided-workspace-desktop.png')});
    for(let i=0;i<4;i++)await page.getByRole('button',{name:'Next step',exact:true}).click();
    await page.getByRole('heading',{name:'Finish with the evidence.'}).waitFor();
    await page.getByRole('heading',{name:/Independent holdout/}).waitFor({timeout:60000});
    await page.getByRole('button',{name:'Finish walkthrough',exact:true}).click();
    assert.equal(await page.locator('.guided-tour').count(),0);
    const after=await page.request.post('http://127.0.0.1:5173/api/patients/RNL-014/mechanisms',{data:{cutoff:90,rate_ml_h:650}});
    assert.equal((await after.json()).evidence.length,countBefore,'Walkthrough navigation must not mutate acquired evidence');
    await page.getByRole('button',{name:'Research guide',exact:true}).click();
    await page.getByRole('heading',{level:1,name:/The reasoning/}).waitFor();
    await page.goBack();
    await page.getByRole('heading',{level:1,name:'A clearer next evidence question.'}).waitFor();
    await page.goto('http://127.0.0.1:5173/workspace?view=mechanisms&patient=RNL-032&minute=90');
    await page.locator('.lab-authority.stale').waitFor();
    await page.reload();await page.locator('.lab-authority.stale').waitFor();
    assert.equal(await page.locator('#patient').inputValue(),'RNL-032');
    await page.goto('http://127.0.0.1:5173/no-such-page');
    await page.getByRole('heading',{name:'This page is not in the workspace.'}).waitFor();
    await page.getByRole('button',{name:'Return home',exact:true}).click();
    await page.getByRole('heading',{level:1,name:/A clearer next question/}).waitFor();
    assert.deepEqual(errors,[]);
    console.log('Complete experience passed: landing, computed hero, source search/filter, live evidence, all document links, guided journey without data mutation, deep links/reload/back, 404, and 1440/1024/768/390/320px layouts.');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
