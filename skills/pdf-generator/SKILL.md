---
name: pdf-generator
description: Panduan dan standar pembuatan dokumen PDF korporat eksekutif profesional menggunakan ReportLab di Python dengan standar desain Astra & Fable. Aktifkan skill ini ketika pengguna meminta pembuatan dokumen PDF resmi, laporan bisnis, lembar studi kasus teknis, rubrik penilaian, atau dokumen formal yang membutuhkan tipografi bersih, layout presisi, running header/footer, dan tanpa elemen visual informal/kekanak-kanakan.
---

# 📄 Executive PDF Generator Skill (ReportLab Engine — Astra & Fable Standards)

Skill ini adalah instrumen standar untuk menghasilkan dokumen PDF resmi berskala eksekutif korporat (*enterprise grade*), mengadopsi standar desain dokumen publikasi **Astra / Fable** (terinspirasi dari Linear, Stripe Press, Apple, dan McKinsey Technical Briefs).

---

## 1. Prinsip Desain Dokumen Astra / Fable

1. **Zero Informal / Childish Elements:**
   * Dilarang menggunakan emoji visual (seperti ⏱, ★, 🚀, 💡, 📋, 💬).
   * Gunakan penomoran formal desimal (`1.1`, `1.2`), bullet point standar (`•`), atau bullet teks formal (`[1]`, `[a]`).
2. **Strict Page Budget & Optical Balance:**
   * Setiap dokumen dirancang dengan target halaman pasti (misal: tepat 2 halaman untuk studi kasus teknis).
   * Gunakan `PageBreak()` secara sadar untuk memisahkan domain masalah bisnis (Halaman 1) dari domain arsitektur teknis (Halaman 2).
   * Hindari elemen menggantung (*orphan / widow lines*) dengan mengontrol rasio `fontSize` dan `leading` secara proporsional:
     - Heading 1: `fontSize: 12.5–13 pt`, `leading: 15.5–16 pt`
     - Section Head: `fontSize: 9.2–9.5 pt`, `leading: 12–12.5 pt`
     - Body Text: `fontSize: 7.8–8.2 pt`, `leading: 10.8–11.5 pt`
     - Monospace Code: `fontSize: 6.6–7 pt`, `leading: 8.3–9 pt`
3. **Executive Corporate Color Palette:**
   * **Corporate Forest Green:** `#14532D` (Primary Brand & Accent Headings)
   * **Corporate Dark Slate:** `#0F172A` (Text Primary, Title, & Terminal Background)
   * **Secondary Text Slate:** `#475569` / `#64748B` (Subtitles & Footers)
   * **Subtle Hairline Borders:** `#E2E8F0` / `#CBD5E1`
   * **Surface Background Neutral:** `#F8FAFC` (Callout & Meta Grid Fill)
   * **Terminal Code Monospace:** `#F1F5F9` on `#0F172A`

---

## 2. Arsitektur Two-Pass NumberedCanvas (Header & Footer Resmi)

Gunakan subclass `canvas.Canvas` untuk menghitung total halaman dokumen secara otomatis dan mencetak running header serta footer "Halaman X dari Y" tanpa overflow:

```python
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class ExecutiveNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

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

    def draw_decorations(self, page_count):
        self.saveState()
        # Running Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#14532D"))
        self.drawString(36, 810, "PT CONTOH")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(100, 810, "|  IT KBGroup  —  Dokumen Uji Kompetensi Teknis")
        
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 802, 559, 802)

        # Running Footer
        self.line(36, 36, 559, 36)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 24, "Lead Asesor: Muhammad Hanafi, S.Tr.Kom (IT KBGroup)  |  Kerahasiaan Dokumen Internal PT Contoh © 2026")
        self.drawRightString(559, 24, f"Halaman {self._pageNumber} dari {page_count}")
        self.restoreState()
```

---

## 3. Komponen Standar Astra / Fable

### A. Metadata Matrix Card
Tabel metadata 3 atau 4 kolom dengan background `#F8FAFC` dan hairline grid `#E2E8F0`:
```python
meta_table = Table(meta_data, colWidths=[175, 175, 173])
meta_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
    ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#CBD5E1')),
    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
]))
```

### B. Executive Callout Box (Stakeholder Persona Quote)
Kotak kutipan dengan aksen garis kiri 3.0 pt berwarna hijau korporat `#14532D`:
```python
quote_table = Table([[Paragraph(f"\"{quote}\"<br/><br/><b>— {author}</b>, <i>{role}</i>", quote_style)]], colWidths=[523])
quote_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ('LINELEFT', (0,0), (0,0), 3.0, colors.HexColor('#14532D')),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
```

### C. Dark Terminal Code Block (SQL / Monospace Snippet)
Blok kode monokromatik gelap (`#0F172A`) dengan teks Courier `#E2E8F0`:
```python
def format_sql(sql_text):
    safe = sql_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    safe = safe.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;').replace('  ', '&nbsp;&nbsp;')
    return safe.replace('\n', '<br/>')

code_table = Table([[Paragraph(format_sql(sql_code), code_style)]], colWidths=[523])
code_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
```

---

## 4. Standar Metadata PDF (Mencegah Judul "Anonymous" di Browser)

Secara default, ReportLab men-set metadata `/Title` dan `/Author` bernilai `(anonymous)` jika tidak didefinisikan secara eksplisit. Akibatnya, peramban web (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari) akan menampilkan kata **"anonymous"** pada tab browser.

Untuk mencegahnya, **WAJIB** menyematkan atribut metadata saat inisialisasi `SimpleDocTemplate`:

```python
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    leftMargin=36,
    rightMargin=36,
    topMargin=44,
    bottomMargin=44,
    title="Kandidat 1 - Sistem Kepatuhan CPOTB | PT Contoh (IT KBGroup)",
    author="Muhammad Hanafi, S.Tr.Kom (IT KBGroup)",
    subject="Uji Kompetensi Teknis Full Stack Software Engineer - HRD & Legal",
    creator="IT KBGroup - PT Contoh"
)
```
Dengan parameter di atas, judul tab di peramban web akan menampilkan nama dokumen resmi yang rapi dan profesional.

---

## 5. Modul Reusable

Engine Python siap pakai dapat diimpor langsung dari:
`skills/pdf-generator/scripts/executive_pdf.py`

Contoh penggunaan:
```python
from executive_pdf import AstraNumberedCanvas, get_astra_styles, create_callout_box, create_terminal_code_block
```

