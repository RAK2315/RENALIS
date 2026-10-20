"""Package visually reviewed slide renders as PDF, with a readable source page.

Editable diagrams/charts and source notes remain in the corresponding PPTX.
The bundled slide PDF exporter currently lacks its standard-font module.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('Calibri',r'C:\Windows\Fonts\calibri.ttf'))

for key,name in [('presentation','RENALIS_Project_Presentation_v04'),('architecture','RENALIS_Architecture_v04')]:
    pages=sorted((ROOT/'tmp/submission'/key).glob('slide-*.png'))
    assert len(pages)==(16 if key=='presentation' else 3)
    target=ROOT/'output/pdf'/f'{name}.pdf'
    c=canvas.Canvas(str(target),pagesize=(1280,720),pageCompression=1)
    c.setTitle(name.replace('_',' '));c.setAuthor('RENALIS project')
    for i,p in enumerate(pages):
        c.bookmarkPage(f'slide-{i+1}');c.addOutlineEntry(f'Slide {i+1}',f'slide-{i+1}')
        c.drawImage(ImageReader(str(p)),0,0,width=1280,height=720);c.showPage()
    c.setFillColor(HexColor('#f7f8f2'));c.rect(0,0,1280,720,fill=1,stroke=0)
    c.setFillColor(HexColor('#173d30'));c.setFont('Calibri',38);c.drawString(64,650,'Sources and interpretation')
    lines=[
        'Implementation: backend/history.py, model.py, mechanisms.py, insights.py and app.py.',
        'Observed results: docs/observed-v04.json and scripts/evaluate_observed_v04.py.',
        'Policy results: docs/policy-validation-v04.json. Initial report and metric amendment retained.',
        'Dataset: Wu, C.-J., HEMOBP v3 (2018), CC BY 4.0. DOI 10.6084/m9.figshare.6260654.v3.',
        'Data publication: https://www.nature.com/articles/s41597-019-0319-8',
        'Clinical context: KDIGO BP and Volume Management in Dialysis conference report (2020).',
        'FHIR R4: https://hl7.org/fhir/R4/observation.html',
        'ABDM guide: https://nrces.in/ndhm/fhir/r4/',
        'Research and competitor decisions: RENALIS_Research_Strategy_and_Master_Plan.pdf.',
        'Study design: docs/clinical-study-protocol.md. No actual clinical study is claimed.',
        'This PDF preserves reviewed slide renders. Editable charts/diagrams and per-slide notes',
        'are in the corresponding PPTX. Software checks do not establish clinical usefulness.',
    ]
    c.setFont('Calibri',23)
    for i,line in enumerate(lines):c.drawString(64,575-i*39,line)
    c.showPage();c.save()
    assert len(PdfReader(str(target)).pages)==len(pages)+1
    print(target.name,len(pages)+1,'pages')
