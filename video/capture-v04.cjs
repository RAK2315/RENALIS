// Record actual browser interactions against an isolated synthetic database.
const {chromium}=require(process.env.RENALIS_PLAYWRIGHT_PATH||'playwright');
const {spawn,execFileSync}=require('node:child_process');const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'artifacts/submission');fs.mkdirSync(out,{recursive:true});
const port=8013;const child=spawn(path.join(root,'.venv/Scripts/python.exe'),['-m','video.serve_capture',path.join(out,`film-${Date.now()}.sqlite`),String(port)],{cwd:root,windowsHide:true,stdio:'ignore'});
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{let browser;try{
 for(let i=0;i<80;i++){try{if((await fetch(`http://127.0.0.1:${port}/api/health`)).ok)break;}catch{}await wait(150);}
 browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:out,size:{width:1440,height:1000}},reducedMotion:'reduce'});
 await context.route('**/api/**',async route=>{const u=new URL(route.request().url());u.port=String(port);const r=await route.fetch({url:u.toString()});await route.fulfill({response:r});});
 const clips=fs.existsSync(path.join(out,'clips.json'))?JSON.parse(fs.readFileSync(path.join(out,'clips.json'),'utf8')):{};
 for(const [chapter,id] of [[3,'memory'],[5,'memory'],[6,'physiology'],[7,'compare'],[8,'measure'],[9,'measure'],[10,'audit'],[11,'verify'],[12,'verify'],[13,'verify'],[14,'compare'],[15,'transport']]){
  if(process.argv.includes('--chapter')&&chapter!==Number(process.argv[process.argv.indexOf('--chapter')+1]))continue;
  const page=await context.newPage();await page.goto('http://127.0.0.1:5173/workspace?view=investigation&minute=80');
  await page.waitForFunction(()=>document.querySelector('.evidence-journey')?.getAttribute('aria-busy')==='false');
  await page.addStyleTag({content:'.sidebar{display:none!important}.main-shell{margin-left:0!important}.toast{display:none!important}html{scroll-behavior:smooth}'});
  const selector=id==='transport'?'.evidence-journey>section:has-text("Carry a state across several sessions")':`#journey-${id}`;
  await page.locator(selector).scrollIntoViewIfNeeded();await wait(2000);
  if(chapter===3){await page.locator('.journey-steps a').nth(1).click();}
  if(chapter===5){await page.locator('#journey-memory summary').click();await wait(1600);await page.locator('#journey-memory table').scrollIntoViewIfNeeded();}
  if(chapter===6){await page.locator('.physiology-node').first().click();await wait(1700);await page.locator('.physiology-node').nth(3).click();}
  if(chapter===7){await page.locator('.journey-families>button').nth(2).click();await wait(1600);await page.locator('.journey-families>button').nth(3).click();}
  if(chapter===8){await page.getByRole('button',{name:'Relative blood volume',exact:true}).click();await wait(1500);await page.locator('.possible-results summary').click();await page.locator('.possible-result-grid').scrollIntoViewIfNeeded();}
  if(chapter===9){await page.getByRole('combobox',{name:'Acquisition latency',exact:true}).selectOption('5');await wait(2500);await page.locator('.journey-candidates').scrollIntoViewIfNeeded();}
  if(chapter===10){await page.getByRole('textbox',{name:'Review note / symptoms / handover context'}).fill('Fictional walkthrough: review competing explanations, keep uncertainty visible, no clinical action.');await page.getByRole('button',{name:'Save review note',exact:true}).click();}
  if(chapter===11){await page.locator('.release-metrics').scrollIntoViewIfNeeded();}
  if(chapter===12){await page.locator('.journey-caution').scrollIntoViewIfNeeded();}
  if(chapter===13){await page.locator('.release-result').last().scrollIntoViewIfNeeded();}
  if(chapter===14){await page.locator('#clock').evaluate(e=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,95);e.dispatchEvent(new Event('input',{bubbles:true}));});await page.locator('.journey-authority.current_event').waitFor();await page.locator('.journey-authority').scrollIntoViewIfNeeded();}
  if(chapter===15){await page.getByRole('button',{name:'Run conditional transport',exact:true}).click();await page.getByText(/Mass-balance numerical error/).waitFor();await page.locator(selector).scrollIntoViewIfNeeded();}
  await wait(5000);const video=page.video();await page.close();const file=await video.path();const name=`chapter-${String(chapter).padStart(2,'0')}.webm`;fs.copyFileSync(file,path.join(out,name));clips[chapter]=name;console.log('Recorded',chapter,id);
 }
 await context.close();fs.writeFileSync(path.join(out,'clips.json'),JSON.stringify(clips,null,2));
}finally{if(browser)await browser.close();try{execFileSync('taskkill',['/pid',String(child.pid),'/T','/F'],{windowsHide:true,stdio:'ignore'});}catch{}}})().catch(e=>{console.error(e);process.exitCode=1;});
