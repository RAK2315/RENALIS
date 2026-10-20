"""Prepare a reviewed public-source folder and ZIP; never publish automatically."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/release';BUNDLE=OUT/'RENALIS-Sigmoid-GitHub'
DIRS=['.github','backend','docs','public','scripts','src','tests','video']
FILES=['.gitignore','.gitattributes','LICENSE','README.md','THIRD_PARTY_NOTICES.md','index.html',
       'package.json','package-lock.json','requirements.txt','requirements-lock.txt','tsconfig.json','vite.config.ts']
IGNORE={'node_modules','__pycache__','.venv','.venv-video','.git'}
def keep(p):return not any(x in IGNORE for x in p.parts) and p.suffix not in {'.pyc','.sqlite','.wav','.mp4','.webm'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    OUT.mkdir(parents=True,exist_ok=True);BUNDLE.mkdir(exist_ok=True)
    selected=[ROOT/f for f in FILES]
    for d in DIRS:selected.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and keep(p.relative_to(ROOT)))
    selected.extend((ROOT/'output/pdf').glob('*.pdf'))
    selected.extend(p for p in (ROOT/'output/presentations').glob('*_Final.pptx') if '_v04_' in p.name or '_Release_Final' in p.name)
    manifest={}
    for p in selected:
        assert p.stat().st_size<50_000_000,p
        rel=p.relative_to(ROOT);target=BUNDLE/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        manifest[rel.as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
    previous_path=OUT/'source-manifest.json'
    if previous_path.exists():
        previous=json.loads(previous_path.read_text(encoding='utf-8')).get('manifest',{})
        for rel in set(previous)-set(manifest):
            old=(BUNDLE/rel).resolve()
            assert old.is_relative_to(BUNDLE.resolve()),'Generated path escaped the source bundle'
            if old.is_file():old.unlink()  # Only a file recorded in our earlier generated manifest.
    # Basic source-content inspection; never echo a candidate secret.
    secret_patterns=[rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}']
    findings=[]
    for rel in manifest:
        p=BUNDLE/rel
        if p.suffix in {'.py','.ts','.tsx','.js','.cjs','.mjs','.json','.md','.yml','.html','.txt'}:
            b=p.read_bytes()
            if any(re.search(pattern,b) for pattern in secret_patterns):findings.append(rel)
    assert not findings,'Potential credential material requires review in: '+','.join(findings)
    links=re.findall(r'\]\(([^)]+)\)',(BUNDLE/'README.md').read_text(encoding='utf-8'))
    missing=[x for x in links if not x.startswith(('http:','https:','#','mailto:')) and not (BUNDLE/x.split('#')[0]).exists()]
    assert not missing,missing
    team=json.loads((BUNDLE/'docs/team.json').read_text())
    assert team['team_name']=='Sigmoid' and team['members'][0]['name']=='Rehaan'
    result={'prepared':True,'published':False,'files':len(manifest),'bytes':sum(v['bytes'] for v in manifest.values()),
            'credential_pattern_check':'passed; basic check, not a formal security audit','readme_local_links':'passed',
            'remaining_publication_steps':['Entrant uploads MP4 as unlisted YouTube','Add actual video URL to README','Publish public GitHub repository','Verify anonymous access and submit'],
            'manifest':manifest}
    (OUT/'source-manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    zip_path=OUT/'RENALIS_Sigmoid_GitHub_Source.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel in sorted(manifest):z.write(BUNDLE/rel,arcname='RENALIS-Sigmoid/'+rel)
    print(json.dumps({'folder':str(BUNDLE),'zip':str(zip_path),'files':len(manifest),'zip_bytes':zip_path.stat().st_size,'readme_links':'passed','credential_pattern_check':'passed'},indent=2))
if __name__=='__main__':build()
