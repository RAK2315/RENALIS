import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import sharp from 'sharp';

const root=process.cwd(),req=createRequire(path.join(root,'package.json'));
const React=req('react'),{renderToStaticMarkup}=req('react-dom/server'),lucide=req('lucide-react');
const skill='C:/Users/rehtr/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const python='C:/Users/rehtr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const out=path.join(root,'tmp/design-v06'),assets=path.join(root,'public/presentation-assets');
await fs.mkdir(out,{recursive:true});await fs.mkdir(assets,{recursive:true});
const C={bg:'#091522',surface:'#102336',line:'#304b60',white:'#edf5f9',muted:'#a5bbca',jade:'#63dbc0',cyan:'#65c9f1',purple:'#b1a1ff',coral:'#ffa383',paper:'#f1f5f4',ink:'#102b3b'};
const F='Segoe UI',M='Consolas',W=1600,H=900;
const film=JSON.parse(await fs.readFile('public/presentation-assets/evidence.json','utf8'));
const obs=JSON.parse(await fs.readFile('docs/observed-v04.json','utf8'));
const policy=JSON.parse(await fs.readFile('docs/policy-validation-v04.json','utf8'));
const notes=[],all=[];
for(const name of ['workspace','history','after-co','acquire-rbv','audit','physiology']){
 const source=`artifacts/submission-v05/screen-${name}.png`;
 if(await fs.stat(source).catch(()=>null))await fs.copyFile(source,path.join(assets,`interface-${name}.png`));
}
const icons={};
for(const [name,color] of Object.entries({Monitor:C.cyan,Server:C.jade,Database:C.coral,Cpu:C.purple,Brain:C.jade,Activity:C.cyan,History:C.jade,ShieldCheck:C.coral,FileJson:C.cyan,GitBranch:C.purple,Layers:C.purple,Clock:C.coral,HeartPulse:C.purple,Droplets:C.jade,Network:C.coral,SlidersHorizontal:C.cyan,FlaskConical:C.coral,FileCheck2:C.jade,UserRound:C.white,ArrowDownToLine:C.cyan,Hospital:C.muted,BookOpen:C.cyan,RefreshCw:C.jade,ChartNoAxesCombined:C.purple,ScanLine:C.cyan,Atom:C.cyan,CodeXml:C.jade,Link:C.muted})){
 const svg=renderToStaticMarkup(React.createElement(lucide[name],{size:120,color,strokeWidth:1.6}));
 const p=path.join(assets,`icon-${name}.png`);await sharp(Buffer.from(svg)).resize(160,160).png().toFile(p);icons[name]=await fs.readFile(p);
}
function txt(s,t,x,y,w,h,size=28,color=C.white,bold=false,font=F){const a=s.shapes.add({geometry:'textbox',name:t.slice(0,60),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.insets=0;a.text.style={typeface:font,fontSize:size,color,bold};return a;}
function box(s,x,y,w,h,fill=C.surface,line=C.line,r=16,dashed=false){return s.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:w,height:h},borderRadius:r,fill,line:{fill:line,width:1.6,style:dashed?'dashed':'solid'}});}
function rule(s,x,y,w,color=C.line){return s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width:1.2}});}
async function pic(s,file,x,y,w,h,fit='contain'){const b=await fs.readFile(file);return s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit,alt:path.basename(file)});}
function icon(s,name,x,y,size=42){const b=icons[name];s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',position:{left:x,top:y,width:size,height:size},fit:'contain',alt:`Lucide ${name}`});}
function base(p,title,sub='',light=false){const s=p.slides.add();s.background.fill=light?C.paper:C.bg;s._light=light;
 txt(s,title,64,45,1470,85,52,light?C.ink:C.white,true);if(sub)txt(s,sub,66,139,1465,66,25,light?'#516f7d':C.muted);
 rule(s,64,829,1472,light?'#cbd8da':C.line);txt(s,'RENALIS  /  Team Sigmoid  /  Research prototype',64,849,1300,25,17,light?'#5b7884':C.muted);txt(s,String(p.slides.items.length).padStart(2,'0'),1480,847,60,30,19,light?C.ink:C.white,false,M);return s;}
function note(s,str){s.speakerNotes.text=str;notes.push(str);}
function node(s,title,sub,x,y,w=300,h=145,ico='Cpu',color=C.cyan){const sh=box(s,x,y,w,h);icon(s,ico,x+18,y+20,40);txt(s,title,x+72,y+18,w-86,55,24,C.white,true);txt(s,sub,x+20,y+81,w-36,h-86,19,C.muted);return sh;}
function wire(s,a,b,label='',from='right',to='left',color=C.cyan,dashed=false,labelPos=null){const l=s.shapes.connect(a,b,{fromSide:from,toSide:to,kind:'straight',line:{fill:color,width:2.3,style:dashed?'dashed':'solid'},tail:{type:'triangle',width:'med',length:'med'}});if(labelPos)txt(s,label,...labelPos,18,color,false,M);return l;}
function zone(s,title,x,y,w,h,color=C.line,dashed=false){box(s,x,y,w,h,'none',color,20,dashed);txt(s,title,x+20,y+12,w-35,28,18,color===C.line?C.muted:color,true,M);}
function callout(s,t,x,y,w=1400,color=C.jade){txt(s,t,x,y,w,70,27,color,true);}
function metric(s,value,label,x,y,color=C.jade,w=340,size=74){txt(s,value,x,y,w,100,size,color,true);txt(s,label,x,y+110,w,90,25,s._light?'#516f7d':C.muted);}
function arrowAt(s,x1,y1,x2,y2,color=C.cyan,dashed=false){return s.shapes.add({geometry:'connector',kind:'straight',position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.abs(x2-x1),height:Math.abs(y2-y1),horizontalFlip:x2<x1,verticalFlip:y2<y1},line:{fill:color,width:2.3,style:dashed?'dashed':'solid'},tail:{type:'triangle',width:'med',length:'med'}});}
function simpleChart(s,categories,series,x,y,w,h,{type='bar',format='0.000',min=0,max,stack=false,axisTitle='',legend=false}={}){
 const ink=s._light?C.ink:C.white,grid=s._light?'#d2dfe1':C.line;
 const c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},categories,series,chartFill:'none',plotAreaFill:'none',hasLegend:legend,legend:{position:'bottom',textStyle:{fontSize:21,color:ink}},barOptions:{grouping:stack?'stacked':'clustered',direction:'column',gapWidth:85},
  dataLabels:{showValue:type==='bar',numberFormatCode:format,numberFormatSourceLinked:false,position:stack?'center':'outEnd',textStyle:{fontSize:24,color:ink}},
  xAxis:{textStyle:{fontSize:22,color:ink},line:{fill:grid,width:1}},yAxis:{min,max,numberFormatCode:stack?'0%':max<=1?'0.00':'0.0',textStyle:{fontSize:20,color:ink},majorGridlines:{fill:grid,width:1},title:axisTitle?{text:axisTitle,textStyle:{fontSize:21,color:ink}}:undefined}});
 applyPresentationChartFont(c,{fontFamily:F});return c;
}

// Architecture views use native nodes and attached connectors.
function containers(p){const s=base(p,'System containers','Current local implementation. Browser requests stay separate from offline evaluation.');
 zone(s,'LOCAL RESEARCH WORKSPACE',270,218,1260,550);
 const user=node(s,'User','Research review\nAcquire + save',62,325,185,175,'UserRound');
 const ui=node(s,'React workspace','TypeScript + Vite\nBrowser :5173',300,325,270,175,'Monitor');
 const api=node(s,'FastAPI service','Python + NumPy\nHTTP JSON :8000',685,325,295,175,'Server');
 const engine=node(s,'Twin + planner','History, state, hypotheses\nInformation + action loss',1090,265,405,160,'Cpu');
 const db=node(s,'SQLite evidence store','Requests, readings, corrections\nSaved experiment revisions',1090,482,405,160,'Database');
 wire(s,user,ui,'', 'right','left',C.cyan);wire(s,ui,api,'','right','left',C.cyan,false,[596,367,80,25]);txt(s,'HTTP\nJSON',590,345,90,65,19,C.cyan,false,M);
 wire(s,api,engine,'','right','left',C.purple);wire(s,api,db,'','right','left',C.coral);
 txt(s,'Function calls',991,249,120,33,16,C.purple,false,M);txt(s,'Transactions',982,595,120,30,16,C.coral,false,M);
 txt(s,'Synthetic inputs',314,554,290,32,23,C.jade,true);txt(s,'Authored BP/device replay\nSix preceding sessions\nExplicit acquisition fixtures',314,596,300,122,22,C.muted);
 txt(s,'Published artifacts',674,556,350,32,23,C.cyan,true);txt(s,'Aggregate JSON, PDF/PPTX\nFictional FHIR collection\nVersioned source + model card',674,596,358,122,22,C.muted);
 callout(s,'Observed HEMOBP modeling runs offline and supplies evaluation reports, not the synthetic twin state.',64,779,1465,C.muted);
 note(s,'Current implementation. Sources: backend/app.py PROJECT_DOCUMENTS, DB schema and endpoints; backend/model.py, history.py, mechanisms.py, discrimination.py, insights.py; src/api.ts; vite.config.ts. API functions run in one Python process, not separate microservices. SQLite is a local database. No NGINX, PostgreSQL, container orchestration, cloud deployment, authentication or live hospital integration is claimed.');return s;}
function components(p){const s=base(p,'Inference components','One API process orchestrates distinct model and evidence responsibilities.');
 const hist=node(s,'History learner','history.py\nPrior + shrinkage + lineage',64,268,315,154,'History');
 const state=node(s,'Particle state','model.py / mechanisms.py\nAvailable history only',485,268,330,154,'Layers');
 const info=node(s,'Discriminator','discrimination.py\nExpected entropy reduction',953,230,570,150,'GitBranch',C.purple);
 const value=node(s,'Action comparison','mechanisms.py\nWaiting + failure + burden',953,439,570,150,'SlidersHorizontal');
 const insight=node(s,'Explanation layer','insights.py\nNoisy ranges + result previews',485,560,330,150,'ScanLine');
 const ledger=node(s,'Released evidence','app.py + SQLite\nTime, quality and corrections',64,560,315,150,'Database');
 wire(s,hist,state,'','right','left',C.jade);wire(s,state,info,'','right','left',C.purple);wire(s,state,value,'','right','left',C.cyan);wire(s,state,insight,'','bottom','top',C.jade);wire(s,ledger,state,'','top','left',C.coral);txt(s,'Assimilation',85,480,180,32,19,C.coral,false,M);
 txt(s,'Two objectives share the posterior',954,644,555,36,28,C.white,true);txt(s,'Information scores do not substitute for\nmodeled action-loss reduction.',954,696,570,72,25,C.muted);
 note(s,'Source modules: backend/history.py learns preceding-session prior; model.py performs replay state estimation and forecast; mechanisms.py defines four families, assimilation, observation equations, projections and action loss; discrimination.py selects the next discriminator; insights.py summarizes predictions. Evidence availability and correction rules are implemented in app.py. The diagram shows responsibilities inside one service, not independent services.');return s;}
function sequence(p){const s=base(p,'Acquisition request sequence','Planning cannot inspect the fixture result before an explicit acquisition.');
 const names=[['Browser','React'],['API','FastAPI'],['Evidence','SQLite'],['Inference','NumPy'],['Device boundary','Synthetic fixture']];
 const xs=[180,480,780,1080,1380];
 names.forEach((n,i)=>{node(s,n[0],n[1],xs[i]-115,220,230,112,['Monitor','Server','Database','Cpu','Activity'][i]);s.shapes.add({geometry:'line',position:{left:xs[i],top:337,width:0,height:418},fill:'none',line:{fill:C.line,width:1.5,style:'dashed'}});});
 const rows=[ [0,1,'1  POST investigation',C.cyan],[1,2,'2  Read evidence',C.coral],[2,1,'3  Released observations',C.coral],[1,3,'4  Recompute posterior and next discriminator',C.purple],[3,1,'5  Recommendation and predicted ranges',C.purple],[1,0,'6  Investigation response',C.jade],[0,1,'7  POST measurements',C.cyan],[1,4,'8  Acquire selected channel',C.coral],[4,1,'9  Actual value or failure',C.coral],[1,2,'10 Append request + reading',C.coral] ];
 rows.forEach(([a,b,label,color],i)=>{const y=362+i*42;arrowAt(s,xs[a],y,xs[b],y,color);txt(s,label,Math.min(xs[a],xs[b])+14,y-27,Math.abs(xs[b]-xs[a])-15,28,17,color,false,M);});
 callout(s,'The next investigation reads the appended evidence and recomputes both support and the next question.',64,779,1465,C.muted);
 note(s,'Sources: backend/app.py POST /api/patients/{pid}/investigation and /measurements; backend/measurement_fixtures.py; backend/discrimination.py. Released evidence is gated by available_minute, observed_minute and quality. Failures are retained as acquisition records. Fixture output never enters the planner. The final recomputation occurs on the subsequent investigation request.');return s;}
function planner(p){const s=base(p,'Adaptive measurement planning','Concrete synthetic replay at minute 90. Each acquired result changes the next question.');
 const post=node(s,'Posterior after CO','3.74 L/min acquired\nCardiac 51.7% / volume 46.2%',64,258,340,170,'Layers');
 const predict=node(s,'Conditional predictions','RBV median 83.87% vs 87.81%\nSensor noise SD 1.00%',485,258,450,170,'ScanLine');
 const rank=node(s,'Feasible measurement','Expected pair information\nRBV 0.39378 bits',1038,258,485,170,'GitBranch');
 const update=node(s,'Updated posterior','Volume 66.9% / cardiac 31.8%\nResidual ambiguity retained',64,576,340,170,'RefreshCw');
 const append=node(s,'Ledger append','Observed time + release time\nQuality, cost and source',485,576,450,170,'Database');
 const acquire=node(s,'Acquire actual RBV','Fixture returns 85.0%\nResult unknown until requested',1038,576,485,170,'Activity');
 wire(s,post,predict,'','right','left',C.purple);wire(s,predict,rank,'','right','left',C.cyan);wire(s,rank,acquire,'','bottom','top',C.coral);wire(s,acquire,append,'','left','right',C.coral);wire(s,append,update,'','left','right',C.jade);
 txt(s,'Equipment, timing, guards, failures and previous acquisitions constrain the candidate set.',65,468,1460,55,27,C.muted);
 callout(s,'No useful discriminator is a valid stop state. Repeated readings currently assume independent noise.',64,778,1480,C.muted);
 note(s,'Actual demonstration snapshots: artifacts/submission-v05/film-data.json, before, afterCO and afterRBV. Implementation: backend/discrimination.py. Values are authored conditional model quantities, not diagnostic probabilities or validated device statistics. Pair information ranks feasible observations; action value is a separate objective. Independent sequential-policy validation remains planned.');return s;}
function persistence(p){const s=base(p,'Evidence persistence and lineage','Logical relationships in SQLite. Correction appends preserve earlier replay cutoffs.');
 const acq=node(s,'acquisitions','status / request_cutoff\navailable_minute / measurement_id',64,250,410,175,'Activity');
 const meas=node(s,'measurements','observed_minute / available_minute\nquality / noise_sd / supersedes',592,250,420,175,'Database');
 const runs=node(s,'lab_runs','revision / settings / result\nImmutable saved JSON snapshot',1124,250,410,175,'FileJson');
 wire(s,acq,meas,'','right','left',C.coral);wire(s,meas,runs,'','right','left',C.jade);txt(s,'reading',490,309,98,30,16,C.coral,false,M);txt(s,'snapshot',1024,309,110,30,16,C.jade,false,M);
 const corr=node(s,'Appended correction','supersedes + reason\nEarlier reading stays in history',592,567,420,170,'History');wire(s,corr,meas,'','top','bottom',C.purple);txt(s,'Logical self-link',830,494,290,32,19,C.purple,false,M);
 node(s,'reviews','patient / cutoff / note\nReview context',64,567,410,170,'FileCheck2');node(s,'branches','cutoff / rate / profile / result\nSaved hypothetical comparison',1124,567,410,170,'GitBranch');
 callout(s,'Quality excludes artifacts from inference. Availability gates replay. Saved revisions retain their evidence.',64,778,1465,C.muted);
 note(s,'Source: backend/app.py CREATE TABLE and correction/save endpoints. Links are logical application relationships, not a claim of database-enforced foreign keys. Saved lab_runs stores result JSON and revision. Corrections use supersedes and correction_reason; archived rows and previous immutable results remain distinguishable.');return s;}
function evaluation(p){const s=base(p,'Evaluation boundaries','Three different evidence questions retain separate data, endpoints and claims.');
 zone(s,'OBSERVED HEMOBP BENCHMARK',64,229,1470,235,C.cyan);
 const raw=node(s,'Versioned public tables','HEMOBP v3 / CC BY 4.0\nClock alignment assumption',86,285,345,145,'FileJson');
 const audit=node(s,'Audited cohort','Elapsed checks / canonical units\nPreceding-session inputs only',510,285,420,145,'ShieldCheck');
 const split=node(s,'Patient-disjoint splits','Fit 563 / calibration 141 / test 176\nMAE, calibration and workload',1033,285,478,145,'ChartNoAxesCombined');
 wire(s,raw,audit,'','right','left',C.cyan);wire(s,audit,split,'','right','left',C.cyan);
 zone(s,'INDEPENDENT SYNTHETIC POLICY STUDY',64,506,708,249,C.coral);zone(s,'CURRENT SEQUENTIAL SELECTOR',821,506,713,249,C.purple,true);
 icon(s,'FlaskConical',89,561,48);txt(s,'192 cases / 768 policy records',157,558,579,45,29,C.white,true);txt(s,'Separate scoring futures and one-acquisition budget.\nDecision value does not outperform fixed cuff overall.',88,627,647,94,25,C.muted);
 icon(s,'GitBranch',846,561,48);txt(s,'Software checks + real UI replay',914,558,585,45,29,C.white,true);txt(s,'Multi-acquisition effectiveness remains unevaluated.\nA future study needs predeclared correlated noise.',847,627,650,94,25,C.muted);
 note(s,'Observed sources: docs/observed-v04.json, scripts/evaluate_observed_v04.py, HEMOBP v3 DOI10.6084/m9.figshare.6260654.v3. Empirical8h cross-table shift requires confirmation. Independent study: docs/policy-validation-v04.json,192 cases,768records, one acquisition per policy. Current sequential discriminator is not validated by that earlier study.');return s;}

const a=Presentation.create({slideSize:{width:W,height:H}});
containers(a);components(a);sequence(a);planner(a);persistence(a);evaluation(a);
const p=Presentation.create({slideSize:{width:W,height:H}});let s;

// 01: full-bleed generated conceptual artwork with editable foreground type.
s=p.slides.add();s.background.fill=C.bg;await pic(s,path.join(assets,'renal-twin-cover.png'),0,0,W,H,'cover');
txt(s,'RENALIS',75,190,800,140,104,C.white,true);txt(s,'Evidence-aware\ndialysis digital twin',79,360,700,150,48,C.white,true);txt(s,'Competing explanations.\nA better next measurement question.',80,559,660,100,31,C.muted);txt(s,'TEAM SIGMOID',80,742,650,45,24,C.jade,true);txt(s,'Rehaan / JSS University, Noida',80,790,670,45,24,C.white);
note(s,'Team details supplied by entrant. Research prototype. Conceptual generated cover illustration, not a real device or patient. Built-in patients/device streams are fictional. Artwork prompt and provenance: public/presentation-assets/provenance.json.');

// 02: actual measured trace plus the research question.
s=base(p,'One BP trace can support several explanations','An observation can narrow uncertainty without identifying a unique physiological cause.',true);
const measured=film.before.observations.filter(o=>o.sbp!==null);
simpleChart(s,measured.map(o=>`${o.minute}`),[{name:'Observed synthetic SBP',values:measured.map(o=>o.sbp),line:{fill:'#147d83',width:4},marker:{symbol:'circle',size:6,fill:'#147d83'}}],65,246,970,460,{type:'line',min:60,max:160,axisTitle:'SBP (mmHg)'});
txt(s,'Elapsed session minutes',375,730,620,40,23,'#516f7d');txt(s,'The missing variable',1120,268,400,45,32,C.ink,true);txt(s,'Is the pressure change\nmore compatible with\nvolume, vascular or\ncardiac response?',1120,347,400,230,33,C.ink);txt(s,'Synthetic replay at minute 90',1120,640,410,70,23,'#516f7d');
note(s,'Trace contains actual non-null available observations from film-data.json before cutoff90. No interpolation beyond the released data is shown. Clinical motivation: KDIGO BP and Volume Management in Dialysis Conference Report2020, https://kdigo.org/wp-content/uploads/2017/02/KDIGO-BP-Volume-Management-in-Dialysis-Conference-Report.pdf . Competing mechanisms remain authored research models.');

// 03: actual product, without a fake screenshot.
s=base(p,'The research workspace','One evidence cutoff connects the patient replay, hypotheses and acquisition history.');
await pic(s,path.join(assets,'interface-workspace.png'),440,224,1095,586);
['Learn','Understand','Compare','Ask','Review','Verify'].forEach((v,i)=>{txt(s,String(i+1).padStart(2,'0'),67,239+i*91,65,50,27,C.jade,false,M);txt(s,v,145,235+i*91,280,55,34,C.white,true);});
note(s,'Actual captured interface on an isolated synthetic database. Source: src/EvidenceJourney.tsx and video/submission_v05/capture.cjs. Patient RNL-014 at minute 90. Six journey sections are implemented, not a UI mockup.');

// 04: native architecture, same visual language as the standalone document.
containers(p);

// 05: history learning flow and its source provenance.
s=base(p,'The prior comes from preceding sessions','Six completed synthetic sessions inform refill estimation before the current replay.');
const sessions=node(s,'Session trajectories','Raw BP + machine settings\nCompleted before current start',65,300,400,180,'History');const learned=node(s,'Likelihood fit','Refill / compensation grid\nUncertainty floor + shrinkage',597,300,410,180,'Brain');const prior=node(s,'Patient prior','Estimate + uncertainty\nSource digest and fit lineage',1140,300,394,180,'Layers');
wire(s,sessions,learned,'','right','left',C.jade);wire(s,learned,prior,'','right','left',C.jade);
txt(s,'What the interface exposes',67,571,600,50,32,C.white,true);txt(s,'Per-session fits, the fitted prior and the forward-session ablation make the learner inspectable.',67,641,1000,100,31,C.muted);metric(s,'6','preceding completed sessions',1160,570,C.jade,340,92);
note(s,'Source: backend/history.py and history_fixtures.py. History contains authored synthetic sessions. Shrinkage, source lineage and ablation expose assumptions; no clinical parameter identification is established.');

// 06: editable compartment diagram.
s=base(p,'The physiological model','Estimated compartments connect removal, refill and family-specific pressure response.');
const tissue=node(s,'Tissue fluid','Estimated compartment',65,300,390,170,'Droplets');const plasma=node(s,'Circulating volume','Estimated compartment',605,300,390,170,'Droplets');const uf=node(s,'Fluid removal','Observed machine setting',1145,300,390,170,'Activity');wire(s,tissue,plasma,'','right','left',C.jade);wire(s,plasma,uf,'','right','left',C.cyan);txt(s,'Refill',481,315,110,50,25,C.jade);txt(s,'Removal',1011,315,130,50,25,C.cyan);
const response=node(s,'Pressure response','Volume sensitivity + compensation\nFour authored response families',605,604,390,165,'HeartPulse');wire(s,plasma,response,'','bottom','top',C.purple);
txt(s,'Current BP readings\nconstrain the hidden state.',68,614,450,100,31,C.muted);txt(s,'A model state estimate\ncan remain ambiguous.',1130,614,405,100,31,C.muted);
note(s,'Source: backend/model.py advance/pressure and backend/mechanisms.py infer/project/sensor_prediction. The schematic is a computational compartment model, not an anatomical diagram or a clinically validated whole-body simulator.');

// 07: actual competing-family evidence, rather than a paragraph list.
s=base(p,'Four families fit the available past','Similar fit does not imply the same projected response.');
const defs=[['volume','Volume / refill','Droplets',C.jade],['vascular','Vascular response','Network',C.coral],['cardiac','Cardiac response','HeartPulse',C.purple],['mixed','Mixed response','Layers',C.cyan]];
defs.forEach(([id,label,ico,color],i)=>{const f=film.before.families.find(f=>f.id===id),x=65+i*376;icon(s,ico,x,260,65);txt(s,label,x,353,350,65,29,color,true);txt(s,`${(f.weight*100).toFixed(1)}%`,x,430,350,105,65,C.white,true);txt(s,'relative model support',x,538,350,55,23,C.muted);rule(s,x,609,332);txt(s,`${f.fit_rmse_mm_hg.toFixed(2)} mmHg`,x,640,340,55,36,C.white,true);txt(s,'past-fit RMSE',x,701,340,50,23,C.muted);});
note(s,'Values: film-data.json before, Meera/RNL-014 minute 90, hypothetical constant650mL/h. Each family has48 particles. Weights quantify relative compatibility inside this model bank, not diagnostic probabilities. Physiology outside the bank may be absent.');

// 08: actual acquisition evidence.
s=base(p,'Cardiac output narrows the disagreement','An acquired low-output result still fits both volume depletion and limited cardiac response.');
metric(s,'3.74','L/min acquired cardiac output',66,285,C.cyan,365,91);txt(s,'Cardiac 51.7%\nVolume 46.2%',67,550,360,130,39,C.white,true);txt(s,'Current model support',67,713,360,45,23,C.muted);await pic(s,path.join(assets,'interface-after-co.png'),465,235,1070,560);
note(s,'Actual synthetic acquisition and posterior: film-data.json afterCO and interface capture. Source backend/measurement_fixtures.py. Output can fall with depleted circulation or limited modeled cardiac response. This reading does not identify a unique cause.');

// 09: native chart preserving all family weights.
s=base(p,'How the acquired evidence changes support','The planner recomputes the full bank after each result. Residual ambiguity remains visible.',true);
simpleChart(s,['BP only','After CO 3.74','After RBV 85.0'],defs.map(([id,label,ico,color])=>({name:label,values:['before','afterCO','afterRBV'].map(k=>film[k].families.find(f=>f.id===id).weight),fill:color,...(['vascular','mixed'].includes(id)?{dataLabelOverrides:[{idx:1,showValue:false},{idx:2,showValue:false}]}:{})})),80,260,1440,480,{stack:true,format:'0.0%',max:1,legend:true,axisTitle:'Relative model support'});
txt(s,'Support is conditional on the authored model bank. It is not a probability of clinical diagnosis.',88,773,1430,47,25,'#516f7d');
note(s,'All four series and all three states are literal values from film-data.json. Percentages may have minor rounding error. New editable chart and embedded workbook snapshot preserve the source values. Cardiac51.66% / volume46.17% afterCO; volume66.93% / cardiac31.78% afterRBV.');

// 10: an editable measurement-range figure.
s=base(p,'Why the next measurement is relative blood volume','The remaining families predict different noisy RBV distributions. Their ranges still overlap.');
const scale=v=>420+(v-80)/12*1050;
for(const [i,label,lo,mid,hi,color] of [[0,'Volume / refill',81.25,83.87,86.40,C.jade],[1,'Cardiac response',84.40,87.81,90.53,C.purple]]){const y=305+i*175;txt(s,label,65,y-2,330,60,32,color,true);rule(s,scale(lo),y+22,scale(hi)-scale(lo),color);box(s,scale(mid)-5,y-2,10,48,color,color,0);txt(s,`10th–90th: ${lo.toFixed(2)}–${hi.toFixed(2)}%`,970,y+66,550,45,23,C.muted,false,M);txt(s,`Median ${mid.toFixed(2)}%`,420,y+66,550,60,29,color,true);}
rule(s,420,668,1050);[80,82,84,86,88,90,92].forEach(v=>txt(s,`${v}`,scale(v)-12,687,70,35,22,C.muted,false,M));txt(s,'% of starting blood volume',730,738,700,50,26,C.white);
txt(s,'0.39378 bits',66,680,330,64,43,C.cyan,true);txt(s,'expected pair information',66,747,340,60,22,C.muted);
note(s,'AfterCO snapshot adaptive planner. Volume median 83.87, 10th–90th81.25–86.40; cardiac87.81,84.40–90.53. Includes declared sensor SD 1.00% of start. Expected pair information0.39378 bits vs cuff0.00004 bits. Native range diagram represents displayed quantiles, not a fitted Gaussian curve. It does not promise resolution or treatment benefit.');

// 11: actual outcome and honest uncertainty.
s=base(p,'The device returns 85.0%','The acquired RBV shifts the balance toward volume / refill without eliminating cardiac support.');
await pic(s,path.join(assets,'interface-acquire-rbv.png'),65,235,1060,565);metric(s,'66.9%','volume / refill support',1175,261,C.jade,360,76);metric(s,'31.8%','cardiac response support',1175,537,C.purple,360,76);
note(s,'Actual synthetic RBV85.0 result from film-data.json afterRBV. No manually chosen resolving5.4 is required. The newly recomputed planner may continue or stop depending on feasible expected separation and guards. This example remains ambiguous.');

// 12: two objective formulas as a semantic comparison diagram.
s=base(p,'Information and action value answer different questions','Both use current beliefs, but only one includes the modeled consequence of a decision.');
icon(s,'GitBranch',65,270,62);txt(s,'Information',65,367,660,65,47,C.purple,true);txt(s,'Expected uncertainty reduction',65,464,660,60,30,C.white);txt(s,'Which feasible observation could\nseparate the remaining explanations?',65,562,660,110,32,C.muted);txt(s,'Units: bits',65,729,660,50,25,C.purple,false,M);
icon(s,'SlidersHorizontal',865,270,62);txt(s,'Action value',865,367,665,65,47,C.cyan,true);txt(s,'Expected modeled loss reduction',865,464,665,60,30,C.white);txt(s,'Could the result improve the comparison\nafter waiting, failure and burden?',865,562,665,110,32,C.muted);txt(s,'Units: declared research loss',865,729,665,50,25,C.cyan,false,M);
note(s,'Source: backend/discrimination.py and mechanisms.py measurement_value. Information bits and action loss are separate units and should not be subtracted from each other. A useful discriminator can have nonpositive net action value. Clinical utility has not been elicited or validated.');

// 13: evidence sequence with audit screenshot.
s=base(p,'Every observation has a lineage','Failures, artifacts and corrections remain distinguishable from evidence used in inference.');
await pic(s,path.join(assets,'interface-audit.png'),650,245,885,525);
for(const [i,title,body] of [[0,'Observe','Record physiological time and quality.'],[1,'Release','Make evidence available after delay.'],[2,'Correct','Append a reason and supersedes link.'],[3,'Save','Keep revision and evidence in a snapshot.']]){txt(s,String(i+1).padStart(2,'0'),66,255+i*134,60,55,28,C.coral,false,M);txt(s,title,155,248+i*134,440,48,32,C.white,true);txt(s,body,155,302+i*134,450,73,24,C.muted);}
note(s,'Source: backend/app.py measurements, acquisitions and lab_runs schema; corrections endpoint. Observation and availability time have different meanings. Artifact values are retained but excluded from assimilation. Saved report revisions do not change after later corrections.');

// 14: actual observed-data MAE, all baseline categories retained.
s=base(p,'History adds a small retrospective signal','HEMOBP v3. 61,947 test windows from 176 patients, with no patient overlap between splits.',true);
simpleChart(s,['Persistence','Dynamic','Demographics\n+ dynamic','History\n+ dynamic'],[{name:'Test MAE',values:obs.models.map(m=>m.mae_mm_hg),fill:'#147d83',points:[{idx:3,fill:'#183e56'}]}],66,255,1060,495,{axisTitle:'MAE (mmHg)',max:14});
metric(s,'−0.1665','mmHg paired history increment',1180,288,'#147d83',350,58);txt(s,'95% patient-cluster interval\n[−0.2298, −0.1099]',1180,548,350,120,26,C.ink);txt(s,'Clinical importance\nremains unestablished.',1180,715,350,88,27,'#516f7d');
note(s,'Source docs/observed-v04.json models and history_increment. History increment compares history+dynamic with demographics+dynamic on the same cohort. MAE12.194,11.356,11.328,11.161mmHg. Empirical clock shift and exclusions constrain interpretation. DOI10.6084/m9.figshare.6260654.v3; https://www.nature.com/articles/s41597-019-0319-8 .');

// 15: observed limitations are explicit and visual.
s=base(p,'The evaluation still has material limits','A retrospective prediction result does not establish physiological identification or clinical benefit.');
metric(s,'61.25%','event sensitivity',66,255,C.cyan,440);metric(s,'13.51%','positive predictive value',600,255,C.coral,440);metric(s,'86.74%','coverage of nominal 90% range',1130,255,C.purple,420);
rule(s,65,505,1467);txt(s,'Clock alignment',66,561,430,55,35,C.white,true);txt(s,'The empirical 8-hour shift needs\nindependent confirmation.',66,639,440,110,27,C.muted);txt(s,'Cohort exclusions',600,561,450,55,35,C.white,true);txt(s,'2,516,989 of 4,366,298 packets\nmatch the declared checks.',600,639,450,110,27,C.muted);txt(s,'Endpoint scope',1130,561,420,55,35,C.white,true);txt(s,'Next measured BP differs from\ncontinuous hypotension.',1130,639,420,110,27,C.muted);
note(s,'Source docs/observed-v04.json audit, interval and event_model. Endpoint requires currently non-low SBP and next distinct measured reading within5–35minutes. Missing events, false alerts and undercoverage remain visible. Raw observed data is not redistributed.');

// 16: negative policy evidence stays legible.
s=base(p,'Decision value does not beat cuff overall','Independent synthetic holdout: 192 cases, four policies and one acquisition per policy.',true);
simpleChart(s,['No observation','Fixed cuff','Information gain','Decision value'],[{name:'Mean regret',values:policy.summaries.map(v=>v.mean_regret),fill:'#b96d4d',points:[{idx:1,fill:'#147d83'}]}],66,257,1060,495,{axisTitle:'Mean physiology regret',max:0.30,format:'0.00000'});
txt(s,'0.22170',1180,310,365,95,64,'#147d83',true);txt(s,'fixed cuff',1180,412,350,55,27,'#516f7d');txt(s,'0.24145',1180,531,365,95,64,'#b96d4d',true);txt(s,'decision value',1180,633,350,55,27,'#516f7d');txt(s,'Lower is better.',1180,738,350,50,27,C.ink,true);
note(s,'Source docs/policy-validation-v04.json. Mean regret0.23078no observation,0.22170fixed cuff,0.24472information gain,0.24145decision value. Earlier one-acquisition study. It does not validate current sequential selection. Paired decision-value delta vs cuff0.01975, interval[-0.00981,0.05996]. All768records and the metric amendment are retained.');

// 17: conditions and resulting authority states.
s=base(p,'Authority changes with evidence quality','The service withholds scenario authority when the replay cannot support it.');
const guards=[['Current low BP','Current event is already present.\nNo advance-warning claim.','HeartPulse'],['Stale or missing BP','Refresh the available evidence\nbefore comparing scenarios.','Clock'],['Completed session','Do not compare new removal\nprofiles after session completion.','FileCheck2'],['Contradictory evidence','Show poor fit and residual\nuncertainty in the model bank.','ShieldCheck']];
guards.forEach(([title,body,ico],i)=>{const x=65+(i%2)*790,y=265+Math.floor(i/2)*260;icon(s,ico,x,y,55);txt(s,title,x+82,y-1,610,55,34,C.white,true);txt(s,body,x+82,y+76,610,110,28,C.muted);});
note(s,'Sources backend/app.py scenario guards, model.py alert states, mechanisms.py support_state, tests/test_model.py and test_discrimination.py. Current events, stale evidence and session completion block ranked scenario mutations. Poor model fit remains explicit. These are software guards, not a medical alarm specification.');

// 18: implemented extensions and clear external boundary.
s=base(p,'Extensions expose the next integration boundary','Current exports and transport experiments remain inspectable research components.');
const comp=node(s,'Current compartments','Evidence-weighted volume state',65,290,410,155,'Droplets');const transport=node(s,'Longitudinal transport','Authored intake / output\nMass-balance checks',590,290,420,155,'RefreshCw');wire(s,comp,transport,'','right','left',C.jade);
node(s,'Synthetic FHIR R4','Patient / Device / BP Observation\nReference + unit checks',65,576,945,165,'FileJson');zone(s,'FUTURE EXTERNAL INTEGRATION',1125,248,409,492,C.muted,true);icon(s,'Hospital',1275,311,90);txt(s,'Clinical systems',1161,452,350,60,35,C.white,true);txt(s,'Live EHR access, governance\nand ABDM conformance\nrequire independent work.',1161,553,350,140,26,C.muted);arrowAt(s,1015,652,1122,652,C.muted,true);
note(s,'Implemented backend/longitudinal.py, backend/fhir.py and app.py /longitudinal and /fhir. Compartment transport does not predict future BP or identify renal function. FHIR R4 collection is fictional and not certified for ABDM. Source standard https://hl7.org/fhir/R4/observation.html and https://nrces.in/ndhm/fhir/r4/ . Future integration is dashed and not an implemented connection.');

// 19: actual validation gates, ordered by dependency.
s=base(p,'The next evidence gates','The strongest next work tests the assumptions that limit interpretation.');
const gates=[['Source timing','Confirm HEMOBP clocks\nand reproduce the cohort.'],['Human interpretation','Test whether reviewers\nunderstand ambiguity.'],['Matched physiology','Calibrate the model against\npaired clinical measurements.'],['Independent policies','Predeclare multi-acquisition\nbudgets and correlated noise.'],['External silent study','Measure calibration and\nworkflow burden externally.']];
gates.forEach(([title,body],i)=>{const x=64+i*300;txt(s,String(i+1).padStart(2,'0'),x,276,250,100,72,i<2?C.jade:C.cyan,true,M);rule(s,x,412,262);txt(s,title,x,462,267,90,30,C.white,true);txt(s,body,x,588,267,147,25,C.muted);});
note(s,'Proposed work, not completed studies. Sources: docs/clinical-study-protocol.md, data-capture-schema.json, implementation-decisions-v04.md and model-card.md. Clinical collaborators, approvals, enrollment and prospective impact are not claimed.');

// 20: closing and a compact, legible source index.
s=base(p,'A clearer next evidence question','RENALIS makes the model disagreement, the next observation and the remaining uncertainty visible.');
txt(s,'See the actual\n20-minute demonstration',66,262,880,165,60,C.white,true);txt(s,'youtu.be/ZcWNYMtM1tI',69,493,960,65,36,C.jade,false,M);txt(s,'github.com/RAK2315/RENALIS',69,596,1070,65,36,C.cyan,false,M);
txt(s,'Team Sigmoid',1150,283,400,60,35,C.white,true);txt(s,'Rehaan\nJSS University, Noida',1150,370,400,105,27,C.muted);txt(s,'Evidence and methods',1150,554,400,45,27,C.white,true);txt(s,'Model card + source modules\nObserved and policy reports\nResearch dossier + study protocol',1150,620,400,124,23,C.muted);
note(s,'Public source https://github.com/RAK2315/RENALIS and unlisted video https://youtu.be/ZcWNYMtM1tI . Sources and interpretations are in per-slide notes and README, docs/model-card.md, docs/observed-v04.json, docs/policy-validation-v04.json, research dossier and study protocol. No universal novelty or patient outcome benefit is claimed.');

for(const [key,pres,name,chartOwners] of [['architecture',a,'RENALIS_Architecture_v06',[]],['presentation',p,'RENALIS_Project_Presentation_v06',[2,9,14,16]]]){
 if(process.argv.includes('--architecture-only')&&key==='presentation'){all.push({key,name,slides:pres.slides.items.length,chartOwners});continue;}
 const folder=path.join(out,key);await fs.mkdir(folder,{recursive:true});
 for(const [i,slide] of pres.slides.items.entries()){
  const png=await pres.export({slide,format:'png',scale:process.argv.includes('--hires')?2:1});await fs.writeFile(path.join(folder,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 }
 const candidate=path.join(folder,'candidate.pptx');await(await PresentationFile.exportPptx(pres)).save(candidate);
 all.push({key,name,slides:pres.slides.items.length,chartOwners});
 console.log(`${key}: ${pres.slides.items.length} slides rendered.`);
}
await fs.writeFile(path.join(out,'manifest.json'),JSON.stringify(all,null,2));
// The bundled inspection exporter can set a process-wide exit code after
// successful preview exports. Reaching this point means every awaited export
// completed. Exceptions still abort before this line.
process.exitCode=0;
