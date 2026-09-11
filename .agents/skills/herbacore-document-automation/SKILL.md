---
name: herbacore-document-automation
description: Procedural standards and formatting rules for PT. Herbacore internal documents, forms, and templates (especially Formulir Permintaan Barang dan Jasa).
---

# PT. Herbacore Document Automation Standard

## 1. Active Template Specification
* **Document Number**: `L01.02-P05.01.001`
* **Title**: `FORMULIR PERMINTAAN BARANG DAN JASA`
* **Revision**: `02`
* **Effective Date**: `1 Juli 2026`
* **Approval Matrix**: 5-party approval hierarchy:
  1. `User` (Dibuat oleh)
  2. `SPV` (Diperiksa oleh)
  3. `Kepala Bagian/Manajer` (Diperiksa dan Disetujui oleh)
  4. `COO/CMO & CPO/CFO` (Diterima oleh)
  5. `CEO`
* **Footnote Rule**: *"Permintaan barang dan jasa yang tercantum dalam RKA maupun tidak, approval-nya sesuai matriks persetujuan pada bagian/dept. masing-masing. Jika permintaan barang dan jasa di luar RKA tambahkan 'Non-Budgeter' pada deskripsi di kolom keterangan."*

## 2. 2-Half Page Layout & Physical Cutting Invariant
* **Paper Sizing**: Folio / F4 (215 x 330 mm, 612 pt x 936 pt).
* **2-Form Structure**: 1 single printed sheet contains 2 forms (Form 1 on the top half, Form 2 on the bottom half) separated by a dashed cutting line.
* **1-Page Strict Invariant**: The entire document MUST fit on **exactly 1 page**. If elements spill to page 2, the printout cannot be cut in half cleanly.

## 3. Cell-Bawah Continuation Method (Format Sambungan Sel)
* **Zero Cell-Height Bloat**: Never allow long text (multi-line specs or URL links) to wrap inside a single cell and expand its height vertically.
* **Row-Splitting Protocol**:
  * **Primary Row**: Item number, main product name, unit, quantity, estimated price, date, and requirement description.
  * **Continuation Row (Cell Bawahnya)**: Item number left blank, specifications/socket in the product name column, and purchase URL link in the Keterangan column.
* **Pagination Balance**:
  * Form 1 holds the first set of items (e.g. Items 1–5 using 2 rows each = 10 rows).
  * Form 2 holds the continuation items with continuing sequential numbers (e.g. Items 6–11).
  * Subtotals in the `JUMLAH` row must correctly sum the quantities and amounts for their respective form, with grand totals matching across both forms.
