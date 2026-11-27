"""NEXUS QUANT — inspection de l'environnement (lecture seule).

Usage (Windows, PowerShell ou cmd) :
    python scripts\\check_env.py

N'installe rien, n'accède pas au réseau, n'écrit aucun fichier.
Affiche : OS, CPU, RAM, disque, version de Python, bibliothèques utiles au projet.
"""
from __future__ import annotations

import importlib.metadata as md
import os
import platform
import shutil
import sys


def ram_total_gb() -> float | None:
    try:
        if sys.platform == "win32":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.ullTotalPhys / 1024**3
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3
    except Exception:
        return None


PACKAGES = [
    "numpy", "pandas", "pyarrow", "polars", "numba", "scipy", "statsmodels",
    "duckdb", "matplotlib", "plotly", "streamlit", "pytest", "pydantic",
    "MetaTrader5", "ccxt", "yfinance",
]


def main() -> None:
    print("=== NEXUS QUANT — environnement ===")
    print(f"OS          : {platform.platform()}")
    print(f"Machine     : {platform.machine()}  |  Processeur : {platform.processor() or 'n/d'}")
    print(f"Coeurs CPU  : {os.cpu_count()}")
    ram = ram_total_gb()
    print(f"RAM totale  : {ram:.1f} Go" if ram else "RAM totale  : n/d")
    here = os.path.abspath(os.getcwd())
    du = shutil.disk_usage(here)
    print(f"Disque ({os.path.splitdrive(here)[0] or here}) : {du.free / 1024**3:.1f} Go libres / {du.total / 1024**3:.1f} Go")
    print(f"Python      : {sys.version.split()[0]} ({sys.executable})")
    print("--- Bibliothèques ---")
    for name in PACKAGES:
        try:
            print(f"  {name:<12} {md.version(name)}")
        except md.PackageNotFoundError:
            print(f"  {name:<12} (absent)")


if __name__ == "__main__":
    main()
