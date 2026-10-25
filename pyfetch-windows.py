#!/usr/bin/env python3
import os
import sys
import ctypes
import socket
import winreg
import platform
import subprocess

LOGO = [
    "⠀⠀⠀⠀⢀⡠⠤⠔⢲⢶⡖⠒⠤⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⣠⡚⠁⢀⠀⠀⢄⢻⣿⠀⠀⠀⡙⣷⢤⡀⠀⠀⠀⠀⠀⠀",
    "⠀⡜⢱⣇⠀⣧⢣⡀⠀⡀⢻⡇⠀⡄⢰⣿⣷⡌⣢⡀⠀⠀⠀⠀",
    "⠸⡇⡎⡿⣆⠹⣷⡹⣄⠙⣽⣿⢸⣧⣼⣿⣿⣿⣶⣼⣆⠀⠀⠀",
    "⣷⡇⣷⡇⢹⢳⡽⣿⡽⣷⡜⣿⣾⢸⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀",
    "⣿⡇⡿⣿⠀⠣⠹⣾⣿⣮⠿⣞⣿⢸⣿⣛⢿⣿⡟⠯⠉⠙⠛⠓",
    "⣿⣇⣷⠙⡇⠀⠁⠀⠉⣽⣷⣾⢿⢸⣿⠀⢸⣿⢿⠀⠀⠀⠀⠀",
    "⡟⢿⣿⣷⣾⣆⠀⠀⠘⠘⠿⠛⢸⣼⣿⢖⣼⣿⠘⡆⠀⠀⠀⠀",
    "⠃⢸⣿⣿⡘⠋⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⡆⠇⠀⠀⠀⠀",
    "⠀⢸⡿⣿⣇⠀⠈⠀⠤⠀⠀⢀⣿⣿⣿⣿⣿⣿⣧⢸⠀⠀⠀⠀",
    "⠀⠈⡇⣿⣿⣷⣤⣀⠀⣀⠔⠋⣿⣿⣿⣿⣿⡟⣿⡞⡄⠀⠀⠀",
    "⠀⠀⢿⢸⣿⣿⣿⣿⣿⡇⠀⢠⣿⡏⢿⣿⣿⡇⢸⣇⠇⠀⠀⠀",
    "⠀⠀⢸⡏⣿⣿⣿⠟⠋⣀⠠⣾⣿⠡⠀⢉⢟⠷⢼⣿⣿⠀⠀⠀",
    "⠀⠀⠈⣷⡏⡱⠁⠀⠊⠀⠀⣿⣏⣀⡠⢣⠃⠀⠀⢹⣿⡄⠀⠀",
    "⠀⠀⠘⢼⣿⠀⢠⣤⣀⠉⣹⡿⠀⠁⠀⡸⠀⠀⠀⠈⣿⡇⠀⠀",
]

C_RESET, C_BOLD = "\033[0m", "\033[1m"
C_PINK,  C_CYAN  = "\033[95m", "\033[96m"
C_GREEN, C_BLUE  = "\033[92m", "\033[94m"

if os.name == "nt":
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
    except Exception:
        return None


def key_value(key, value):
    return f"{C_CYAN}{C_BOLD}{key}{C_RESET}: {value}"


def get_user_host():
    user = os.environ.get("USERNAME", "user")
    return f"{C_GREEN}{C_BOLD}{user}{C_RESET}{C_PINK}@{C_RESET}{C_GREEN}{socket.gethostname()}{C_RESET}"


def get_windows_name():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as k:
            name = winreg.QueryValueEx(k, "ProductName")[0]
            try: 
                display = winreg.QueryValueEx(k, "DisplayVersion")[0]
            except OSError:
                display = winreg.QueryValueEx(k, "ReleaseId")[0]
        return f"{name} {display}"
    except Exception:
        return " ".join(filter(None, platform.win32_ver()))


def get_kernel():
    v = sys.getwindowsversion()
    return f"Windows NT {v.major}.{v.minor}.{v.build}"


def get_uptime():
    ms = ctypes.windll.kernel32.GetTickCount64()
    secs = int(ms // 1000)
    d, secs = divmod(secs, 86400)
    h, rem = divmod(secs, 3600)
    m = rem // 60
    return (f"{d} дн, " if d else "") + f"{h:02d}:{m:02d}"


def get_cpu():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
            name = winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
    except Exception:
        name = platform.processor() or "Unknown"
    return f"{name} ({os.cpu_count() or '?'} потоков)"


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                ("ullAvailExtendedVirtual", ctypes.c_uint64)]


def get_ram():
    try:
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(mem)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
        total = mem.ullTotalPhys / 1024**3
        used = (mem.ullTotalPhys - mem.ullAvailPhys) / 1024**3
        return f"{used:.1f} / {total:.1f} ГиБ"
    except Exception:
        return "unknown"


def get_gpu():
    out = run(["powershell", "-NoProfile", "-Command",
               "(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) -join '; '"])
    if out:
        return out
    out = run(["wmic", "path", "win32_VideoController", "get", "name"])
    if out:
        lines = [l.strip() for l in out.splitlines() if l.strip() and "Name" not in l]
        if lines:
            return "; ".join(lines)
    return "Unknown"


def get_disk():
    try:
        free = ctypes.c_ulonglong()
        total = ctypes.c_ulonglong()
        ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:\\", None, ctypes.byref(total), ctypes.byref(free))
        t, f = total.value / 1024**3, free.value / 1024**3
        return f"{t - f:.0f} / {t:.0f} ГиБ (C:\\)"
    except Exception:
        return "unknown"


def get_shell():
    parent = os.environ.get("PARENTNAME") or os.environ.get("ComSpec", "")
    term = os.environ.get("WT_SESSION") and "Windows Terminal" or "conhost"
    return f"{os.path.basename(parent or 'cmd')} ({term})" if parent else term


def get_colors_bar():
    blocks = [f"\033[4{i}m   " for i in range(8)]
    blocks += ["\033[0m  "] + [f"\033[10{i}m   " for i in range(8)]
    return "".join(blocks) + C_RESET


def main():
    sep = f"{C_PINK}──────────────────────────────{C_RESET}"
    info = [
        get_user_host(),
        sep,
        key_value("OS",       get_windows_name()),
        key_value("Ядро",     get_kernel()),
        key_value("Аптайм",   get_uptime()),
        key_value("CPU",      get_cpu()),
        key_value("RAM",      get_ram()),
        key_value("GPU",      get_gpu()),
        key_value("Диск C:",  get_disk()),
        key_value("Shell",    get_shell()),
        key_value("Python",   platform.python_version()),
        sep,
        get_colors_bar(),
    ]

    width = max(len(line) for line in LOGO)
    n = max(len(LOGO), len(info))
    for i in range(n):
        left = f"{C_PINK}{LOGO[i]}{C_RESET}" if i < len(LOGO) else " " * width
        right = info[i] if i < len(info) else ""
        print(f"{left:<{width + 20}} {right}")


if __name__ == "__main__":
    main()
