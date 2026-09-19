import io, requests
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128

SMALL_TAG_WIDTH_MM = 50
SMALL_TAG_HEIGHT_MM = 12

def price_text(v):
    if v in (None, ""): return ""
    s = str(v).replace("€", "").strip()
    try: return f"{float(s):.2f} EUR"
    except: return f"{s} EUR"

def _fit_text(c, text, font, max_size, min_size, width):
    size = max_size
    while size > min_size and c.stringWidth(str(text), font, size) > width:
        size -= .5
    return size

def create_small_tag_pdf(items, copies=1):
    """One 50 x 12 mm PDF page per fold-over jewelry tag."""
    width, height = SMALL_TAG_WIDTH_MM * mm, SMALL_TAG_HEIGHT_MM * mm
    half = width / 2
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    for item in items:
        for _ in range(max(1, int(copies))):
            barcode = str(item.get("barcode") or "")
            title = str(item.get("title") or "")
            variant = str(item.get("variant") or "").replace("Default Title", "").strip(" ,")
            price = price_text(item.get("price"))
            # subtle fold guide
            c.setStrokeColor(colors.HexColor("#d5d5d5"))
            c.setLineWidth(.25)
            c.setDash(1, 1)
            c.line(half, 1.2*mm, half, height-1.2*mm)
            c.setDash()
            c.setFillColor(colors.black)
            # left face: Code 128 + exact human-readable barcode
            if len(barcode) == 8 and barcode.isdigit():
                bc = code128.Code128(barcode, barHeight=5.0*mm, barWidth=.24*mm, humanReadable=False)
                maxw = half - 3*mm
                if bc.width > maxw: bc.barWidth *= maxw / bc.width
                bc.drawOn(c, (half-bc.width)/2, 4.0*mm)
                c.setFont("Helvetica", 5.8)
                c.drawCentredString(half/2, 1.4*mm, barcode)
            # right face: price, product and variant
            rx = half + 1.5*mm
            rw = half - 3*mm
            ps = _fit_text(c, price, "Helvetica-Bold", 7.2, 5.2, rw)
            c.setFont("Helvetica-Bold", ps); c.drawCentredString(half+half/2, 8.6*mm, price)
            ts = _fit_text(c, title, "Helvetica-Bold", 6.2, 4.5, rw)
            c.setFont("Helvetica-Bold", ts); c.drawCentredString(half+half/2, 5.4*mm, title)
            if variant:
                vs = _fit_text(c, variant, "Helvetica", 4.9, 3.7, rw)
                c.setFont("Helvetica", vs); c.drawCentredString(half+half/2, 2.5*mm, variant)
            c.showPage()
    c.save(); buf.seek(0); return buf

def _wrap(c,text,font,size,width,maxlines=2):
    words=str(text or '').split(); lines=[]; line=''
    for word in words:
        t=(line+' '+word).strip()
        if c.stringWidth(t,font,size)<=width: line=t
        else:
            if line: lines.append(line)
            line=word
            if len(lines)>=maxlines-1: break
    if line and len(lines)<maxlines: lines.append(line)
    return lines

def _image_reader(item):
    local = item.get("image_file")
    if local:
        p = Path(local)
        if not p.is_absolute():
            p = Path(__file__).resolve().parents[1] / p
        if p.exists(): return ImageReader(str(p))
    url = item.get("image")
    if url and str(url).startswith(("http://","https://")):
        r=requests.get(url,timeout=5); r.raise_for_status()
        return ImageReader(io.BytesIO(r.content))
    return None

def _box(c,item,x,y,w,h):
    pad=min(w,h)*.055; cx=x+w/2; top=y+h-pad
    title=str(item.get('title') or ''); var=str(item.get('variant') or '').replace('Default Title','').strip(' ,')
    b=str(item.get('barcode') or ''); p=price_text(item.get('price'))
    fs=max(7,min(11,h/25)); c.setFillColor(colors.black); c.setFont('Helvetica-Bold',fs)
    for line in _wrap(c,title,'Helvetica-Bold',fs,w-2*pad,2): c.drawString(x+pad,top-fs,line); top-=fs*1.15
    c.setFont('Helvetica',max(6,fs*.78))
    for line in _wrap(c,var,'Helvetica',max(6,fs*.78),w-2*pad,2): c.drawString(x+pad,top-fs*.8,line); top-=fs*.9
    c.setFillColor(colors.blue); c.setFont('Helvetica-Bold',max(5,fs*.65)); c.drawString(x+pad,top-fs*.7,'STOCK'); top-=fs*.9; c.setFillColor(colors.black)
    barcode_zone=max(34,h*.18); price_zone=max(16,h*.08); img_bottom=y+pad+barcode_zone+price_zone; img_top=top-2
    img_h=max(0,img_top-img_bottom); img_w=w-2*pad
    try:
        im=_image_reader(item)
        if im and img_h>5:
            iw,ih=im.getSize(); scale=min(img_w/iw,img_h/ih); dw,dh=iw*scale,ih*scale
            c.drawImage(im,cx-dw/2,img_bottom+(img_h-dh)/2,dw,dh,mask='auto')
    except Exception: pass
    if p:
        c.setFillColor(colors.red); c.setFont('Helvetica-Bold',max(9,min(15,fs*1.3)))
        c.drawCentredString(cx,y+pad+barcode_zone+3,p); c.setFillColor(colors.black)
    if len(b)==8 and b.isdigit():
        bh=max(18,barcode_zone*.52); bc=code128.Code128(b,barHeight=bh,barWidth=.55,humanReadable=False)
        maxbw=w-2*pad
        if bc.width>maxbw: bc.barWidth*=maxbw/bc.width
        by=y+pad+10; bc.drawOn(c,cx-bc.width/2,by); c.setFont('Helvetica',max(6,fs*.7)); c.drawCentredString(cx,y+pad,b)

def create_a4_sheet(items,rows=4,columns=3,label_type='box'):
    rows=max(1,int(rows)); columns=max(1,int(columns)); buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=A4); pw,ph=A4; cw,ch=pw/columns,ph/rows; per=rows*columns
    for i,item in enumerate(items):
        if i and i%per==0:c.showPage()
        j=i%per; row=j//columns; col=j%columns
        _box(c,item,col*cw,ph-(row+1)*ch,cw,ch)
    c.save(); buf.seek(0); return buf
