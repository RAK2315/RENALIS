"""Verify the delivered film, chapters, joins, audio and downloadable documents."""
import hashlib,json,subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/submission-v05'
FF=imageio_ffmpeg.get_ffmpeg_exe()
def metadata(p):
    frames=imageio_ffmpeg.read_frames(str(p));meta=next(frames);frames.close();return meta
def packets(p):
    r=subprocess.run([FF,'-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','framecrc','-'],capture_output=True,check=True)
    return sum(bool(l.strip()) and not l.startswith(b'#') for l in r.stdout.splitlines())
def main():
    final=OUT/'RENALIS_Team_Sigmoid_20min.mp4';assert final.exists()
    files=[final]+[OUT/f'RENALIS_Chapter_{i}_5min.mp4' for i in range(1,5)]
    media=[]
    for i,p in enumerate(files):
        m=metadata(p);duration=1200 if i==0 else 300
        assert abs(m['duration']-duration)<.06,(p.name,m)
        assert m['size']==(1920,1080) and m['fps']==24,m
        count=packets(p);assert count==duration*24,(p.name,count)
        media.append({'file':p.name,'seconds':m['duration'],'fps':m['fps'],'size':m['size'],'video_packets':count,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    # Decode every video and audio packet in the joined master.
    decoded=subprocess.run([FF,'-v','error','-i',str(final),'-f','null','-'],capture_output=True)
    assert decoded.returncode==0 and not decoded.stderr,decoded.stderr.decode(errors='replace')
    timeline=json.loads((OUT/'timeline.json').read_text());assert len(timeline)==40
    assert all(s['start']==i*30 and s['duration']==30 and len(s['beats'])==3 for i,s in enumerate(timeline))
    cues=json.loads((OUT/'captions.json').read_text());assert all(0<=c['start']<c['end']<=1200 for c in cues)
    assert all(a['end']<=b['start']+.001 for a,b in zip(cues,cues[1:]))
    for scene in timeline:
        actual=' '.join(c['text'] for c in cues if c['scene']==scene['id'])
        assert actual==' '.join(' '.join(scene['speech']).split()), scene['id']
    info=sf.info(OUT/'soundtrack.wav');assert info.frames==1200*24000 and info.channels==2
    joins=[]
    with sf.SoundFile(OUT/'soundtrack.wav') as a:
        for t in [300,600,900]:
            a.seek(t*24000-24000);x=a.read(48000,dtype='float32')
            jump=float(np.max(np.abs(x[24000]-x[23999])))
            assert jump<.03,(t,jump)
            joins.append({'second':t,'waveform_sample_jump':jump,'continuous_master_audio':True})
    # Save representative encoded frames, including all chapter boundaries.
    for t in [6,75,285,299.96,300,300.04,375,405,495,599.96,600,600.04,735,899.96,900,900.04,1015,1190]:
        subprocess.run([FF,'-y','-v','error','-ss',str(t),'-i',str(final),'-frames:v','1',str(OUT/f'qa-{t:g}.png')],check=True)
    result={'passed':True,'media':media,'full_master_decode':'passed without errors','chapter_joins':joins,'scenes':40,'caption_cues':len(cues),'audio_seconds':info.duration,'publication':'Local artifacts; entrant uploads video and publishes source','claims':'Sequential selector software-tested, independent policy validation remains planned'}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='media'},indent=2))
if __name__=='__main__':main()
