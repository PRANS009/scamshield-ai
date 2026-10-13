import io
from xml.sax.saxutils import escape
from fastapi import HTTPException, UploadFile
from app.config import MAX_UPLOAD

async def read_upload(file: UploadFile, extensions):
    name=(file.filename or '').lower()
    if not any(name.endswith(ext) for ext in extensions):
        raise HTTPException(415,'Unsupported file type. Allowed: '+', '.join(extensions))
    data=await file.read(MAX_UPLOAD+1)
    await file.close()
    if len(data)>MAX_UPLOAD:
        raise HTTPException(413,'Maximum file size is 5 MB.')
    if not data:
        raise HTTPException(422,'The uploaded file is empty.')
    return name,data

def extract_document(name,data):
    if name.endswith('.txt'):
        try:
            text=data.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(422,'Text files must be UTF-8.') from None
    else:
        if not data.startswith(b'%PDF-'):
            raise HTTPException(415,'The file is not a valid PDF.')
        try:
            import fitz
            with fitz.open(stream=data,filetype='pdf') as document:
                if document.needs_pass or len(document)>20:
                    raise ValueError('Encrypted PDFs and PDFs over 20 pages are unsupported.')
                parts=[];total=0
                for page in document:
                    text=page.get_text()
                    total+=len(text)
                    if total>25000:
                        raise ValueError('Document exceeds the 25,000-character text limit.')
                    parts.append(text)
                text='\n'.join(parts)
        except Exception:
            raise HTTPException(422,'Unable to extract PDF: use an unencrypted text PDF, at most 20 pages and 25,000 characters.') from None
    if len(text)>25000 or len(text.strip())<10:
        raise HTTPException(422,'Need 10–25,000 characters of extractable text. Scanned PDFs need OCR before upload.')
    return text

def decode_qr(data):
    try:
        from PIL import Image
        import numpy as np
        import cv2
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ('PNG','JPEG') or image.width*image.height>12_000_000:
                raise ValueError()
            image.thumbnail((1800,1800))
            arr=cv2.cvtColor(np.array(image.convert('RGB')),cv2.COLOR_RGB2BGR)
        value,_,_=cv2.QRCodeDetector().detectAndDecode(arr)
        if not value or len(value)>25000:
            raise ValueError()
        return value
    except Exception:
        raise HTTPException(422,'No readable QR code found. Use a clear PNG/JPEG under 12 megapixels.') from None

def make_pdf(report):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    out=io.BytesIO();styles=getSampleStyleSheet()
    styles['Title'].textColor=colors.HexColor('#1674da')
    story=[]
    def add(text,style='BodyText'):
        # All external strings are escaped: ReportLab paragraph markup is never accepted.
        story.append(Paragraph(escape(str(text)),styles[style]));story.append(Spacer(1,8))
    add('ScamShield AI — Risk Report','Title');add('Verify Before You Trust.','Heading2')
    add(f'Report: {report.report_id} | Generated: {report.created_at}')
    add(f'{report.risk_level} | Rule score {report.risk_score}/100 | Evidence: {report.evidence_confidence}','Heading2')
    add(report.summary);add(f'Research: {report.research_status}')
    for title,items in [('Research notices',report.research_errors),('Observed indicators',[f'{f.label} (+{f.points}): {f.explanation}' for f in report.red_flags]),
        ('Local observations',report.verified_facts),('Possible contradictions',report.contradictory_evidence),('Unverified claims',report.unverified_claims),
        ('Recommended actions',report.recommendations),('Limitations',report.limitations)]:
        add(title,'Heading2')
        for item in items or ['None recorded.']:
            add(item)
    add('Evidence sources — search excerpts, not independently verified','Heading2')
    for source in report.sources:
        add(f'[{source.id}] {source.title}','Heading3');add(source.url);add(source.snippet);add('Retrieved: '+source.retrieved_at)
    SimpleDocTemplate(out,title='ScamShield AI report').build(story)
    return out.getvalue()
