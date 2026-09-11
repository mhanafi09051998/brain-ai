---
name: web-game-dev
description: >-
  Standar rekayasa, arsitektur, dan optimasi pengembangan game berbasis Web
  (HTML5, Canvas2D, WebGL, WebGPU, Three.js, Babylon.js, PixiJS, Phaser, Rapier.js).
  Mencakup implementasi Fixed Timestep Game Loop, Entity Component System (ECS),
  Zero-Allocation GC Mitigation, Shaders (GLSL/WGSL), Audio (Web Audio API),
  Asset Pipeline (GLTF/Draco/KTX2), dan Multiplayer Netcode (WebSockets/WebRTC).
---

# Web Game Development: Standar Arsitektur & Rekayasa Teknis

Dokumen ini mendefinisikan standar rekayasa game berbasis web berkinerja tinggi (*high-performance web game development*) untuk lingkungan peramban modern.

---

## 1. Tumpukan Teknologi Rekomendasi (*Battle-Tested Stacks*)

| Kategori | Solusi Utama | Alternatif / Tambahan | Catatan Arsitektur |
| :--- | :--- | :--- | :--- |
| **3D Rendering** | **Three.js** (r160+) / **Babylon.js** | WebGPU Native / PlayCanvas | Utamakan Three.js untuk fleksibilitas modular; Babylon.js untuk engine terpadu (all-in-one). |
| **2D Rendering** | **PixiJS** (v8) | **Phaser 3** / Canvas2D native | PixiJS untuk rendering 2D berkecepatan tinggi via WebGL/WebGPU; Phaser untuk framework game siap pakai. |
| **Fisika (Physics)** | **Rapier.js** (WASM) | Matter.js (2D) / Cannon-es (3D) | Rapier berbasis Rust/WASM, deterministik, performa komputasi tertinggi di browser. |
| **State & Logic** | **ECS (bitecs / miniplex)** | Finite State Machine (FSM) | Data-Oriented Design (DOD) untuk memproses ribuan entitas tanpa overhead OOP. |
| **Audio** | **Web Audio API** / **Howler.js** | - | Wajib menangani *AudioContext Autoplay Policy* (inisialisasi pada interaksi pertama pengguna). |
| **Aset 3D/2D** | **glTF 2.0 (.glb)** + Draco/Meshopt | KTX2 / Basis Universal (Textures) | Kompresi tekstur GPU-native untuk memangkas VRAM dan waktu download. |
| **Networking** | **WebSockets** / **WebRTC DataChannels** | Geckos.io (UDP-like WebRTC) | WebSockets untuk turn-based/state update; WebRTC/UDP untuk game aksi bertempo cepat. |

---

## 2. Invarian Performa Web Game (*The Performance Budget*)

1. **Target Frame Rate**: Stabil 60 FPS (Frame budget $\le 16.6\text{ ms}$) atau 120 FPS ($\le 8.3\text{ ms}$).
2. **Zero-Allocation Hot Loops (Disiplin Bebas Alokasi di `update()` & `render()`)**:
   - **Dilarang keras instansiasi objek baru** di dalam loop game (misal: `new THREE.Vector3()`, array baru, atau anonymous closure).
   - Gunakan **Object Pooling** dan mutasi in-place:
     ```javascript
     // ANTI-PATTERN (Memicu Garbage Collector Spikes / Frame Drops)
     function update(target) {
       const offset = new THREE.Vector3(0, 1, 0); // ❌ ALOKASI BARU SETIAP FRAME
       mesh.position.add(offset);
     }

     // PATTERN WAJIB (Zero Allocation via Pre-allocated Vector instances)
     const _tempVec = new THREE.Vector3(); // ✅ Dialokasikan sekali di luar loop
     function update(target) {
       _tempVec.set(0, 1, 0);
       mesh.position.add(_tempVec);
     }
     ```
3. **Cap Device Pixel Ratio**:
   - Batasi `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2.0))` untuk mencegah crash atau overheating pada layar Retina/4K mobile.
4. **Draw Call Mitigation**:
   - Gunakan `InstancedMesh` atau `BatchedMesh` untuk objek berulang (rumput, musuh, peluru).
   - Satukan tekstur ke dalam *Texture Atlas*.

---

## 3. Arsitektur Game Loop Terstandarisasi

Gunakan **Fixed Timestep with Accumulator** agar simulasi fisika tetap deterministik dan konsisten terlepas dari variasi refresh rate layar:

```typescript
export class GameEngine {
  private lastTime: number = 0;
  private accumulator: number = 0;
  private readonly fixedDelta: number = 1 / 60; // 60 Hz simulasi fisika

  public start(): void {
    this.lastTime = performance.now();
    requestAnimationFrame(this.loop.bind(this));
  }

  private loop(currentTime: number): void {
    const frameTime = Math.min((currentTime - this.lastTime) / 1000, 0.25); // Cap delta untuk cegah spiral of death
    this.lastTime = currentTime;
    this.accumulator += frameTime;

    // Fixed Update untuk Logic & Physics (Deterministik)
    while (this.accumulator >= this.fixedDelta) {
      this.fixedUpdate(this.fixedDelta);
      this.accumulator -= this.fixedDelta;
    }

    // Alpha interpolation untuk render halus antar frame
    const alpha = this.accumulator / this.fixedDelta;
    this.render(alpha);

    requestAnimationFrame(this.loop.bind(this));
  }

  private fixedUpdate(dt: number): void {
    // 1. Process Input
    // 2. Step Physics Simulation
    // 3. Update Game State / ECS
  }

  private render(alpha: number): void {
    // 1. Interpolate Transforms
    // 2. Render Scene via WebGL/WebGPU
  }
}
```

---

## 4. Pipeline Input & Kontrol Pengguna

- **Pointer Lock API**: Untuk game First-Person / TPS 3D (`element.requestPointerLock()`).
- **Input Polling Matrix**: Hindari langsung memproses logika di dalam event listener DOM. Simpan state input ke dalam bitmask / object buffer dan evaluasi saat `fixedUpdate()`.
- **Touch Virtual Sticks**: Menggunakan *dynamic touch anchoring* agar kontrol sentuh layar ponsel responsif.

---

## 5. Manajemen Memori & Siklus Hidup Aset (Disposal Protocol)

Browser tidak meng-garbage-collect memori GPU WebGL secara otomatis. Setiap scene change atau penghapusan objek wajib memanggil disposal eksplisit:

```typescript
export function disposeNode(node: THREE.Object3D): void {
  if (!node) return;

  if (node instanceof THREE.Mesh) {
    if (node.geometry) {
      node.geometry.dispose();
    }
    if (node.material) {
      if (Array.isArray(node.material)) {
        node.material.forEach((mat) => disposeMaterial(mat));
      } else {
        disposeMaterial(node.material);
      }
    }
  }
}

function disposeMaterial(mat: THREE.Material): void {
  mat.dispose();
  for (const key of Object.keys(mat)) {
    const value = (mat as any)[key];
    if (value && typeof value === 'object' && 'minFilter' in value) {
      value.dispose(); // Dispose WebGL Texture
    }
  }
}
```

---

## 6. Checklist Verifikasi Game Web Siap Produksi

- [ ] **Frame Timing Audit**: Tidak ada spike garbage collector (GC) pada Chrome DevTools Performance Profiler.
- [ ] **Mobile Touch & Resize**: Game merespons event `resize` dan `orientationchange` tanpa distorsi aspek rasio.
- [ ] **Audio Policy Handling**: Audio dimulai tanpa error `DOMException: play() failed` berkat gate UI interaksi pertama (*Click to Start*).
- [ ] **Asset Loading Screen**: Ada progress bar eksplisit untuk loading GLTF dan buffer audio.
- [ ] **Clean GPU VRAM Disposal**: Memori WebGL tidak bocor saat berpindah level (*level transition*).
