---
name: document-controller
description: Standar, arsitektur, dan protokol Document Controller (Pengendali Dokumen) korporat & teknis berbasis ISO 9001:2015 (Klausul 7.5), sistem Electronic Document Management System (EDMS), serta implementasi perangkat lunak (Laravel/PHP & Node.js). Aktifkan skill ini ketika pengguna meminta pengelolaan siklus hidup dokumen, sistem penomoran dokumen/transmittal, metadata registrasi (MDR), alur persetujuan (Review & Approval Workflow), kontrol revisi, audit trail, atau pembangunan aplikasi Document Controller / Document Management System (DMS).
---

# 📑 Enterprise Document Controller & EDMS Architecture Skill

Skill ini adalah standar operasional dan acuan teknis komprehensif untuk peran **Document Controller (DC)**, manajemen informasi terdokumentasi korporat (*ISO 9001:2015 Clause 7.5*), serta perancangan perangkat lunak **Electronic Document Management System (EDMS / DMS)** berbasis Laravel dan arsitektur modern.

---

## 1. Fondasi Standar: ISO 9001:2015 (Klausul 7.5 Informasi Terdokumentasi)

Setiap sistem pengendalian dokumen yang andal wajib memenuhi 4 pilar utama kepatuhan mutu:

1. **Pembuatan & Identifikasi Unik (*Creation & Identification*)**:
   - Setiap dokumen wajib memiliki identitas tunggal: Judul, Nomor Dokumen Unik, Tanggal Efektif, Penulis (*Author*), dan Status Revisi.
   - Menggunakan format baku dan media yang terlindungi dari manipulasi ilegal.
2. **Peninjauan & Pengesahan (*Review & Approval*)**:
   - Dokumen tidak boleh dirilis ke publik/lapangan tanpa bukti pengesahan berjenjang (*dual/multi-signature approval*).
   - Matriks otorisasi membedakan hak *Originator*, *Reviewer*, dan *Approver*.
3. **Pengendalian Distribusi & Akses (*Distribution & Access*)**:
   - Dokumen yang beredar di titik penggunaan (*point of use*) wajib merupakan versi paling mutakhir (*Current Valid Version*).
   - Mencegah penggunaan dokumen kadaluarsa (*obsolete*) secara tidak sengaja.
4. **Audit Trail & Jejak Perubahan (*Traceability*)**:
   - Setiap revisi wajib mendokumentasikan ringkasan perubahan (*Revision History / Delta Changes*), identitas pelaku perubahan, dan alasan revisi.

---

## 2. Sistem Penomoran Standar Dokumen & Transmittal

Standar penomoran dokumen teknik dan korporat mengadopsi struktur kode semantik modular:

```
[PROJECT] - [ORIGINATOR] - [RECEIVER] - [DOC_TYPE] - [DISCIPLINE] - [SEQUENCE] - [REV]
Contoh   : TRN-ENG-CLT-REP-ARC-0012-01
```

### Komponen Kode:
- **`PROJECT`**: Kode unik proyek (misal: `TRN` untuk Train System, `BIO` untuk Biografi).
- **`ORIGINATOR`**: Kode departemen/perusahaan pembuat (misal: `ENG` = Engineering, `QA` = Quality Assurance).
- **`RECEIVER`**: Pihak penerima (misal: `CLT` = Client, `CTR` = Contractor, `INT` = Internal).
- **`DOC_TYPE`**: Format dokumen:
  - `REP`: Laporan Teknis (*Technical Report*)
  - `SPE`: Spesifikasi Teknis (*Technical Specification*)
  - `DWG`: Gambar Teknik (*Engineering Drawing*)
  - `SOP`: Standar Operasional Prosedur
  - `TRN`: Document Transmittal Notice
  - `MDR`: Master Document Register
- **`DISCIPLINE`**: Bidang keilmuan (`ARC` = Arsitektur, `CIV` = Sipil, `ELE` = Elektrikal, `SOF` = Software/IT).
- **`SEQUENCE`**: Nomor urut 4 digit (`0001` s/d `9999`).
- **`REVISION`**:
  - `Rev A, B, C...`: Fase Draft / Internal Review (Belum disahkan).
  - `Rev 0, 1, 2...`: Fase Rilis / Disetujui (Approved for Construction / Release).

### Format Transmittal Notice (Surat Pengantar Dokumen)
Surat transmittal wajib mencantumkan:
- **Nomor Transmittal**: `TRN-[PROJECT]-[YEAR]-[SEQ]`
- **Tujuan Pengiriman (*Purpose of Issue*)**:
  - `IFI`: *Issued for Information*
  - `IFR`: *Issued for Review*
  - `IFA`: *Issued for Approval*
  - `IFC`: *Issued for Construction / Release*
  - `ASB`: *As-Built Final Record*
- **Kode Respons Reviewer (*Approval Action Code*)**:
  - **Code 1**: Disetujui Penuh (*Approved / Work May Proceed*).
  - **Code 2**: Disetujui dengan Catatan Revisi (*Approved Except as Noted*).
  - **Code 3**: Ditolak, Wajib Diperbaiki & Diajukan Ulang (*Rejected / Revise & Resubmit*).
  - **Code 4**: Hanya untuk Informasi (*Information Only*).

---

## 3. Master Document Register (MDR / DCI)

MDR adalah basis data induk pengendali seluruh dokumen dalam suatu organisasi atau proyek.

| No | Nomor Dokumen | Judul Dokumen | Disiplin | Rev | Status | Tgl Pengajuan | Tgl Persetujuan | Kode Respon | Lokasi Berkas |
| :- | :--- | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :--- |
| 1 | TRN-QA-INT-SOP-SOF-0001 | Standar Koding & Pengujian | IT | 0 | Released | 2026-09-01 | 2026-09-02 | Code 1 | `storage/docs/0001.pdf` |
| 2 | TRN-ENG-CTR-SPE-ARC-0002 | Desain Arsitektur Sistem | IT | 1 | Released | 2026-09-05 | 2026-09-07 | Code 1 | `storage/docs/0002.pdf` |
| 3 | TRN-PM-CLT-REP-MGT-0003 | Laporan Progres Mingguan | PM | B | Under Review| 2026-09-08 | — | Pending | `storage/docs/0003.pdf` |

---

## 4. Arsitektur Software Document Management System (Laravel DMS)

Jika mengimplementasikan controller dokumen dalam Laravel, terapkan prinsip **Service-Oriented Architecture (SOA)**, **Integritas Kriptografis**, dan **State Machine**.

### A. Skema Database Relasional

```
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│              documents               │ 1   * │          document_revisions          │
├──────────────────────────────────────┤───────├──────────────────────────────────────┤
│ id (PK)                              │       │ id (PK)                              │
│ document_number (Unique Index)       │       │ document_id (FK)                     │
│ title, category, discipline          │       │ revision_code (e.g. 'Rev 0', 'Rev A')│
│ current_revision (e.g. 'Rev 0')      │       │ file_path, file_size, mime_type      │
│ status (Draft, In_Review, Approved)  │       │ checksum_sha256 (Hash Integritas)    │
│ originator_id, approver_id           │       │ change_summary                       │
│ is_confidential (Boolean)            │       │ created_by (User FK)                 │
│ created_at, updated_at               │       │ created_at                           │
└──────────────────────────────────────┘       └──────────────────────────────────────┘
                   │ 1
                   │
                   ▼ *
┌──────────────────────────────────────┐
│         document_audit_logs          │
├──────────────────────────────────────┤
│ id (PK), document_id (FK)            │
│ user_id, action (UPLOAD, APPROVE)    │
│ old_status, new_status               │
│ ip_address, user_agent, timestamp    │
└──────────────────────────────────────┘
```

### B. Controller Standar (`DocumentController.php`)

```php
namespace App\Http\Controllers;

use App\Models\Document;
use App\Services\DocumentControlService;
use Illuminate\Http\Request;

class DocumentController extends Controller
{
    protected DocumentControlService $docService;

    public function __construct(DocumentControlService $docService)
    {
        $this->docService = $docService;
    }

    public function uploadRevision(Request $request, Document $document)
    {
        $this->authorize('update', $document);

        $validated = $request->validate([
            'revision_code' => 'required|string|max:10',
            'file' => 'required|file|mimes:pdf,docx,xlsx|max:51200', // max 50MB
            'change_summary' => 'required|string|max:1000',
        ]);

        $revision = $this->docService->addRevision(
            document: $document,
            uploadedFile: $request->file('file'),
            revisionCode: $validated['revision_code'],
            changeSummary: $validated['change_summary'],
            userId: auth()->id()
        );

        return response()->json([
            'status' => 'success',
            'message' => 'Revisi dokumen berhasil dicatat ke sistem audit.',
            'data' => $revision,
        ]);
    }
}
```

### C. Keamanan & Integritas File
1. **Pengecekan Checksum SHA-256**: Simpan hash SHA-256 pada setiap upload untuk memastikan berkas tidak mengalami manipulasi di disk storage.
2. **Private Storage & Signed URLs**: Jangan letakkan berkas terkontrol di direktori `public/`. Gunakan `Storage::disk('private')` dan otorisasi lewat *temporary signed URLs*.
3. **Immutability Revisi**: Berkas yang sudah berstatus `Approved` tidak boleh ditimpa (*no file overwrite*). Setiap perbaikan wajib menghasilkan baris baru pada tabel `document_revisions`.

---

## 5. Referensi Repositori Open-Source Teruji

1. **[harish81/digidocu](https://github.com/harish81/digidocu)**:
   - Platform DMS open-source Laravel terlengkap dengan fitur kompresi gambar, penggabungan PDF (*PDF combiner*), dan manajemen arsip zip.
2. **[singhateh/Laravel-11-Document-Management-System](https://github.com/singhateh/Laravel-11-Document-Management-System)**:
   - Implementasi modern berbasis Laravel 11 dengan Role-Based Access Control (RBAC), notifikasi email alur persetujuan, dan keamanan berkas.
3. **[kyotaka7/Documents_managment_system](https://github.com/kyotaka7/Documents_managment_system)**:
   - Sistem DocuVerse untuk manajemen berkas terpusat dengan autentikasi berjenjang.
