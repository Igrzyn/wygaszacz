import subprocess
import os
import sys
import time
import winreg

if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    print("❌ Nie podano folderu instalacyjnego.")
    input("Naciśnij Enter, aby zamknąć...")
    sys.exit(1)

# 🧹 Rejestr: ścieżka do wpisu uninstall
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\WygaszaczEdukacyjny"

def usuń_wpis_z_rejestru():
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        print("🗑 Usunięto wpis z Panelu sterowania.")
    except FileNotFoundError:
        print("ℹ️ Wpis rejestru już nie istnieje.")
    except PermissionError:
        print("❌ Brak uprawnień do usunięcia wpisu rejestru.")
    except Exception as e:
        print("❌ Błąd przy usuwaniu z rejestru:", e)

print("🛑 Kończenie działania wygaszacza...")
subprocess.run(["taskkill", "/IM", "wygaszacz.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["schtasks", "/End", "/TN", "WygaszaczEdukacyjny"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["schtasks", "/Delete", "/TN", "WygaszaczEdukacyjny", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Ścieżka do samego uninstall.exe
uninstall_exe_path = os.path.abspath(sys.argv[0])

# Tworzymy plik .bat, który poczeka aż uninstall się zakończy i usunie wszystko
bat_path = os.path.join(os.environ["TEMP"], "usun_wygaszacz.bat")
with open(bat_path, "w", encoding="utf-8") as f:
    f.write(f"""
@echo off
timeout /t 3 > nul
reg delete "HKLM\\{REG_PATH}" /f
rmdir /s /q "{folder}"
del "{uninstall_exe_path}"
del "%~f0"
""")

# Odpalamy .bat
print("📦 Zaplanowano usunięcie plików i wpisu rejestru...")
subprocess.Popen(['cmd', '/c', bat_path], creationflags=subprocess.CREATE_NO_WINDOW)

print("✅ Deinstalacja logiczna zakończona. Fizyczne usunięcie nastąpi za chwilę.")
input("Naciśnij Enter, aby zamknąć...")
