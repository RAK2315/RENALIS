"""Resumable local narration and a continuous original music bed, four 5m parts."""
import argparse,hashlib,json,re,subprocess,wave
from pathlib import Path
import numpy as np
import soundfile as sf
import onnxruntime as ort
import imageio_ffmpeg
from video.narrate import LocalNarrator

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/submission-v05';SR=24000
STORY=json.loads(Path(__file__).with_name('story.json').read_text(encoding='utf-8'))
OUT.mkdir(exist_ok=True,parents=True);(OUT/'voice').mkdir(exist_ok=True)
def stamp(t,sep=','):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
def narrate(chapter=None):
    opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
    models=ROOT/'artifacts/video/models'
    session=ort.InferenceSession(str(models/'kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
    engine=LocalNarrator.from_session(session,str(models/'voices-v1.0.bin'))
    for s in STORY:
        if chapter and s['chapter']!=chapter:continue
        for j,text in enumerate(s['speech']):
            speed=[1.02,1.04,1.01][j]
            sig=digest([text,'af_heart',speed,'kokoro-1.0-v05'])
            p=OUT/'voice'/f"{s['id']}-{j}.wav";m=p.with_suffix('.json')
            if p.exists() and m.exists() and json.loads(m.read_text())['signature']==sig:
                print('Cached',p.name,flush=True);continue
            a,r=engine.create(text,voice='af_heart',speed=speed,lang='en-us')
            assert r==SR and np.isfinite(a).all() and np.max(np.abs(a))>.01
            sf.write(p,a,SR,subtype='PCM_16')
            m.write_text(json.dumps({'signature':sig,'seconds':len(a)/SR,'text':text,'voice':'af_heart','speed':speed},indent=2))
            print('Narrated',p.name,round(len(a)/SR,2),flush=True)

def assemble():
    timeline=[];all_cues=[]
    # Assemble short scenes first; fit only overlong scenes with pitch-preserving
    # atempo, retaining both original voice and the exact fitted audio.
    for s in STORY:
        if not all((OUT/'voice'/f"{s['id']}-{j}.wav").exists() and (OUT/'voice'/f"{s['id']}-{j}.json").exists() for j in range(3)):
            timeline.append(s)
            continue
        waves=[sf.read(OUT/'voice'/f"{s['id']}-{j}.wav",dtype='float32')[0] for j in range(3)]
        total=sum(len(a)/SR for a in waves)
        if total>28.1:
            ratio=total/28.1
            assert ratio<1.22, f"Rewrite overlong scene {s['id']}: {total}"
            for j in range(3):
                src=OUT/'voice'/f"{s['id']}-{j}.wav";dst=src.with_name(src.stem+'-fit.wav')
                subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-i',str(src),'-af',f'atempo={ratio}','-ar',str(SR),str(dst)],check=True)
                waves[j]=sf.read(dst,dtype='float32')[0]
        gap=(30-sum(len(a)/SR for a in waves))/4
        local=gap;beats=[];scene=np.zeros(30*SR,dtype=np.float32)
        for j,a in enumerate(waves):
            a=a.copy();fade=min(240,len(a)//2);a[:fade]*=np.linspace(0,1,fade);a[-fade:]*=np.linspace(1,0,fade)
            # Normalize phrase gain conservatively; limiter/loudness runs at final mux.
            a*=.72/max(.30,float(np.max(np.abs(a))))
            start=round(local*SR);scene[start:start+len(a)]+=a
            beat={'start':local,'duration':len(a)/SR,'text':s['speech'][j],'screen':s['points'][j]}
            beats.append(beat)
            words=beat['text'].split();pieces=[words[k:k+12] for k in range(0,len(words),12)];position=0
            for piece in pieces:
                begin=s['start']+local+len(a)/SR*position/len(words);position+=len(piece)
                end=s['start']+local+len(a)/SR*position/len(words)
                all_cues.append({'start':begin,'end':end,'text':' '.join(piece),'scene':s['id']})
            local+=len(a)/SR+gap
        sf.write(OUT/f"scene-{s['id']}-voice.wav",scene,SR,subtype='PCM_16')
        timeline.append({**s,'beats':beats,'spoken_seconds':sum(len(a)/SR for a in waves)})
    (OUT/'timeline.json').write_text(json.dumps(timeline,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'captions.json').write_text(json.dumps(all_cues,indent=2),encoding='utf-8')
    for sep,name,prefix in [(',','captions.srt',''),('.','captions.vtt','WEBVTT\n\n')]:
        (OUT/name).write_text(prefix+'\n\n'.join(f"{i+1}\n{stamp(c['start'],sep)} --> {stamp(c['end'],sep)}\n{c['text']}" for i,c in enumerate(all_cues))+'\n',encoding='utf-8')
    (OUT/'transcript.md').write_text('# RENALIS submission film\n\nTeam Sigmoid — Rehaan, JSS University, Noida\n\n'+'\n\n'.join(f"## {stamp(s['start'],'.')[:8]} — {s['title']}\n\n"+' '.join(s['speech']) for s in STORY),encoding='utf-8')
    chords=[[146.832,220.,293.665,349.228],[130.813,195.998,261.626,329.628],[174.614,261.626,349.228,440.],[130.813,195.998,293.665,391.995]]
    beat=60/82;bar=beat*4
    from contextlib import nullcontext
    complete=all('beats' in s for s in timeline)
    with (sf.SoundFile(OUT/'soundtrack.wav',mode='w',samplerate=SR,channels=2,subtype='PCM_16') if complete else nullcontext(None)) as full:
        for chapter in range(1,5):
            if not all('beats' in s for s in timeline if s['chapter']==chapter):continue
            base=(chapter-1)*300;size=300*SR
            voice=np.concatenate([sf.read(OUT/f"scene-{s['id']}-voice.wav",dtype='float32')[0] for s in STORY if s['chapter']==chapter])
            music=np.zeros((size,2),dtype=np.float32)
            for k in range(int((base-6)/bar),int((base+300)/bar)+1):
                begin=k*bar;chord=chords[k%4]
                for offset in [0,beat,beat*2,beat*3]:
                    at=begin+offset;low=max(base,at);high=min(base+300,at+5)
                    if high<=low:continue
                    t=np.arange(round((high-low)*SR))/SR+(low-at);ix=round((low-base)*SR);length=min(len(t),size-ix);t=t[:length]
                    freq=chord[int(round(offset/beat))%4]
                    env=(1-np.exp(-t/.025))*np.exp(-t/1.1)
                    tone=(np.sin(2*np.pi*freq*2*t)+.12*np.sin(2*np.pi*freq*4.003*t))*.017*env
                    pan=.5+.22*np.sin(k+offset)
                    music[ix:ix+length,0]+=tone*(1-pan);music[ix:ix+length,1]+=tone*pan
                    if offset==0:
                        for f in chord:
                            pad=(np.sin(2*np.pi*f*t)+.15*np.sin(2*np.pi*f*2.002*t))*.009*(1-np.exp(-t/.9))*np.exp(-t/3)
                            music[ix:ix+length]+=pad[:,None]
            absolute=base+np.arange(size)/SR
            fade=np.minimum(1,absolute/3)*np.minimum(1,(1200-absolute)/4)
            # Block-based speech ducking and a continuous score phase across joins.
            block=240;active=np.array([np.max(np.abs(voice[i:i+block]))>.025 for i in range(0,size,block)],dtype=float)
            smooth=np.convolve(np.pad(active,(15,15)),np.ones(31)/31,mode='valid')
            duck=1-.55*np.interp(np.arange(size)/block,np.arange(len(smooth)),smooth)
            mixed=voice[:,None]+music*(fade*duck)[:,None]
            sf.write(OUT/f'chapter-{chapter:02}-soundtrack.wav',mixed,SR,subtype='PCM_16')
            if full is not None:full.write(mixed)
    (OUT/'audio-provenance.json').write_text(json.dumps({'voice':'Kokoro-82M v1.0 af_heart; synthetic, local CPU','performance':'Warm delivery; phrase rates 1.01–1.04; no human impersonation','music':'Original procedural composition; continuous global phase; speech ducking','captions':'Phrase-level synthetic speech duration with proportional 12-word cue timing','duration_seconds':1200,'chapters':4,'complete':complete,'max_silent_scene_seconds':max(30-s['spoken_seconds'] for s in timeline if 'spoken_seconds' in s)},indent=2))
    print('Complete continuous soundtrack ready.' if complete else 'Available chapter timings/audio checkpointed; other narration is still generating.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--chapter',type=int);p.add_argument('--assemble',action='store_true');a=p.parse_args()
    if a.assemble:assemble()
    else:narrate(a.chapter)
