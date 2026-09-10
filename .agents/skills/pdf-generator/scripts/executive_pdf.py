"""
executive_pdf.py - Modular High-Fidelity PDF Engine (Astra / Fable Design Standard)
Engine ReportLab berstandar korporat eksekutif untuk pembuatan dokumen resmi, studi kasus,
rubrik evaluasi teknis, dan laporan arsitektur sistem.

Dependensi: reportlab>=4 (`pip install reportlab`).

Contoh penggunaan minimal:

    from executive_pdf import create_document, get_astra_styles, make_canvas
    from reportlab.platypus import Paragraph

    styles = get_astra_styles()
    doc = create_document(
        "laporan.pdf",
        title="Laporan Arsitektur Sistem",
        author="Nama Penulis",
        subject="Ringkasan teknis",
        creator="Divisi IT - PT Contoh",
    )
    doc.build(
        [Paragraph("Judul", styles["DocTitle"]), Paragraph("Isi dokumen.", styles["BodyText"])],
        canvasmaker=make_canvas(company_name="PT CONTOH", division_name="Divisi IT",
                                doc_subject="Laporan Arsitektur", author_name="Nama Penulis"),
    )
"""

from datetime import date
from typing import Any, Dict, List, Type

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

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


# Lebar area konten A4 dengan margin kiri/kanan 36 pt (595 - 72)
CONTENT_WIDTH = 523
PAGE_MARGIN_X = 36
PAGE_RIGHT_X = 559

# ==============================================================================
# NUMBERED CANVAS DENGAN TWO-PASS HEADER & FOOTER
# ==============================================================================
class AstraNumberedCanvas(canvas.Canvas):
    """Canvas two-pass: menghitung total halaman lalu menggambar running header/footer
    "Halaman X dari Y". Teks header/footer diambil dari atribut kelas berikut dan dapat
    dikustomisasi per dokumen melalui `make_canvas(...)` tanpa mengubah kelas ini."""

    company_name: str = "PT CONTOH"
    division_name: str = "IT KBGroup"
    doc_subject: str = "Dokumen Uji Kompetensi Teknis Full Stack Software Engineer"
    author_label: str = "Lead Asesor"
    author_name: str = "Muhammad Hanafi, S.Tr.Kom"
    confidentiality_note: str = "Kerahasiaan Dokumen Internal"
    doc_year: int = date.today().year

    CONFIGURABLE_ATTRS = (
        "company_name", "division_name", "doc_subject", "author_label",
        "author_name", "confidentiality_note", "doc_year",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def header_text(self) -> str:
        return f"|  {self.division_name}  —  {self.doc_subject}"

    def footer_text(self) -> str:
        return (
            f"{self.author_label}: {self.author_name} ({self.division_name})  |  "
            f"{self.confidentiality_note} {self.company_name} © {self.doc_year}"
        )

    def draw_decorations(self, page_count: int) -> None:
        self.saveState()
        # Header Rule
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(Palette.FOREST_900)
        self.drawString(PAGE_MARGIN_X, 810, self.company_name)
        company_width = self.stringWidth(self.company_name, "Helvetica-Bold", 8)
        self.setFont("Helvetica", 8)
        self.setFillColor(Palette.SLATE_600)
        self.drawString(PAGE_MARGIN_X + company_width + 6, 810, self.header_text())

        self.setStrokeColor(Palette.SLATE_200)
        self.setLineWidth(0.6)
        self.line(PAGE_MARGIN_X, 802, PAGE_RIGHT_X, 802)

        # Footer Rule
        self.line(PAGE_MARGIN_X, 36, PAGE_RIGHT_X, 36)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(Palette.SLATE_500)
        self.drawString(PAGE_MARGIN_X, 24, self.footer_text())
        self.drawRightString(PAGE_RIGHT_X, 24, f"Halaman {self._pageNumber} dari {page_count}")
        self.restoreState()


def make_canvas(**overrides: Any) -> Type[AstraNumberedCanvas]:
    """Membuat subclass `AstraNumberedCanvas` dengan teks header/footer kustom.
    Hasilnya diberikan ke `SimpleDocTemplate.build(story, canvasmaker=...)`."""
    unknown = set(overrides) - set(AstraNumberedCanvas.CONFIGURABLE_ATTRS)
    if unknown:
        raise TypeError(
            f"Atribut tidak dikenal: {sorted(unknown)}. "
            f"Yang didukung: {list(AstraNumberedCanvas.CONFIGURABLE_ATTRS)}"
        )
    return type("ConfiguredAstraCanvas", (AstraNumberedCanvas,), dict(overrides))


def create_document(
    pdf_path: str,
    *,
    title: str,
    author: str,
    subject: str,
    creator: str,
    pagesize=A4,
    top_margin: float = 44,
    bottom_margin: float = 44,
) -> SimpleDocTemplate:
    """Membuat `SimpleDocTemplate` A4 standar Astra dengan metadata PDF wajib
    (mencegah judul "anonymous" di tab peramban)."""
    return SimpleDocTemplate(
        pdf_path,
        pagesize=pagesize,
        leftMargin=PAGE_MARGIN_X,
        rightMargin=PAGE_MARGIN_X,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
        title=title,
        author=author,
        subject=subject,
        creator=creator,
    )

# ==============================================================================
# BUILDER HELPER FUNCTIONS
# ==============================================================================
def get_astra_styles() -> Dict[str, ParagraphStyle]:
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


def escape_paragraph_text(text: str) -> str:
    """Meng-escape karakter markup ReportLab (&, <, >) agar teks bebas tampil apa adanya."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def create_callout_box(quote_text: str, author_name: str, author_role: str, styles: Dict[str, ParagraphStyle]) -> Table:
    content = (
        f"\"{escape_paragraph_text(quote_text)}\"<br/><br/>"
        f"<b>— {escape_paragraph_text(author_name)}</b>, <i>{escape_paragraph_text(author_role)}</i>"
    )
    t = Table([[Paragraph(content, styles['QuoteText'])]], colWidths=[CONTENT_WIDTH])
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


def create_terminal_code_block(sql_code: str, label: str, styles: Dict[str, ParagraphStyle]) -> List[Table]:
    safe_code = escape_paragraph_text(sql_code)
    safe_code = safe_code.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;').replace('  ', '&nbsp;&nbsp;')
    safe_code = safe_code.replace('\n', '<br/>')

    header_bar = [
        [Paragraph(f"<b>TERMINAL:</b> {escape_paragraph_text(label.upper())}", styles['TerminalHeader'])]
    ]
    code_body = [
        [Paragraph(safe_code, styles['CodeText'])]
    ]

    t_header = Table(header_bar, colWidths=[CONTENT_WIDTH])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E293B')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))

    t_body = Table(code_body, colWidths=[CONTENT_WIDTH])
    t_body.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), Palette.SLATE_900),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))

    return [t_header, t_body]
