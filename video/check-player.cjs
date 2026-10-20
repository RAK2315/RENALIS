const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const out=path.resolve(__dirname,'../artifacts/video');
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1100}});
    const errors=[];page.on('pageerror',e=>errors.push(String(e)));
    await page.goto('http://127.0.0.1:5173/artifacts/video/player.html?v=2');
    await page.waitForFunction(()=>document.querySelectorAll('.chapter').length===14&&document.querySelector('video').readyState>=1);
    assert.match(await page.locator('#duration').textContent(),/2 minutes 46 seconds/);
    const duration=await page.locator('video').evaluate(v=>v.duration);
    assert.ok(Math.abs(duration-165.9667)<.15);
    await page.locator('video').evaluate(v=>v.play());
    await page.waitForFunction(()=>document.querySelector('video').currentTime>1);
    const quality=await page.locator('video').evaluate(v=>({decoded:v.webkitDecodedFrameCount,
      audio:v.webkitAudioDecodedByteCount,error:v.error?.message||null}));
    assert.equal(quality.error,null);assert.ok(quality.decoded>0);assert.ok(quality.audio>0);
    await page.locator('.chapter').nth(9).click();
    await page.waitForFunction(()=>document.querySelector('video').currentTime>110);
    await page.getByRole('button',{name:'Music + captions',exact:true}).click();
    await page.waitForFunction(()=>document.querySelector('video').readyState>=2&&document.querySelector('video').currentTime>110);
    assert.match(await page.locator('video').evaluate(v=>v.currentSrc),/music-only/);
    await page.getByRole('button',{name:'Narration + music',exact:true}).click();
    await page.waitForFunction(()=>document.querySelector('video').readyState>=2&&document.querySelector('video').currentTime>110);
    const samples=[];
    for(const player of await page.locator('audio').all()){
      await player.evaluate(p=>p.play());
      await page.waitForFunction(()=>document.querySelector('video').paused);
      const info=await player.evaluate(p=>({src:p.getAttribute('src'),duration:p.duration,error:p.error?.message||null}));
      assert.equal(info.error,null);assert.ok(info.duration>2&&info.duration<8);samples.push(info);
      assert.equal(await page.locator('audio').evaluateAll(players=>players.filter(p=>!p.paused).length),1);
    }
    await page.locator('audio').last().evaluate(p=>p.pause());
    for(const width of [1440,768,390,320]){
      await page.setViewportSize({width,height:1000});
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
      assert.ok(overflow<=1,'Player overflows at '+width+'px');
      await page.screenshot({path:path.join(out,'qa','player-'+width+'.png'),fullPage:true});
    }
    assert.deepEqual(errors,[]);
    const report={status:'passed',duration,quality,samples,chapters:14,
      checks:['Main video decodes picture and sound','Chapter seek','Audio version switching preserves position',
      'Four voice samples play','Single audio source plays at a time','No overflow at 320/390/768/1440px','No script errors']};
    fs.writeFileSync(path.join(out,'player-checks.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report,null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
