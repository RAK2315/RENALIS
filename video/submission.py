"""Reproducible local 20-minute research demo: Kokoro + real browser excerpts.

Run with .venv-video Python. No external upload is performed.
"""
import json,os,re,sys,subprocess,hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
import onnxruntime as ort
from video.narrate import LocalNarrator
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/submission';OUT.mkdir(exist_ok=True,parents=True)
STORY=json.loads((ROOT/'video/submission-narration.json').read_text(encoding='utf-8'))
SR=24000

def stamp(t,separator=','):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{separator}{ms:03}'

def audio():
    opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
    model=ROOT/'artifacts/video/models'
    session=ort.InferenceSession(str(model/'kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
    engine=LocalNarrator.from_session(session,str(model/'voices-v1.0.bin'))
    chapters=[]
    for i,scene in enumerate(STORY,1):
        if i<int(os.environ.get('RENALIS_VOICE_START','1')) or i>int(os.environ.get('RENALIS_VOICE_END','16')):continue
        chunks=[];current=''
        for sentence in re.split(r'(?<=[.!?])\s+',scene['text']):
            if len((current+' '+sentence).split())>43 and current:chunks.append(current);current=''
            current=(current+' '+sentence).strip()
        if current:chunks.append(current)
        cursor=1.;cues=[];parts=[np.zeros(SR)]
        for j,chunk in enumerate(chunks):
            filename=OUT/f'voice-{i:02}-{j:02}.wav';sig=hashlib.sha256(chunk.encode()).hexdigest();signature=filename.with_suffix('.sha256')
            if filename.exists() and signature.exists() and signature.read_text()==sig:wave,rate=sf.read(filename)
            else:
                wave,rate=engine.create(chunk,voice='af_heart',speed=1.,lang='en-us');sf.write(filename,wave,rate);signature.write_text(sig)
            assert rate==SR and np.isfinite(wave).all()
            # Sentence-sized captions keep full sentences visible in manageable lines.
            sentences=re.split(r'(?<=[.!?])\s+',chunk);weight=sum(len(t) for t in sentences)
            local=cursor
            for sentence in sentences:
                dur=len(wave)/SR*len(sentence)/weight;cues.append({'start':local,'end':local+dur,'text':sentence});local+=dur
            parts.extend([wave,np.zeros(round(.24*SR))]);cursor+=len(wave)/SR+.24
        speech=np.concatenate(parts);sf.write(OUT/f'audio-{i:02}.wav',speech,SR)
        chapters.append({'chapter':i,'title':scene['title'],'speech_seconds':len(speech)/SR,'cues':cues})
        print('Narration',i,round(len(speech)/SR,2),flush=True)
    if 'RENALIS_VOICE_START' in os.environ:return
    minimum=sum(max(60,c['speech_seconds']+2) for c in chapters)
    assert minimum<=1200,f'Speech exceeds 20-minute budget: {minimum}'
    extra=(1200-minimum)/len(chapters);cursor=0.;srt=[]
    for c in chapters:
        c['start']=cursor;c['duration']=max(60,c['speech_seconds']+2)+extra;cursor+=c['duration']
        for cue in c['cues']:srt.append(f"{len(srt)+1}\n{stamp(c['start']+cue['start'])} --> {stamp(c['start']+cue['end'])}\n{cue['text']}\n")
    chapters[-1]['duration']+=1200-cursor
    (OUT/'timeline.json').write_text(json.dumps(chapters,indent=2),encoding='utf-8')
    (OUT/'captions.srt').write_text('\n'.join(srt),encoding='utf-8')
    (OUT/'captions.vtt').write_text('WEBVTT\n\n'+'\n'.join(re.sub(r'(\d\d:\d\d:\d\d),(\d{3})',r'\1.\2',s) for s in srt),encoding='utf-8')

def ass_time(t):
    cent=round(t*100);h,cent=divmod(cent,360000);m,cent=divmod(cent,6000);s,cent=divmod(cent,100)
    return f'{h}:{m:02}:{s:02}.{cent:02}'

def render():
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();chapters=json.loads((OUT/'timeline.json').read_text());clips=json.loads((OUT/'clips.json').read_text())
    for c in chapters:
        i=c['chapter'];d=c['duration'];caption=OUT/f'chapter-{i:02}.ass'
        part_name=f'part-{i:02}.mp4' if i<=8 else f'part-{i:02}-final.mp4'
        existing=OUT/part_name
        if existing.exists():
            try:
                frames=imageio_ffmpeg.read_frames(str(existing));meta=next(frames);frames.close()
                if meta.get('duration',0)>=d-.1:
                    print('Reused complete chapter',i,flush=True);continue
            except (OSError,RuntimeError):pass
        header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Calibri,34,&H00F2F6E8,&H00FFFFFF,&H00233D30,&H00233D30,0,0,0,0,100,100,0,0,3,14,0,2,90,90,28,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
        events=[f"Dialogue: 0,{ass_time(cue['start'])},{ass_time(cue['end'])},Default,,0,0,0,,{cue['text']}" for cue in c['cues']]
        events.append(f"Dialogue: 0,{ass_time(c['speech_seconds']+.5)},{ass_time(d)},Default,,0,0,0,,Review the on-screen example. The next chapter continues automatically.")
        caption.write_text(header+'\n'.join(events),encoding='utf-8')
        args=[ffmpeg,'-y','-hide_banner','-loglevel','error','-loop','1','-framerate','1','-i',str(ROOT/f'tmp/submission/presentation/slide-{i:02}.png')]
        clip=clips.get(str(i));inputs=1
        if clip:args+=['-i',str(OUT/clip)];inputs+=1
        args+=['-i',str(OUT/f'audio-{i:02}.wav')]
        # Preserve the entire slide and recorded viewport. Caption area never crops evidence.
        filters=['[0:v]scale=1600:900:flags=lanczos,pad=1920:1080:160:0:color=0x173d30,fps=24,setsar=1[slide]']
        if clip:
            start=max(12,c['speech_seconds']-19)
            filters+=[f'[1:v]scale=-2:900:flags=lanczos,pad=1920:1080:(ow-iw)/2:0:color=0x173d30,setsar=1,fps=24,tpad=stop_mode=clone:stop_duration={d},setpts=PTS-STARTPTS+{start}/TB[clip]',f"[slide][clip]overlay=eof_action=pass:enable='gte(t,{start})'[base]"]
        else:filters+=['[slide]null[base]']
        filters+=[f'[base]ass=artifacts/submission/chapter-{i:02}.ass,fade=t=in:st=0:d=0.5,fade=t=out:st={d-.5}:d=0.5[v]',f'[{inputs}:a]apad,alimiter=limit=0.95[a]']
        args+=['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-t',str(d),'-c:v','libx264','-preset','ultrafast','-crf','22','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','128k','-threads','4',str(OUT/part_name)]
        subprocess.run(args,check=True,cwd=ROOT);print('Rendered',i,flush=True)
    (OUT/'parts.txt').write_text('\n'.join(f"file 'part-{c['chapter']:02}{'-final' if c['chapter']>8 else ''}.mp4'" for c in chapters))
    subprocess.run([ffmpeg,'-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(OUT/'parts.txt'),'-c','copy','-t','1200','-movflags','+faststart',str(OUT/'RENALIS_Submission_Demo_v04.mp4')],check=True)
    (OUT/'player.html').write_bytes((ROOT/'video/submission-player.html').read_bytes())
    (OUT/'provenance.json').write_text(json.dumps({'duration_seconds':1200,'resolution':[1920,1080],'fps':24,'narration':'Local Kokoro-82M v1.0, af_heart, synthetic voice','voice_license':'Apache-2.0 model; MIT runtime','footage':'Actual browser recordings against an isolated fictional-patient database','slides':'Editable RENALIS 0.4 presentation','captions':'Sentence-sized timing proportional within TTS chunks, burned into video; SRT/VTT included','publication':'Local artifact only; not uploaded'},indent=2))

if __name__=='__main__':
    if '--render' in sys.argv:render()
    else:audio()
