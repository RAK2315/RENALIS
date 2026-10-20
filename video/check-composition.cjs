// Regression checks for the actual rendered film, at every spoken concept.
const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const out=path.resolve(__dirname,'../artifacts/video');
(async()=>{
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
    const runtimeErrors=[];page.on('pageerror',e=>runtimeErrors.push(String(e)));
    await page.goto('http://127.0.0.1:5173/video/composition.html');
    await page.waitForFunction(()=>window.__ready,null,{timeout:60000});
    const timeline=JSON.parse(fs.readFileSync(path.join(out,'timeline.json'),'utf8'));
    const captures=JSON.parse(fs.readFileSync(path.join(out,'assets','capture.json'),'utf8'));
    // The narrated numerical example must still be the captured API example.
    // Fail if it changes rather than exporting stale numbers from the screenplay.
    assert.equal(captures.demoResult.rate_ml_h,650);
    assert.equal(captures.demoResult.recommended_measurement.channel,'cardiac_output');
    assert.equal(captures.demoResult.recommended_measurement.offset_minutes,0);
    assert.equal(captures.demoResult.recommended_measurement.decision_value,.0521);
    assert.equal(captures.measuredResult.evidence[0].value,3.74);
    assert.equal(captures.demoResult.observations.filter(r=>r.sbp!==null&&r.quality==='valid').at(-1).sbp,95.9);
    assert.equal(timeline.revision,2,'The old whole-page scrolling film is not the corrected composition');
    const reports=[];
    fs.mkdirSync(path.join(out,'qa','beats'),{recursive:true});
    for(const scene of timeline.scenes){
      for(const beat of scene.beats){
        for(const fraction of [.18,.55,.86]){
          const moment=beat.start+beat.voice_duration*fraction;
          const result=await page.evaluate(t=>window.renderFrame(t,{audit:true}),moment);
          assert.equal(result.scene,scene.id);
          assert.equal(result.concept,beat.key,'Narration and visible concept differ');
          assert.equal(result.screen,beat.screen);
          assert.ok(result.caption,'Spoken phrase needs a visible caption');
          assert.ok(beat.text.includes(result.caption),'Caption must belong to the current utterance');
          assert.deepEqual(result.errors,[],scene.id+'/'+beat.key+': '+result.errors.join('; '));
          for(const media of result.media){
            assert.equal(media.mode,'contain','Screenshots must never be scrolled or cropped');
            const [sx,sy]=media.source,[x,y,w,h]=media.destination,[bx,by,bw,bh]=media.bounds;
            assert.ok(Math.abs(w/h-sx/sy)<.001,'Screenshot aspect ratio changed');
            assert.ok(x>=bx&&y>=by&&x+w<=bx+bw+.01&&y+h<=by+bh+.01,'Panel exceeds its frame');
          }
          reports.push({scene:scene.id,beat:beat.key,time:moment,text_count:result.text.length,media:result.media});
          if(fraction===.55)await page.screenshot({path:path.join(out,'qa','beats',scene.id+'-'+beat.key+'.png')});
        }
      }
    }
    assert.deepEqual(runtimeErrors,[]);
    const report={status:'passed',spoken_concepts:timeline.scenes.reduce((n,s)=>n+s.beats.length,0),
      checked_frames:reports.length,checks:['Narration / concept alignment','Caption / utterance alignment',
      'Text inside safe frame','Complete panel containment','Screenshot aspect ratio','Narrated values match captured API','No browser errors'],frames:reports};
    fs.writeFileSync(path.join(out,'composition-checks.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify({...report,frames:undefined},null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
