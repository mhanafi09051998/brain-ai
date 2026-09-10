# Spesifikasi Multi-Task Flow: Alur Kerja Terspesialisasi Antar Disiplin

Dokumen ini mendefinisikan arsitektur **Multi-Task Flow** untuk asisten Claudia dan subagen. Dokumen ini membuktikan secara formal mengapa setiap domain keahlian membutuhkan alur kerja terpisah (*domain-specific task flow*), serta memetakan matriks tahapan, kriteria verifikasi, dan artefak wajibnya.

---

## 1. Landasan Formal: Mengapa Satu Alur Tidak Cukup?

Tanggapan pengguna:  
> *"Setiap skill memiliki task flow yang berbeda, contoh task flow full stack engineer tidak sama dengan task flow researcher, apakah benar tanggapan saya ini?"*

**Tanggapan tersebut 100% BENAR secara teknis, arsitektural, dan empiris.**

Ada 3 alasan fundamental (*The Triad of Task Heterogeneity*):

1. **Asimetri Verifikasi (*Verification Asymmetry*)**:
   - Pada **Full-Stack Engineering**, kriteria verifikasi bersifat mekanis-deterministik: status HTTP 200/201, skema relasional terisolasi, exit code pengujian unit/feature bernilai 0, dan bundel build bebas error.
   - Pada **Technical Research**, kriteria verifikasi bersifat semantik-faktual: triangulasi data antar sumber resmi, ketepatan sitasi (file:/// dan nomor baris riil), konsistensi logis, dan ketiadaan halusinasi. Menjalankan unit test pada riset literatur adalah *category mistake*.

2. **Perbedaan Siklus Umpan Balik (*Feedback Loop Dynamics*)**:
   - **Spatial / XR**: Membutuhkan pengujian *spatial coordinates*, *scene graph budgeting*, *input mapping 6DoF*, serta audit latensi/frametime (*90 FPS VR target*) untuk mencegah *motion sickness*.
   - **Document Controller**: Berfokus pada siklus hidup kepatuhan ISO 9001 (Klausul 7.5), ketunggalan nomor registrasi (MDR), matriks RACI (Responsible, Accountable, Consulted, Informed), dan jejak audit revisi.

3. **Perbedaan Input & Output (*I/O Contracts*)**:
   - Menerapkan alur yang kaku dan seragam (*monolithic one-size-fits-all*) akan menyebabkan over-engineering pada tugas riset, atau sebaliknya melewatkan fase krusial (seperti audit frame-rate pada XR atau audit revisi pada Document Control).

---

## 2. Matriks Perbandingan Alur Kerja Antar Disiplin

| Dimensi | Full-Stack Engineer Flow | Technical Researcher Flow | Spatial & XR Developer Flow | Document Controller Flow |
| :--- | :--- | :--- | :--- | :--- |
| **Fokus Inti** | Integrasi end-to-end data & UI | Kebenaran faktual & sintesis | Komputasi spasial & interaksi 3D | Kepatuhan & keterlacakan dokumen |
| **Tahap 1** | Schema & Model Grounding | Inquiry Scope & Framing | Spatial Budget & Coordinate Setup | Identification & Codification |
| **Tahap 2** | API Contract & Business Logic | Broad Discovery & File Scanning | Scene Graph & Asset Hierarchy | MDR (Master Register) Indexing |
| **Tahap 3** | Frontend UI & State Binding | Deep Textual & Logic Grounding | 6DoF Input & Interaction Mapping | Review & Authorization Check (RACI) |
| **Tahap 4** | Automated Test Verification | Cross-Reference & Triangulation | Spatial UI & Procedural Audio | Revision Audit & Change Log |
| **Tahap 5** | Production Build & Optimization | Fact Extraction & Concise Delivery | Frame-Rate Audit (90 FPS) & Handshake | Controlled Distribution & Sync |
| **Artefak Utama** | Endpoint, Komponen, Migration | Laporan sintesis, Tabel matriks | WebXR Canvas, Camera Rig, Shaders | Form Registrasi MDR, Transmittal |
| **Metode Uji** | Unit/Feature Tests, Linter, Build | Cek referensi silang, bukti disk | WebXR Handshake, Profiler FPS | Audit kepatuhan ISO 9001:2015 |

---

## 3. Implementasi Kode: `TaskFlowRouter`

Sistem mengimplementasikan router otomatis di [`self_learning/multi_task_flow.py`](file:///C:/Users/Win10/Music/train/self_learning/multi_task_flow.py):

```python
from self_learning.multi_task_flow import TaskFlowRouter, DomainRole

router = TaskFlowRouter()

# 1. Mengambil alur spesifik berdasarkan peran
flow = router.get_flow(DomainRole.FULLSTACK)

# 2. Atau mendeteksi alur secara otomatis dari deskripsi tugas
auto_flow = router.route_by_task_description("Buatkan adegan 3D WebXR interaktif dengan Three.js")
# -> Mengembalikan instance SpatialXRTaskFlow

# 3. Mendaftarkan alur kerja baru secara dinamis (misal: Blockchain / ML / IoT)
custom_stages = [
    DomainStage("audit", "Security Audit", "Verifikasi celah reentrancy"),
    DomainStage("gas_opt", "Gas Optimization", "Pengecekan biaya eksekusi byte-code"),
]
router.register_custom_flow(
    role_name="blockchain_engineer",
    stages=custom_stages,
    keywords=["solidity", "smart contract", "web3"]
)
```

---

## 4. Mekanisme Otomasi untuk Hal/Domain Baru (Novel Skill Flow Synthesis)

Ketika pengguna memberikan instruksi atau proyek di luar 4 domain standar (misal: *Machine Learning Training, Cybersecurity, Smart Contracts, Embedded Robotics*):

1. **Deteksi Domain Baru (*Novelty Detection*)**:
   - `TaskFlowRouter` mendeteksi bahwa kata kunci tugas tidak memiliki representasi pipeline khusus.
2. **Sintesis Tahapan Domain Berbasis Kerangka Meta 6-Fase**:
   - Sistem **Auto-Plan** menurunkan tahapan spesifik dari 6 fase tertutup (*Ingestion ➔ Planning ➔ Execution ➔ Verification ➔ Reflexion ➔ Distillation*).
   - Menetapkan **kriteria verifikasi empiris yang relevan secara matematis/teknis** (misal: *loss convergence* untuk ML, *gas limit* untuk smart contract).
3. **Pendaftaran Dinamis (`register_custom_flow`)**:
   - Instansiasi `DynamicTaskFlow` langsung didaftarkan ke runtime router.
4. **Persistensi ke Knowledge Store & Memory**:
   - Struktur alur baru langsung disimpan ke `self_learning/knowledge_base/` dan dicatat ke `memory.md` (*Auto-Learn*), sehingga pada iterasi berikutnya alur tersebut siap digunakan kembali tanpa perlu disintesis ulang.

