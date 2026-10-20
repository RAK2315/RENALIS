"""Decode the finished export and inspect samples from every scene."""
import json
import re
import subprocess
from pathlib import Path
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'video'
QA=OUT/'qa';QA.mkdir(exist_ok=True)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
timeline=json.loads((OUT/'timeline.json').read_text(encoding='utf-8'))
video=OUT/'renalis-explainer.mp4'


def run(args):
    return subprocess.run([ffmpeg,*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,creationflags=subprocess.CREATE_NO_WINDOW)


metadata={}
for name in ('renalis-explainer.mp4','renalis-music-only.mp4'):
    reader=imageio_ffmpeg.read_frames(str(OUT/name))
    info=next(reader);reader.close()
    assert tuple(info['size'])==(1920,1080),info
    assert abs(info['fps']-30)<.01,info
    assert abs(info['duration']-timeline['duration'])<.12,info
    decoded=run(['-v','error','-i',str(OUT/name),'-map','0:v:0','-map','0:a:0','-f','null','-'])
    assert not decoded.stderr.strip(),decoded.stderr.decode(errors='replace')
    metadata[name]={**info,'bytes':(OUT/name).stat().st_size,'full_decode':'passed'}
    print(f'Full decode passed: {name}')

analysis=run(['-hide_banner','-i',str(video),'-vn','-sn','-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-'])
text=analysis.stderr.decode(errors='replace')
blocks=re.findall(r'\{\s*"input_i"[\s\S]+?\}',text)
assert blocks,'No loudness report produced'
loudness=json.loads(blocks[-1])
assert float(loudness['input_i'])>-25,loudness
assert float(loudness['input_tp'])<0,loudness

for i,scene in enumerate(timeline['scenes']):
    at=scene['start']+min(scene['duration']*.46,5)
    run(['-y','-hide_banner','-loglevel','error','-ss',str(at),'-i',str(video),'-frames:v','1',str(QA/f'frame-{i:02}.png')])
rows=(len(timeline['scenes'])+1)//2
run(['-y','-hide_banner','-loglevel','error','-framerate','1','-i',str(QA/'frame-%02d.png'),'-vf',f'scale=768:432,tile=2x{rows}:padding=12:margin=12:color=0xf1f4e9','-frames:v','1',str(OUT/'contact-sheet.png')])
run(['-y','-hide_banner','-loglevel','error','-ss',str(timeline['scenes'][1]['start']+3),'-i',str(video),'-frames:v','1',str(OUT/'poster.png')])
report={'duration_seconds':timeline['duration'],'resolution':[1920,1080],'fps':30,'frames':sum(s['frames'] for s in timeline['scenes']),
        'files':metadata,'audio_loudness':loudness,'sampled_scenes':len(timeline['scenes']),
        'provenance':'Complete production app panels from an isolated synthetic-demo database. Local Kokoro af_heart narration and original generated score.',
        'composition_checks':json.loads((OUT/'composition-checks.json').read_text(encoding='utf-8'))['status'],
        'spoken_concepts':sum(len(s['beats']) for s in timeline['scenes'])}
(OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'duration':report['duration_seconds'],'frames':report['frames'],'loudness':loudness,'qa':'passed'},indent=2))
