"""Insert entrant-supplied publication URLs; does not upload or assert access."""
import argparse,json,re
from pathlib import Path
from urllib.parse import urlparse,parse_qs
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--youtube',required=True);p.add_argument('--repository',required=True);a=p.parse_args()
    u=urlparse(a.youtube);host=u.hostname or ''
    video=u.path.strip('/') if host=='youtu.be' else parse_qs(u.query).get('v',[''])[0]
    if u.scheme!='https' or host not in {'youtu.be','youtube.com','www.youtube.com'} or not re.fullmatch(r'[A-Za-z0-9_-]{11}',video):p.error('Supply a real HTTPS YouTube watch/share URL.')
    r=urlparse(a.repository)
    if r.scheme!='https' or r.hostname!='github.com' or not re.fullmatch(r'/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+/?',r.path):p.error('Supply the actual HTTPS GitHub owner/repository URL.')
    youtube=f'https://www.youtube.com/watch?v={video}';repo='https://github.com'+r.path.rstrip('/')
    readme=ROOT/'README.md';s=readme.read_text(encoding='utf-8')
    s=re.sub(r'^\*\*20-minute narrated demo:\*\*.*$',f'**20-minute narrated demo:** [Watch the unlisted video]({youtube}). **Source:** [Public GitHub repository]({repo}).',s,flags=re.M)
    s=s.replace('20-minute film prepared locally; actual YouTube watch link must be added after entrant upload',f'[Unlisted 20-minute demo]({youtube})')
    readme.write_text(s,encoding='utf-8')
    team_path=ROOT/'docs/team.json';team=json.loads(team_path.read_text());team.update(youtube_url=youtube,repository_url=repo);team_path.write_text(json.dumps(team,indent=2),encoding='utf-8')
    print('README and team metadata updated. Verify anonymous playback/download access before submitting; this command does not verify publication.')
if __name__=='__main__':main()
