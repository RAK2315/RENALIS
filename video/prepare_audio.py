"""Place local synthetic narration, original score, captions, and timeline."""
import json
import math
import wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'video'
SR=48000
FPS=30
story=json.loads((ROOT/'video'/'storyboard.json').read_text(encoding='utf-8'))


def read_wav(path):
    with wave.open(str(path),'rb') as source:
        rate=source.getframerate();channels=source.getnchannels();width=source.getsampwidth()
        assert width==2, 'Expected 16-bit local speech audio'
        data=np.frombuffer(source.readframes(source.getnframes()),dtype='<i2').astype(float)/32768
        data=data.reshape(-1,channels).mean(axis=1)
    if rate!=SR:
        data=np.interp(np.arange(round(len(data)*SR/rate))*rate/SR,np.arange(len(data)),data)
    return data


def write_wav(path,data):
    if data.ndim==1:data=np.column_stack([data,data])
    with wave.open(str(path),'wb') as output:
        output.setnchannels(2);output.setsampwidth(2);output.setframerate(SR)
        output.writeframes((np.clip(data,-.97,.97)*32767).astype('<i2').tobytes())


def stamp(seconds):
    n=round(seconds*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,ms=divmod(n,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


cursor=0;timeline=[];cues=[]
for scene in story:
    local=.75;beats=[]
    for beat in scene['beats']:
        path=OUT/'narration-v2'/f"{scene['id']}-{beat['key']}.wav"
        voice=read_wav(path);speech_duration=len(voice)/SR
        # Keep each concept visible while its actual audio plays, plus a reading pause.
        hold=max(speech_duration+beat.get('pause',.55),len(beat['screen'].split())/3.0)
        item={**beat,'start':cursor+local,'local_start':local,
              'voice_duration':speech_duration,'duration':hold,'audio':path.name}
        beats.append(item)
        # Split only long captions at punctuation or a word boundary. Timings
        # stay inside this individual utterance instead of a whole scene.
        words=beat['text'].split();parts=[words] if len(words)<=15 else [words[:len(words)//2],words[len(words)//2:]]
        position=0
        for part in parts:
            start=item['start']+speech_duration*position/len(words)
            position+=len(part)
            end=item['start']+speech_duration*position/len(words)
            cues.append({'start':start,'end':end,'text':' '.join(part),'scene':scene['id'],'beat':beat['key']})
        local+=hold
    frames=math.ceil((local+.65)*FPS);duration=frames/FPS
    scene={**scene,'beats':beats,'start':cursor,'duration':duration,'frames':frames,
           'voice':' '.join(b['text'] for b in beats)}
    scene['caption_cues']=[c for c in cues if c['start']>=cursor and c['start']<cursor+duration]
    timeline.append(scene);cursor+=duration

size=round(cursor*SR)
narration=np.zeros(size)
for scene in timeline:
    for beat in scene['beats']:
        voice=read_wav(OUT/'narration-v2'/beat['audio'])
        # Tiny fades prevent clicks where phrase files join the silent bed.
        fade_samples=min(round(.012*SR),len(voice)//2)
        voice[:fade_samples]*=np.linspace(0,1,fade_samples)
        voice[-fade_samples:]*=np.linspace(1,0,fade_samples)
        start=round(beat['start']*SR);narration[start:start+len(voice)]+=voice
narration*=.78/max(np.max(np.abs(narration)),1e-6)
write_wav(OUT/'narration.wav',narration)

# Original ambient score. No stock recording, sampled song, or copyrighted melody.
music=np.zeros((size,2),dtype=np.float64)
chords=[[146.832,220.,293.665,349.228],[130.813,195.998,261.626,329.628],
        [174.614,261.626,349.228,440.],[130.813,195.998,293.665,391.995]]
beat=60/78
for bar,start in enumerate(np.arange(0,cursor,beat*4)):
    chord=chords[bar%4]
    length=min(round(beat*5*SR),size-round(start*SR))
    if length<=0:continue
    t=np.arange(length)/SR
    pad=(1-np.exp(-t/1.15))*np.exp(-t/3.9)
    for k,freq in enumerate(chord):
        tone=(np.sin(2*np.pi*freq*t)+.24*np.sin(2*np.pi*freq*2.002*t))*.014*pad
        pan=.35+.3*k/3
        i=round(start*SR);music[i:i+length,0]+=tone*(1-pan);music[i:i+length,1]+=tone*pan
    for j in range(4):
        pluck_start=start+j*beat
        if pluck_start>=cursor:break
        length=min(round(2.7*SR),size-round(pluck_start*SR));tt=np.arange(length)/SR
        freq=chord[(bar+j)%4]*2
        env=(1-np.exp(-tt/.008))*np.exp(-tt/1.0)
        tone=(np.sin(2*np.pi*freq*tt)+.15*np.sin(2*np.pi*freq*3*tt))*env*.025
        i=round(pluck_start*SR);pan=.5+.2*np.sin(bar+j)
        music[i:i+length,0]+=tone*(1-pan);music[i:i+length,1]+=tone*pan
    for j in (0,2):
        at=start+j*beat;length=min(round(.20*SR),size-round(at*SR))
        if length<=0:continue
        tt=np.arange(length)/SR;tone=np.sin(2*np.pi*(47*tt+2*(1-np.exp(-tt*30))))*np.exp(-tt*27)*.025
        i=round(at*SR);music[i:i+length]+=tone[:,None]

# Gentle original transition accents and click ticks, kept below narration.
for scene in timeline[1:]:
    at=max(0,scene['start']-.12);length=min(round(.65*SR),size-round(at*SR));tt=np.arange(length)/SR
    tone=(np.sin(2*np.pi*(700*tt-380*tt**2))*.008)*np.sin(np.pi*np.minimum(tt/.65,1))**2
    i=round(at*SR);music[i:i+length,0]+=tone;music[i:i+length,1]+=tone*.7
fade=np.minimum(1,np.arange(size)/(SR*2.3))*np.minimum(1,(size-np.arange(size))/(SR*3.5))
music*=fade[:,None]
write_wav(OUT/'original-score.wav',music)
# Smooth speech ducking: keep the original score, make every word intelligible.
# Block envelope avoids an expensive sample-wise convolution for a long film.
block=480;peaks=np.array([float(np.max(np.abs(narration[i:i+block]))) for i in range(0,size,block)])
active=np.minimum(1,peaks/.035)
smooth=np.convolve(np.pad(active,(15,15)),np.ones(31)/31,mode='valid')
duck=1-.48*np.interp(np.arange(size)/block,np.arange(len(smooth)),smooth)
mixed=music*duck[:,None];mixed[:,0]+=narration;mixed[:,1]+=narration
write_wav(OUT/'soundtrack.wav',mixed)
(OUT/'timeline.json').write_text(json.dumps({'revision':2,'fps':FPS,'width':1920,'height':1080,'duration':cursor,'scenes':timeline,'captions':cues},indent=2),encoding='utf-8')
(OUT/'renalis-explainer.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(cues))+'\n',encoding='utf-8')
(OUT/'transcript.txt').write_text('\n\n'.join(f"{s['chapter']}\n{s['voice']}" for s in timeline)+'\n',encoding='utf-8')
print(json.dumps({'seconds':round(cursor,2),'fps':FPS,'scenes':len(timeline),'words':sum(len(s['voice'].split()) for s in timeline)},indent=2))
