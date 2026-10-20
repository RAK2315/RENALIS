"""Export reviewed high-resolution slides with a searchable native text layer."""
import json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
pdfmetrics.registerFont(TTFont('SegoeUI',r'C:\Windows\Fonts\segoeui.ttf'))
N={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
for item in json.loads((ROOT/'tmp/design-v06/manifest.json').read_text()):
    pages=sorted((ROOT/'tmp/design-v06'/item['key']).glob('slide-*.png'))
    assert len(pages)==item['slides']
    target=ROOT/'output/pdf'/f"{item['name']}.pdf"
    c=canvas.Canvas(str(target),pagesize=(1600,900),pageCompression=1)
    c.setTitle('RENALIS '+('Architecture' if item['key']=='architecture' else 'Project Presentation'))
    c.setAuthor('Rehaan / Team Sigmoid / JSS University, Noida')
    z=zipfile.ZipFile(ROOT/'tmp/design-v06'/item['key']/'candidate.pptx')
    for i,p in enumerate(pages):
        c.bookmarkPage(f'page-{i+1}');c.addOutlineEntry(f"{item['key'].title()} {i+1}",f'page-{i+1}')
        c.drawImage(ImageReader(str(p)),0,0,width=1600,height=900)
        # This conversion adds searchable text from the original editable slide
        # objects without changing the reviewed visual rendering.
        xml=ET.fromstring(z.read(f'ppt/slides/slide{i+1}.xml'))
        for shape in xml.findall('.//p:sp',N):
            offset=shape.find('.//a:xfrm/a:off',N)
            if offset is None:continue
            x=int(offset.get('x'))/9525;y=900-int(offset.get('y'))/9525-20
            text=' '.join(t.text or '' for t in shape.findall('.//a:t',N))
            if not text:continue
            layer=c.beginText(x,y);layer.setFont('SegoeUI',18);layer.setTextRenderMode(3);layer.textLine(text);c.drawText(layer)
        c.linkURL('https://github.com/RAK2315/RENALIS',rect=(64,13,700,55),relative=0)
        if item['key']=='presentation' and i==19:
            c.linkURL('https://youtu.be/ZcWNYMtM1tI',rect=(66,330,1090,420),relative=0)
            c.linkURL('https://github.com/RAK2315/RENALIS',rect=(66,220,1120,310),relative=0)
        c.showPage()
    c.save()
    assert len(PdfReader(target).pages)==item['slides']
    assert len(PdfReader(target).pages[0].extract_text())>50
    print(target.name,item['slides'],'pages')
