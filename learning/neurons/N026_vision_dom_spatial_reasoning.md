# Neuron N026: Multimodal Vision-Language Spatial Reasoning & DOM Geometry AST

## 📌 Domain & Invarian Arsitektur
- **Domain**: Multimodal UI Grounding, Vision-Language Spatial Reasoning, Pixel-to-DOM Layout Tree, Viewport Coordinate Bounding Boxes, & OCR Token Alignment.
- **Prinsip Utama**: *Visual state is ground truth; DOM is intent*. Jangan pernah berasumsi elemen DOM terlihat atau dapat diinteraksikan hanya karena ada di HTML. Visibilitas fisik ditentukan oleh perpotongan viewport (*clipping rects*), *overflow boundaries*, *opacity*, serta *z-index stacking context*.
- **Synaptic Synapses**: Terhubung langsung dengan [N003] (Mobile UI/Touch Bounds), [N004] (Ponytail Minimality), [N009] (Spatial Indexing & R-Tree), [N011] (Mechanical Sympathy / Low-Overhead Parsing), [N015] (AST Traversal & Visitors), [N019] (Strict Schema Validation).

---

## 🧭 5 Aturan Emas Spatial Reasoning & DOM Geometry

### 1. Viewport Coordinate Normalization $[0, 1000]$
- Representasikan seluruh bounding box visual dalam ruang terstandarisasi $[y_{\min}, x_{\min}, y_{\max}, x_{\max}] \in [0, 1000]^4$ atau pixel absolut $[x, y, w, h]$ dengan referensi viewport nyata $(W \times H)$.
- Formula transformasi:
  $$x_{\text{norm}} = \text{round}\left(\frac{x_{\text{px}}}{W} \times 1000\right), \quad y_{\text{norm}} = \text{round}\left(\frac{y_{\text{px}}}{H} \times 1000\right)$$
- Mencegah disparitas resolusi antara screenshot VLM (e.g. 1080p vs Retina 4K vs Mobile Viewport).

### 2. Recursive Effective Clipping Rect & Visibility Pruning
- Setiap node anak dibatasi oleh perpotongan (*intersection*) dari seluruh bounding rect parent berproperti `overflow: hidden`, `overflow: scroll`, atau `clip-path`.
- Invarian: Jika $\text{Area}(R_{\text{node}} \cap R_{\text{ancestors}} \cap R_{\text{viewport}}) \le 0$, node **wajib di-prune** dari tree interaksi (tidak dapat diklik).

### 3. Z-Index & Stacking Context Occlusion
- Elemen dengan level stacking context lebih tinggi pada koordinat $(x, y)$ menutupi (*occlude*) elemen di bawahnya.
- Hit-testing wajib mengevaluasi simpul teratas pada tumpukan visual: $\text{Target}(x, y) = \arg\max_{node \in \text{Candidates}} (\text{stack\_level}, \text{tree\_depth})$.

### 4. OCR Token Alignment via Bounding Box Containment & Soft IoU
- Menggabungkan token teks visual OCR ke node DOM terdekat menggunakan metrik *Overlap Ratio*:
  $$\text{Overlap}(B_{\text{ocr}}, B_{\text{dom}}) = \frac{\text{Area}(B_{\text{ocr}} \cap B_{\text{dom}})}{\text{Area}(B_{\text{ocr}})} \ge 0.70$$
- Jika token OCR berada di dalam $B_{\text{dom}}$ atau memiliki titik tengah (*centroid*) di dalam $B_{\text{dom}}$, lekatkan label semantik teks ke node AST tersebut.

### 5. Deterministic Click Action Dispatch
- Titik klik optimal adalah *Center-of-Mass Inset* yang di-clamp sebesar 15% dari tepi elemen untuk menghindari mis-click pada border, scrollbar, atau trigger drop-down sibling:
  $$x_{\text{click}} = x + \lfloor 0.5 \cdot w \rfloor, \quad y_{\text{click}} = y + \lfloor 0.5 \cdot h \rfloor$$
- Untuk antarmuka mobile, pastikan target klik minimal $44 \times 44$ CSS px (WCAG 2.5.5 / [N003]).

---

## 🛠️ Implementasi Referensi Stdlib Python: Spatial AST & OCR Grounding

```python
#!/usr/bin/env python3
"""
Neuron N026: Multimodal Vision-Language Spatial Reasoning & DOM Geometry AST
Standard library only (zero external dependencies).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
import sys
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
import json
import math


class Direction(Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    LEFT_OF = "LEFT_OF"
    RIGHT_OF = "RIGHT_OF"
    INSIDE = "INSIDE"
    OVERLAPPING = "OVERLAPPING"


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def xmin(self) -> float:
        return self.x

    @property
    def ymin(self) -> float:
        return self.y

    @property
    def xmax(self) -> float:
        return self.x + self.w

    @property
    def ymax(self) -> float:
        return self.y + self.h

    @property
    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.w / 2.0, self.y + self.h / 2.0)

    def intersect(self, other: Rect) -> Optional[Rect]:
        nx1 = max(self.xmin, other.xmin)
        ny1 = max(self.ymin, other.ymin)
        nx2 = min(self.xmax, other.xmax)
        ny2 = min(self.ymax, other.ymax)
        if nx2 > nx1 and ny2 > ny1:
            return Rect(x=nx1, y=ny1, w=nx2 - nx1, h=ny2 - ny1)
        return None

    def contains_point(self, px: float, py: float) -> bool:
        return self.xmin <= px <= self.xmax and self.ymin <= py <= self.ymax

    def iou(self, other: Rect) -> float:
        inter = self.intersect(other)
        if not inter or inter.area <= 0:
            return 0.0
        union_area = self.area + other.area - inter.area
        return inter.area / union_area if union_area > 0 else 0.0

    def to_normalized_1000(self, vw: float, vh: float) -> Tuple[int, int, int, int]:
        """Returns [ymin, xmin, ymax, xmax] in 0-1000 scale."""
        ymin = int(round(max(0.0, min(1.0, self.ymin / vh)) * 1000))
        xmin = int(round(max(0.0, min(1.0, self.xmin / vw)) * 1000))
        ymax = int(round(max(0.0, min(1.0, self.ymax / vh)) * 1000))
        xmax = int(round(max(0.0, min(1.0, self.xmax / vw)) * 1000))
        return (ymin, xmin, ymax, xmax)


@dataclass
class DOMNode:
    node_id: str
    tag: str
    rect: Rect
    text: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List[DOMNode] = field(default_factory=list)
    parent: Optional[DOMNode] = None
    z_index: int = 0
    is_visible: bool = True
    effective_rect: Optional[Rect] = None

    def add_child(self, child: DOMNode) -> None:
        child.parent = self
        self.children.append(child)


@dataclass
class OCRToken:
    text: str
    rect: Rect
    confidence: float = 1.0


class SpatialGeometryEngine:
    def __init__(self, viewport_width: float = 1920.0, viewport_height: float = 1080.0):
        self.vw = viewport_width
        self.vh = viewport_height
        self.viewport_rect = Rect(0.0, 0.0, self.vw, self.vh)

    def compute_layout_tree(self, root: DOMNode) -> None:
        """
        Traverse DOM tree, calculate recursive effective clipping rectangles,
        and mark visibility invariants.
        """
        def _traverse(node: DOMNode, current_clip: Rect, depth: int) -> None:
            clip_here = current_clip
            if node.attributes.get("overflow") in ("hidden", "scroll", "auto"):
                inter = current_clip.intersect(node.rect)
                clip_here = inter if inter is not None else Rect(0, 0, 0, 0)

            node.effective_rect = node.rect.intersect(clip_here)
            node.is_visible = (
                node.effective_rect is not None
                and node.effective_rect.area > 0.0
                and node.attributes.get("display") != "none"
                and node.attributes.get("visibility") != "hidden"
                and float(node.attributes.get("opacity", "1.0")) > 0.01
            )

            for child in node.children:
                _traverse(child, clip_here, depth + 1)

        _traverse(root, self.viewport_rect, 0)

    def align_ocr_tokens(self, root: DOMNode, tokens: List[OCRToken]) -> None:
        """
        Align visual OCR tokens to corresponding DOM AST nodes via containment & IoU.
        """
        all_nodes = self._flatten_visible_nodes(root)
        
        for token in tokens:
            t_center = token.rect.center
            best_node: Optional[DOMNode] = None
            max_containment_or_iou = 0.0

            for node in all_nodes:
                if not node.effective_rect:
                    continue
                
                # Check center point containment
                if node.effective_rect.contains_point(t_center[0], t_center[1]):
                    score = 1.0 + (1.0 / (node.effective_rect.area + 1.0))
                    if score > max_containment_or_iou:
                        max_containment_or_iou = score
                        best_node = node
                else:
                    iou = node.effective_rect.iou(token.rect)
                    if iou > 0.3 and iou > max_containment_or_iou:
                        max_containment_or_iou = iou
                        best_node = node

            if best_node:
                if best_node.text:
                    if token.text not in best_node.text:
                        best_node.text = f"{best_node.text} {token.text}".strip()
                else:
                    best_node.text = token.text

    def find_node_by_spatial_relation(
        self,
        root: DOMNode,
        anchor_node: DOMNode,
        direction: Direction,
        tag_filter: Optional[str] = None,
        max_distance: float = 800.0
    ) -> Optional[DOMNode]:
        """
        Resolve queries like 'Find input to the RIGHT_OF anchor' using geometric vector angles and distance.
        """
        if not anchor_node.effective_rect:
            return None

        ax, ay = anchor_node.effective_rect.center
        candidates = self._flatten_visible_nodes(root)
        best_candidate: Optional[DOMNode] = None
        min_dist = float("inf")

        for cand in candidates:
            if cand == anchor_node or not cand.effective_rect:
                continue
            if tag_filter and cand.tag != tag_filter:
                continue

            cx, cy = cand.effective_rect.center
            dx = cx - ax
            dy = cy - ay
            dist = math.hypot(dx, dy)

            if dist > max_distance:
                continue

            valid = False
            if direction == Direction.RIGHT_OF and dx > 0 and abs(dy) <= max(anchor_node.effective_rect.h, cand.effective_rect.h) * 1.5:
                valid = True
            elif direction == Direction.LEFT_OF and dx < 0 and abs(dy) <= max(anchor_node.effective_rect.h, cand.effective_rect.h) * 1.5:
                valid = True
            elif direction == Direction.BELOW and dy > 0 and abs(dx) <= max(anchor_node.effective_rect.w, cand.effective_rect.w) * 1.5:
                valid = True
            elif direction == Direction.ABOVE and dy < 0 and abs(dx) <= max(anchor_node.effective_rect.w, cand.effective_rect.w) * 1.5:
                valid = True

            if valid and dist < min_dist:
                min_dist = dist
                best_candidate = cand

        return best_candidate

    def get_action_click_coordinate(self, node: DOMNode) -> Tuple[int, int]:
        """
        Returns pixel coordinates (x, y) for deterministic mouse click.
        """
        if not node.effective_rect or not node.is_visible:
            raise ValueError(f"Node {node.node_id} is not visible in viewport.")
        
        cx, cy = node.effective_rect.center
        return (int(round(cx)), int(round(cy)))

    def _flatten_visible_nodes(self, root: DOMNode) -> List[DOMNode]:
        nodes = []
        def _collect(n: DOMNode):
            if n.is_visible:
                nodes.append(n)
            for c in n.children:
                _collect(c)
        _collect(root)
        return nodes


# =====================================================================
# INVARIANT VERIFICATION SUITE
# =====================================================================
if __name__ == "__main__":
    engine = SpatialGeometryEngine(viewport_width=1920, viewport_height=1080)

    # 1. Build Mock DOM Layout Tree
    root = DOMNode(node_id="root", tag="body", rect=Rect(0, 0, 1920, 1080))
    
    container = DOMNode(
        node_id="modal_container",
        tag="div",
        rect=Rect(400, 200, 800, 600),
        attributes={"overflow": "hidden"}
    )
    root.add_child(container)

    label_email = DOMNode(
        node_id="lbl_email",
        tag="label",
        rect=Rect(450, 250, 100, 40),
        text=""
    )
    container.add_child(label_email)

    input_email = DOMNode(
        node_id="txt_email",
        tag="input",
        rect=Rect(570, 250, 250, 40),
        attributes={"type": "text"}
    )
    container.add_child(input_email)

    btn_submit = DOMNode(
        node_id="btn_submit",
        tag="button",
        rect=Rect(840, 250, 120, 40)
    )
    container.add_child(btn_submit)

    # Offscreen / clipped element outside modal container
    hidden_child = DOMNode(
        node_id="clipped_node",
        tag="div",
        rect=Rect(1300, 250, 200, 50)  # x=1300 is outside container (max x = 400 + 800 = 1200)
    )
    container.add_child(hidden_child)

    # 2. Run AST Layout Computation
    engine.compute_layout_tree(root)

    assert label_email.is_visible is True, "label_email must be visible"
    assert input_email.is_visible is True, "input_email must be visible"
    assert hidden_child.is_visible is False, "clipped_node must be pruned due to overflow hidden clip"

    # 3. Align OCR Tokens to DOM Nodes
    ocr_tokens = [
        OCRToken(text="Email", rect=Rect(452, 255, 45, 18)),
        OCRToken(text="Address", rect=Rect(500, 255, 48, 18)),
        OCRToken(text="Submit", rect=Rect(860, 260, 60, 20)),
    ]
    engine.align_ocr_tokens(root, ocr_tokens)

    assert "Email Address" in label_email.text, f"OCR token failed to align. Got: {label_email.text}"
    assert "Submit" in btn_submit.text, f"OCR token failed to align to button. Got: {btn_submit.text}"

    # 4. Test Spatial Directional Query
    target_input = engine.find_node_by_spatial_relation(
        root=root,
        anchor_node=label_email,
        direction=Direction.RIGHT_OF,
        tag_filter="input"
    )
    assert target_input is not None, "Failed to find input RIGHT_OF label"
    assert target_input.node_id == "txt_email", f"Expected txt_email, got {target_input.node_id}"

    # 5. Coordinate Action Precision & Normalization
    click_x, click_y = engine.get_action_click_coordinate(btn_submit)
    assert click_x == 900 and click_y == 270, f"Expected (900, 270), got ({click_x}, {click_y})"

    norm_coords = btn_submit.effective_rect.to_normalized_1000(1920, 1080)
    assert norm_coords[0] == 231 and norm_coords[1] == 438, f"Unexpected normalized bounds: {norm_coords}"

    print("  [✓] Neuron N026 Verification Passed: Geometry AST, Clipping, OCR Alignment & Spatial Queries OK.")
```
