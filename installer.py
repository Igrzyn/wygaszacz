import os
import subprocess
import sys
import ctypes
import shutil
import winreg
import tempfile
import textwrap
import traceback

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    executable = sys.executable
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    sys.exit()

def zapisz_do_rejestru(imie, uninstall_path, install_dir):
    try:
        klucz = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall\WygaszaczEdukacyjny"
        )
        winreg.SetValueEx(klucz, "DisplayName", 0, winreg.REG_SZ, f"Wygaszacz Edukacyjny ({imie})")
        winreg.SetValueEx(klucz, "UninstallString", 0, winreg.REG_SZ, f'"{uninstall_path}" "{install_dir}"')
        winreg.SetValueEx(klucz, "InstallLocation", 0, winreg.REG_SZ, install_dir)
        winreg.SetValueEx(klucz, "Publisher", 0, winreg.REG_SZ, "Desengi")
        winreg.SetValueEx(klucz, "DisplayVersion", 0, winreg.REG_SZ, "1.0")
        winreg.SetValueEx(klucz, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(klucz, "NoRepair", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(klucz)
        print("✅ Zarejestrowano deinstalator w Panelu sterowania.")
    except Exception as e:
        print("❌ Błąd rejestru:", e)

def main():
    print("=== Instalator Wygaszacza Edukacyjnego ===\n")

    imie = input("Podaj imię dziecka: ").strip()
    if not imie:
        print("❌ Imię nie może być puste.")
        return

    print("\nWybierz częstotliwość:")
    print("1) Co 5 minut")
    print("2) Co 15 minut")
    print("3) Co 30 minut")
    print("4) Co 60 minut")
    czest_map = {"1": "5", "2": "15", "3": "30", "4": "60"}
    wybor = input("Twój wybór (1-4): ").strip()
    czestotliwosc = czest_map.get(wybor)
    if not czestotliwosc:
        print("❌ Nieprawidłowy wybór.")
        return
    # Ustalanie folderu, w którym znajdują się pliki po rozpakowaniu
    if getattr(sys, 'frozen', False):
        # Jeśli uruchomiono z pliku .exe stworzonego przez PyInstaller
        bundle_dir = sys._MEIPASS
    else:
        # Jeśli uruchomiono z pliku .py
        bundle_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    folder_docelowy = os.path.join(os.environ["ProgramFiles"], "WygaszaczEdukacyjny")
    os.makedirs(folder_docelowy, exist_ok=True)

    folder_biezacy = os.path.dirname(os.path.abspath(sys.argv[0]))
        # Poprawne ścieżki do spakowanych plików
    src_wygaszacz = os.path.join(bundle_dir, "wygaszacz.exe")
    src_uninstall = os.path.join(bundle_dir, "uninstall.exe")

    dst_wygaszacz = os.path.join(folder_docelowy, "wygaszacz.exe")
    dst_uninstall = os.path.join(folder_docelowy, "uninstall.exe")
    
    try:
        shutil.copy2(src_wygaszacz, dst_wygaszacz)
        shutil.copy2(src_uninstall, dst_uninstall)
        print("✅ Skopiowano pliki.")
    except Exception as e:
        print("❌ Błąd kopiowania:", e)
        return

    try:
        shutil.copy2(src_wygaszacz, dst_wygaszacz)
        shutil.copy2(src_uninstall, dst_uninstall)
        print("✅ Skopiowano pliki.")
    except Exception as e:
        print("❌ Błąd kopiowania:", e)
        return

    # 🔁 Tworzenie zadania PowerShell (z obsługą baterii)
    ps_script = textwrap.dedent(f"""
    $action = New-ScheduledTaskAction -Execute "{dst_wygaszacz}" -Argument '"{imie}"'
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes {czestotliwosc}) `
    -RepetitionDuration (New-TimeSpan -Days 365)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -TaskName "WygaszaczEdukacyjny" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
    """)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8") as ps_file:
        ps_file.write(ps_script)
        ps_path = ps_file.name

    try:
        subprocess.run([
            "powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path
        ], check=True)
        print("✅ Zadanie utworzone (PowerShell).")
    except subprocess.CalledProcessError as e:
        print("❌ Błąd przy tworzeniu zadania:", e)
        return

    zapisz_do_rejestru(imie, dst_uninstall, folder_docelowy)

    print("\n✅ Instalacja zakończona!")
    input("Naciśnij Enter, aby zamknąć instalator...")

if __name__ == "__main__":
    try:
        if not is_admin():
            print("⚠️ Potrzebne uprawnienia administratora. Uruchamiam ponownie...")
            restart_as_admin()
        main()
    except Exception as e:
        print("\n❌ Błąd krytyczny:", e)
        traceback.print_exc()
        input("🔴 Naciśnij Enter, aby zamknąć...")
