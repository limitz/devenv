#!/usr/bin/env python3
"""Build an A4 illustrated routine PDF (reportlab platypus) from a content module and rendered figures.

usage: build_pdf.py --content CONTENT.py --figures FIG_DIR --out routine.pdf

CONTENT.py schema: see references/layout.md (TITLE, RUNNING_HEADER, SUMMARY, CONSTRAINTS, SESSION_MAP,
STOP_RULES, STOP_NOTE, SECTIONS, FREQUENCY, ADDING_LOAD, LOAD_STEPS, GOOD_SESSION, CLOSING, CREDITS,
CREDITS_JSON_NOTE, HOLD_TITLE, HOLD_INTRO, HOLD_LIST, APPENDIX_NOTE, APPENDICES). Optional blocks may be omitted (set to None / empty).
"""
import os, re, json, sys, argparse, importlib.util
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                                KeepTogether, PageBreak, Flowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

INK, MUTED, ACCENT, RULE, BAND = '#1b2a33', '#6b7f8a', '#c2483a', '#d5dee2', '#f2f6f7'
MARGIN = 16 * mm
PAGE_W, PAGE_H = A4
BODY_W = PAGE_W - 2 * MARGIN
IMG_COL = 53 * mm
IMG_W, IMG_H = 50 * mm, 36 * mm

# Helvetica lacks U+2192 and U+25B2; borrow them from DejaVu Sans (ships with matplotlib)
try:
    import matplotlib
    dv = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf', 'DejaVuSans.ttf')
    pdfmetrics.registerFont(TTFont('DejaVuSans', dv))
    ARROW = '<font name="DejaVuSans">→</font>'
    FLAG = f'<font color="{ACCENT}" name="DejaVuSans">▲</font>'
except Exception:
    ARROW, FLAG = 'to', f'<font color="{ACCENT}">!</font>'

def md(s):
    """**bold**, *italic*, and the → glyph"""
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', s)
    return s.replace('→', ARROW)

S = {
    'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=INK, spaceAfter=4 * mm),
    'summary': ParagraphStyle('summary', fontName='Helvetica', fontSize=10.5, leading=14.5, textColor=INK, spaceAfter=7 * mm),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=11.5, leading=14, textColor=INK, spaceBefore=4 * mm, spaceAfter=2 * mm),
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=9.6, leading=13, textColor=INK),
    'muted': ParagraphStyle('muted', fontName='Helvetica', fontSize=9.4, leading=12.6, textColor=MUTED),
    'label': ParagraphStyle('label', fontName='Helvetica-Bold', fontSize=9.4, leading=12.6, textColor=INK),
    'stop': ParagraphStyle('stop', fontName='Helvetica', fontSize=9.8, leading=13.4, textColor=ACCENT),
    'exname': ParagraphStyle('exname', fontName='Helvetica-Bold', fontSize=10.6, leading=13, textColor=INK),
    'dose': ParagraphStyle('dose', fontName='Helvetica', fontSize=9.2, leading=12, textColor=ACCENT, spaceBefore=0.6 * mm, spaceAfter=1.4 * mm),
    'cue': ParagraphStyle('cue', fontName='Helvetica', fontSize=9.1, leading=12.2, textColor=INK),
    'flag': ParagraphStyle('flag', fontName='Helvetica-Oblique', fontSize=8.8, leading=11.8, textColor=MUTED, spaceBefore=1.0 * mm),
    'secnum': ParagraphStyle('secnum', fontName='Helvetica-Bold', fontSize=30, leading=32, textColor=ACCENT),
    'sectitle': ParagraphStyle('sectitle', fontName='Helvetica-Bold', fontSize=13.5, leading=16, textColor=INK),
    'secsub': ParagraphStyle('secsub', fontName='Helvetica', fontSize=9.4, leading=12, textColor=MUTED),
    'num': ParagraphStyle('num', fontName='Helvetica-Bold', fontSize=9.6, leading=13, textColor=ACCENT),
    'small': ParagraphStyle('small', fontName='Helvetica', fontSize=8.4, leading=11, textColor=MUTED),
}

def hr(width=BODY_W, color=RULE, thickness=0.5, space=1.5 * mm):
    class HR(Flowable):
        def wrap(self, aw, ah): return width, thickness + space
        def draw(self):
            self.canv.setStrokeColor(colors.HexColor(color)); self.canv.setLineWidth(thickness)
            self.canv.line(0, space / 2, width, space / 2)
    return HR()

def kv_table(rows, label_w=36 * mm, label_style='label', text_style='body'):
    data = [[Paragraph(md(a), S[label_style]), Paragraph(md(b), S[text_style])] for a, b in rows]
    t = Table(data, colWidths=[label_w, BODY_W - label_w])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, colors.HexColor(RULE)),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2 * mm), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2 * mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 3 * mm),
    ]))
    return t

def session_map_table(rows):
    data = [[Paragraph(str(n), S['num']), Paragraph(md(name), S['label']), Paragraph(t, S['muted']), Paragraph(md(note), S['body'])]
            for n, name, t, note in rows]
    t = Table(data, colWidths=[8 * mm, 34 * mm, 16 * mm, BODY_W - 58 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, colors.HexColor(RULE)),
        ('TOPPADDING', (0, 0), (-1, -1), 2.0 * mm), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0 * mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 3 * mm),
    ]))
    return t

def section_header(num, title, duration, subtitle):
    left = Paragraph(str(num), S['secnum'])
    dur = f'<font color="{MUTED}" size="9.4">&nbsp;&nbsp;·&nbsp;&nbsp;{duration}</font>' if duration else ''
    right = [Paragraph(f'{md(title)}{dur}', S['sectitle'])]
    if subtitle:
        right.append(Paragraph(md(subtitle), S['secsub']))
    t = Table([[left, right]], colWidths=[16 * mm, BODY_W - 16 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(BAND)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5 * mm), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5 * mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 4 * mm), ('RIGHTPADDING', (0, 0), (-1, -1), 4 * mm),
    ]))
    return t

def exercise_row(ex, fig_dir):
    n, name, dose, cues, flag = ex
    img = Image(os.path.join(fig_dir, f'{n:02d}.png'), width=IMG_W, height=IMG_H)
    txt = [Paragraph(f'<font color="{ACCENT}">{n}</font>&nbsp;&nbsp;{md(name)}', S['exname']),
           Paragraph(md(dose), S['dose']),
           Paragraph(md(cues), S['cue'])]
    if flag:
        txt.append(Paragraph(f'{FLAG}&nbsp; {md(flag)}', S['flag']))
    t = Table([[img, txt]], colWidths=[IMG_COL, BODY_W - IMG_COL])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, colors.HexColor(RULE)),
        ('TOPPADDING', (0, 0), (-1, -1), 1.6 * mm), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6 * mm),
        ('LEFTPADDING', (0, 0), (0, 0), 0), ('RIGHTPADDING', (0, 0), (0, 0), 3 * mm),
        ('LEFTPADDING', (1, 0), (1, 0), 2 * mm), ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))
    return KeepTogether(t)

def make_on_page(header):
    def on_page(canv, doc):
        if doc.page == 1:
            return
        canv.saveState()
        canv.setFont('Helvetica', 8.4); canv.setFillColor(colors.HexColor(MUTED))
        y = PAGE_H - MARGIN + 4 * mm
        canv.drawString(MARGIN, y, header)
        canv.drawRightString(PAGE_W - MARGIN, y, str(doc.page))
        canv.setStrokeColor(colors.HexColor(RULE)); canv.setLineWidth(0.5)
        canv.line(MARGIN, y - 2 * mm, PAGE_W - MARGIN, y - 2 * mm)
        canv.restoreState()
    return on_page

def build(C, fig_dir, out):
    g = lambda k, d=None: getattr(C, k, d)
    global IMG_W, IMG_H
    if g('FIG_H_MM'):                      # optional per-routine figure cap (e.g. 35) when a six-row section spills
        IMG_H = float(C.FIG_H_MM) * mm
        IMG_W = IMG_H * 50 / 36
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN + 3 * mm, bottomMargin=MARGIN,
                            title=re.sub('<[^>]+>|&amp;', lambda m: '&' if m.group(0) == '&amp;' else '', C.TITLE),
                            subject=g('SUMMARY', ''))
    st = [Paragraph(C.TITLE, S['title'])]
    if g('SUMMARY'): st.append(Paragraph(md(C.SUMMARY), S['summary']))
    if g('CONSTRAINTS'):
        st += [Paragraph(g('CONSTRAINTS_TITLE', 'Working constraints'), S['h2']), kv_table(C.CONSTRAINTS)]
    if g('SESSION_MAP'):
        st += [Paragraph('Session map', S['h2']), session_map_table(C.SESSION_MAP)]
    if g('APPENDIX_NOTE'):
        st += [Spacer(1, 2 * mm), Paragraph(md(C.APPENDIX_NOTE), S['muted'])]
    if g('STOP_RULES'):
        st += [Paragraph('Stop rules', S['h2']), Paragraph(md(C.STOP_RULES), S['stop'])]
    if g('STOP_NOTE'):
        st += [Spacer(1, 3 * mm), Paragraph(md(C.STOP_NOTE), S['muted'])]
    def section_page(sec):
        st.append(PageBreak())
        st.append(section_header(sec['num'], sec['title'], sec.get('duration', ''), sec.get('subtitle', '')))
        st.append(Spacer(1, 1.5 * mm))
        if sec.get('intro'):
            st.extend([Paragraph(md(sec['intro']), S['muted']), Spacer(1, 1.5 * mm)])
        for ex in sec['exercises']:
            st.append(exercise_row(ex, fig_dir))
    for sec in C.SECTIONS:
        section_page(sec)
    tail = any(g(k) for k in ('FREQUENCY', 'ADDING_LOAD', 'LOAD_STEPS', 'GOOD_SESSION', 'CLOSING', 'CREDITS'))
    if tail:
        st.append(PageBreak())
        st.append(Paragraph(g('FINAL_TITLE', 'Progression &amp; scheduling'), S['sectitle']))
        st.append(Spacer(1, 2 * mm))
        if g('FREQUENCY'):
            st += [Paragraph('Frequency', S['h2']), kv_table(C.FREQUENCY)]
        if g('ADDING_LOAD'):
            st += [Paragraph(g('ADDING_LOAD_TITLE', 'Adding load back'), S['h2']), Paragraph(md(C.ADDING_LOAD), S['body']), Spacer(1, 2 * mm)]
        if g('LOAD_STEPS'):
            steps = [[Paragraph(str(i + 1), S['num']), Paragraph(md(s), S['body'])] for i, s in enumerate(C.LOAD_STEPS)]
            t = Table(steps, colWidths=[8 * mm, BODY_W - 8 * mm])
            t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                   ('TOPPADDING', (0, 0), (-1, -1), 1.0 * mm), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.0 * mm)]))
            st.append(t)
        if g('GOOD_SESSION'):
            st += [Paragraph(g('GOOD_SESSION_TITLE', 'What a good session feels like'), S['h2']), Paragraph(md(C.GOOD_SESSION), S['body'])]
        if g('CLOSING'):
            st += [Spacer(1, 4 * mm), Paragraph(md(C.CLOSING), S['stop'])]
        if g('CREDITS'):
            st += [Spacer(1, 10 * mm), hr(), Paragraph('Image credits', S['h2']), Paragraph(md(C.CREDITS), S['small'])]
    if g('HOLD_LIST'):                          # explicit no-go list: what is deliberately left out and what unlocks it
        st.append(PageBreak())
        st.append(Paragraph(g('HOLD_TITLE', 'On hold'), S['sectitle']))
        st.append(Spacer(1, 2 * mm))
        if g('HOLD_INTRO'):
            st += [Paragraph(md(C.HOLD_INTRO), S['muted']), Spacer(1, 3 * mm)]
        st.append(kv_table(C.HOLD_LIST, label_w=46 * mm))
    for app in (g('APPENDICES') or []):        # optional add-on blocks after the progression page; num is a letter
        section_page(app)
    doc.build(st, onFirstPage=make_on_page(C.RUNNING_HEADER), onLaterPages=make_on_page(C.RUNNING_HEADER))
    cj = os.path.join(os.path.dirname(os.path.abspath(out)), 'credits.json')
    json.dump({'third_party_images': list(g('THIRD_PARTY_IMAGES', []) or []), 'note': g('CREDITS_JSON_NOTE', '')},
              open(cj, 'w'), indent=2)
    print('wrote', out, 'and', cj)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--figures', default='figures')
    ap.add_argument('--out', default='routine.pdf')
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('content_mod', args.content)
    C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
    build(C, args.figures, args.out)
