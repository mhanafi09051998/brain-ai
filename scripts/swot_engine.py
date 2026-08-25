#!/usr/bin/env python3
"""
Claudia Strategic Intelligence: SWOT & TOWS Matrix Engine
Autonomous Strategic Analysis & Risk Assessment Module
"""

import os
import sys
import json
import argparse
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

class SWOTEngine:
    def __init__(self, target_name: str, target_type: str = "business"):
        self.target_name = target_name
        self.target_type = target_type
        self.swot_data = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        self.tows_strategies = {
            "SO": [], # Strengths-Opportunities (Maxi-Maxi)
            "WO": [], # Weaknesses-Opportunities (Mini-Maxi)
            "ST": [], # Strengths-Threats (Maxi-Mini)
            "WT": []  # Weaknesses-Threats (Mini-Mini)
        }

    def add_factor(self, category: str, factor: str, impact_score: int = 5):
        """Add a strategic factor with impact weight (1-10)"""
        cat = category.lower()
        if cat in self.swot_data:
            self.swot_data[cat].append({"factor": factor, "weight": impact_score})

    def formulate_tows(self):
        """Synthesize TOWS Cross-Matrix Strategies from raw SWOT factors"""
        s_list = [f["factor"] for f in self.swot_data["strengths"]]
        w_list = [f["factor"] for f in self.swot_data["weaknesses"]]
        o_list = [f["factor"] for f in self.swot_data["opportunities"]]
        t_list = [f["factor"] for f in self.swot_data["threats"]]

        # SO Strategies: Leverage Strengths to seize Opportunities
        if s_list and o_list:
            self.tows_strategies["SO"].append(
                f"Kapitalisasi '{s_list[0]}' untuk mengeksploitasi potensi pasar '{o_list[0]}'."
            )
        
        # WO Strategies: Overcome Weaknesses by exploiting Opportunities
        if w_list and o_list:
            self.tows_strategies["WO"].append(
                f"Gunakan momentum '{o_list[0]}' untuk menutup celah '{w_list[0]}'."
            )

        # ST Strategies: Leverage Strengths to mitigate Threats
        if s_list and t_list:
            self.tows_strategies["ST"].append(
                f"Bentengi sistem dari '{t_list[0]}' dengan keunggulan '{s_list[0]}'."
            )

        # WT Strategies: Defensive moves to minimize Weaknesses & avoid Threats
        if w_list and t_list:
            self.tows_strategies["WT"].append(
                f"Lakukan mitigasi darurat pada '{w_list[0]}' agar tidak dieksploitasi oleh '{t_list[0]}'."
            )

    def print_matrix(self):
        print(f"\n{'='*70}")
        print(f"📊 LAPORAN ANALISIS STRATEGIS SWOT & TOWS: {self.target_name.upper()}")
        print(f"{'='*70}")

        print("\n[ 1. FAKTOR INTERNAL ]")
        print("💪 KEKUATAN (STRENGTHS):")
        for idx, s in enumerate(self.swot_data["strengths"], 1):
            print(f"  {idx}. {s['factor']} (Bobot: {s['weight']}/10)")

        print("\n⚠️ KELEMAHAN (WEAKNESSES):")
        for idx, w in enumerate(self.swot_data["weaknesses"], 1):
            print(f"  {idx}. {w['factor']} (Bobot: {w['weight']}/10)")

        print("\n[ 2. FAKTOR EKSTERNAL ]")
        print("🚀 PELUANG (OPPORTUNITIES):")
        for idx, o in enumerate(self.swot_data["opportunities"], 1):
            print(f"  {idx}. {o['factor']} (Bobot: {o['weight']}/10)")

        print("\n🛡️ ANCAMAN (THREATS):")
        for idx, t in enumerate(self.swot_data["threats"], 1):
            print(f"  {idx}. {t['factor']} (Bobot: {t['weight']}/10)")

        print(f"\n{'-'*70}")
        print("🎯 [ 3. MATRIKS STRATEGI TOWS (ACTIONABLE ROADMAP) ]")
        print(f"{'-'*70}")
        print("🔥 SO (Maxi-Maxi Strategy - Ekspansi Agresif):")
        for item in self.tows_strategies["SO"]:
            print(f"  • {item}")

        print("\n🔄 WO (Mini-Maxi Strategy - Perbaikan Internal untuk Peluang):")
        for item in self.tows_strategies["WO"]:
            print(f"  • {item}")

        print("\n🛡️ ST (Maxi-Mini Strategy - Diversifikasi & Pertahanan):")
        for item in self.tows_strategies["ST"]:
            print(f"  • {item}")

        print("\n🚨 WT (Mini-Mini Strategy - Mitigasi Risiko / Survival):")
        for item in self.tows_strategies["WT"]:
            print(f"  • {item}")

        print(f"\n{'='*70}\n")

def run_sample_goblix_analysis():
    engine = SWOTEngine(target_name="Goblix Streaming Platform", target_type="Digital Media Product")
    
    # Strengths
    engine.add_factor("strengths", "Arsitektur Fullstack Ultra-Ringan (Node.js native, RAM < 25MB)", 9)
    engine.add_factor("strengths", "Kualitas tayangan Full HD 1080p BluRay dengan Hardsub/Softsub Indonesia resmi", 9)
    engine.add_factor("strengths", "Autentikasi produksi aman berbasis PBKDF2-SHA512 + JWT Session", 8)
    
    # Weaknesses
    engine.add_factor("weaknesses", "Jumlah katalog film awal masih terbatas (initial library)", 6)
    engine.add_factor("weaknesses", "Belum ada sistem CDN multi-region terdistribusi untuk jutaan penonton", 5)
    
    # Opportunities
    engine.add_factor("opportunities", "Tingginya permintaan streaming film 1080p Sub Indo tanpa iklan pop-up", 10)
    engine.add_factor("opportunities", "Integrasi integrasi AI recommendation engine untuk personalisasi tontonan", 8)
    
    # Threats
    engine.add_factor("threats", "Regulasi hak cipta dan kepatuhan lisensi penyiaran digital", 9)
    engine.add_factor("threats", "Lonjakan utilisasi bandwidth server saat traffic viral", 7)

    engine.formulate_tows()
    engine.print_matrix()

if __name__ == "__main__":
    run_sample_goblix_analysis()
