"""Prepare thumbnail, upload copy and a compact delivery manifest."""
import json,sys,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/submission-v05'
def main():
    im=Image.new('RGB',(1280,720),'#123c2c');d=ImageDraw.Draw(im)
    fonts=Path('C:/Windows/Fonts')
    serif=ImageFont.truetype(str(fonts/'georgia.ttf'),68)
    title=ImageFont.truetype(str(fonts/'georgia.ttf'),53)
    sans=ImageFont.truetype(str(fonts/'calibri.ttf'),26)
    number=ImageFont.truetype(str(fonts/'calibrib.ttf'),52)
    for r in [135,195,255]:d.ellipse((970-r,325-r,970+r,325+r),outline='#486d46',width=2)
    d.text((65,47),'RENALIS',font=serif,fill='#e7efce')
    d.text((66,170),'Which measurement\nshould come next?',font=title,fill='#e7efce',spacing=12)
    d.text((68,330),'A dialysis twin that explains its uncertainty',font=sans,fill='#b5cba8')
    d.rounded_rectangle((68,420,525,560),radius=16,fill='#e1ebd5')
    d.text((92,438),'CARDIAC OUTPUT',font=sans,fill='#4f6651');d.text((92,480),'3.74 L/min',font=number,fill='#173d30')
    d.line((555,490,675,490),fill='#bdd49b',width=8);d.polygon([(675,490),(650,473),(650,507)],fill='#bdd49b')
    d.rounded_rectangle((710,420,1206,560),radius=16,fill='#e1ebd5')
    d.text((734,438),'NEXT: RELATIVE BLOOD VOLUME',font=sans,fill='#4f6651');d.text((734,480),'Acquire. Reassess.',font=number,fill='#173d30')
    d.text((68,638),'TEAM SIGMOID · REHAAN · JSS UNIVERSITY, NOIDA',font=sans,fill='#bfd1ac')
    d.text((1070,640),'20:00 DEMO',font=ImageFont.truetype(str(fonts/'calibrib.ttf'),24),fill='#e7efce')
    im.save(OUT/'thumbnail.png',optimize=True)
    description='''TITLE
RENALIS | Evidence-aware Dialysis Digital Twin | Team Sigmoid | 20-Minute Demo

DESCRIPTION
RENALIS makes competing physiological explanations and the next evidence question visible in a dialysis research workspace. This complete demonstration includes the actual website, animated model explanations, an adaptive CO3.74 → relative-volume85.0 investigation, an auditable evidence trail, and the evaluated results and limitations.

Team: Sigmoid
Entrant: Rehaan (solo)
Institution: JSS University, Noida
Public GitHub repository: ADD THE ACTUAL PUBLIC REPOSITORY URL BEFORE UPLOAD

CHAPTERS
00:00 The problem and the twin
05:00 The next evidence question
10:00 The evidence behind the claims
15:00 A complete research prototype

The built-in patients and captured device streams are fictional. The public observed-data benchmark is separate. The new sequential selector is implemented and software-tested; independent multi-acquisition policy validation remains planned. Earlier decision-value selection did not outperform fixed cuff overall in the frozen synthetic holdout. No clinical diagnosis, treatment control or prospective patient benefit is claimed.

Synthetic local narration: Kokoro-82M v1.0, af_heart. Original procedural background score. No human voice is impersonated.

UPLOAD SETTINGS
Visibility: Unlisted. Upload the joined20-minute MP4, English SRT captions and supplied thumbnail. After upload, put the actual watch link in README and docs/team.json. Verify anonymous playback and public repository downloads before submitting the form.
'''
    (OUT/'upload-description.txt').write_text(description,encoding='utf-8')
    print('Thumbnail and upload copy ready.')
def kit():
    result=json.loads((OUT/'verification.json').read_text());assert result['passed']
    source=ROOT/'artifacts/release/RENALIS-Sigmoid-GitHub'
    manifest=json.loads((ROOT/'artifacts/release/source-manifest.json').read_text())['manifest']
    target=ROOT/'artifacts/release/RENALIS_Sigmoid_Submission_Kit.zip'
    with zipfile.ZipFile(target,'w') as z:
        for name in ['RENALIS_Team_Sigmoid_20min.mp4','captions.srt','captions.vtt','transcript.md','thumbnail.png','upload-description.txt','verification.json','audio-provenance.json','player-checks.json','capture-checks.json']:
            p=OUT/name;assert p.exists(),p
            z.write(p,'RENALIS-Sigmoid/video/'+name,compress_type=zipfile.ZIP_STORED if p.suffix=='.mp4' else zipfile.ZIP_DEFLATED)
        for rel in sorted(manifest):z.write(source/rel,'RENALIS-Sigmoid/github/'+rel,compress_type=zipfile.ZIP_DEFLATED)
        z.write(ROOT/'docs/UPLOAD_NEXT.md','RENALIS-Sigmoid/UPLOAD_NEXT.md',compress_type=zipfile.ZIP_DEFLATED)
    print('Complete submission kit:',target,'bytes:',target.stat().st_size)
if __name__=='__main__':
    if '--kit' in sys.argv:kit()
    else:main()
