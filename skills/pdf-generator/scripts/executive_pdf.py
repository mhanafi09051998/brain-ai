"""
executive_pdf.py - Modular High-Fidelity PDF Engine (Astra / Fable Design Standard)
Engine ReportLab berstandar korporat eksekutif untuk pembuatan dokumen resmi, studi kasus,
rubrik evaluasi teknis, dan laporan arsitektur sistem.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ==============================================================================
# PALET WARNA ASTRA / FABLE
# ==============================================================================
class Palette:
    SLATE_950 = colors.HexColor('#020617')
    SLATE_900 = colors.HexColor('#0F172A') # Dark Corporate Header & Terminal
    SLATE_800 = colors.HexColor('#1E293B') # Deep Text
    SLATE_600 = colors.HexColor('#475569') # Secondary Text
    SLATE_500 = colors.HexColor('#64748B') # Muted Captions
    SLATE_200 = colors.HexColor('#E2E8F0') # Subtle Dividers
    SLATE_100 = colors.HexColor('#F1F5F9') # Soft Fill
    SLATE_50  = colors.HexColor('#F8FAFC') # Clean Surface Neutral

    FOREST_900 = colors.HexColor('#14532D') # Primary Brand Dark Green
    FOREST_700 = colors.HexColor('#15803D') # Vibrant Brand Green
    FOREST_100 = colors.HexColor('#DCFCE7') # Light Brand Pill Fill
    FOREST_50  = colors.HexColor('#F0FDF4') # Subtle Brand Tint

    SKY_600   = colors.HexColor('#0284C7')  # Info Accent
    AMBER_500 = colors.HexColor('#F59E0B')  # Warning Accent
    ROSE_600  = colors.HexColor('#E11D48')  # Critical Accent
    WHITE     = colors.HexColor('#FFFFFF')

# ==============================================================================
# NUMBERED CANVAS DENGAN TWO-PASS HEADER & FOOTER
# ==============================================================================
class AstraNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.company_name = getattr(self, 'company_name', 'PT CONTOH')
        self.division_name = getattr(self, 'division_name', 'IT KBGroup')
        self.doc_subject = getattr(self, 'doc_subject', 'Dokumen Uji Kompetensi Teknis Full Stack Software Engineer')
        self.assessor_name = getattr(self, 'assessor_name', 'Muhammad Hanafi, S.Tr.Kom')

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        if hasattr(self, 'doc_title') and self.doc_title:
            self.setTitle(self.doc_title)
        if hasattr(self, 'assessor_name') and self.assessor_name:
            self.setAuthor(self.assessor_name)
        if hasattr(self, 'doc_subject') and self.doc_subject:
            self.setSubject(self.doc_subject)
        if hasattr(self, 'company_name') and self.company_name:
            self.setCreator(f"{self.division_name} — {self.company_name}")
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        # Header Rule
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(Palette.FOREST_900)
        self.drawString(36, 810, "PT CONTOH")
        self.setFont("Helvetica", 8)
        self.setFillColor(Palette.SLATE_600)
        self.drawString(98, 810, "|  IT KBGroup  —  Dokumen Uji Kompetensi Teknis Full Stack Software Engineer")
        
        self.setStrokeColor(Palette.SLATE_200)
        self.setLineWidth(0.6)
        self.line(36, 802, 559, 802)

        # Footer Rule
        self.line(36, 36, 559, 36)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(Palette.SLATE_500)
        self.drawString(36, 24, "Lead Asesor: Muhammad Hanafi, S.Tr.Kom (IT KBGroup)  |  Kerahasiaan Dokumen Internal PT Contoh © 2026")
        self.drawRightString(559, 24, f"Halaman {self._pageNumber} dari {page_count}")
        self.restoreState()

# ==============================================================================
# BUILDER HELPER FUNCTIONS
# ==============================================================================
def get_astra_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles['DocTitle'] = ParagraphStyle(
        'AstraTitle',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15.5,
        textColor=Palette.SLATE_900,
        spaceAfter=2
    )

    styles['DocSub'] = ParagraphStyle(
        'AstraSub',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=Palette.FOREST_900,
        spaceAfter=5
    )

    styles['MetaLabel'] = ParagraphStyle(
        'AstraMetaLabel',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=Palette.SLATE_900
    )

    styles['MetaValue'] = ParagraphStyle(
        'AstraMetaVal',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=Palette.SLATE_800
    )

    styles['SectionHeading'] = ParagraphStyle(
        'AstraSectionHead',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=12,
        textColor=Palette.FOREST_900,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    styles['BodyText'] = ParagraphStyle(
        'AstraBody',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=Palette.SLATE_800,
        spaceAfter=2
    )

    styles['QuoteText'] = ParagraphStyle(
        'AstraQuote',
        parent=base['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10.8,
        textColor=Palette.SLATE_900
    )

    styles['BulletItem'] = ParagraphStyle(
        'AstraBullet',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=Palette.SLATE_800,
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=2
    )

    styles['CodeText'] = ParagraphStyle(
        'AstraCode',
        parent=base['Normal'],
        fontName='Courier',
        fontSize=6.6,
        leading=8.3,
        textColor=Palette.SLATE_100
    )

    styles['TerminalHeader'] = ParagraphStyle(
        'AstraTermHead',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor('#94A3B8')
    )

    return styles

def create_callout_box(quote_text, author_name, author_role, styles):
    content = f"\"{quote_text}\"<br/><br/><b>— {author_name}</b>, <i>{author_role}</i>"
    t = Table([[Paragraph(content, styles['QuoteText'])]], colWidths=[523])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), Palette.SLATE_50),
        ('BOX', (0,0), (-1,-1), 0.5, Palette.SLATE_200),
        ('LINELEFT', (0,0), (0,0), 3.0, Palette.FOREST_900),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def create_terminal_code_block(sql_code, label, styles):
    safe_code = sql_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    safe_code = safe_code.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;').replace('  ', '&nbsp;&nbsp;')
    safe_code = safe_code.replace('\n', '<br/>')

    header_bar = [
        [Paragraph(f"<b>TERMINAL:</b> {label.upper()}", styles['TerminalHeader'])]
    ]
    code_body = [
        [Paragraph(safe_code, styles['CodeText'])]
    ]

    t_header = Table(header_bar, colWidths=[523])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E293B')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))

    t_body = Table(code_body, colWidths=[523])
    t_body.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), Palette.SLATE_900),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))

    return [t_header, t_body]
