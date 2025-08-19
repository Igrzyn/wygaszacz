
import tkinter as tk
import random
import keyboard
import threading
import time
import sys

IMIE = sys.argv[1] if len(sys.argv) > 1 else "Dziecko"

class Wygaszacz:
    def __init__(self, root):
        self.root = root
        self.root.title("Wygaszacz edukacyjny")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", self.zablokuj_zamkniecie)

        self.answer = None
        self.entry = None
        self.feedback = None
        self.timer_label = None
        self.countdown_job = None

        self.blokuj_szkodliwe_klawisze()
        self.generate_question()

    def zablokuj_zamkniecie(self):
        pass

    def blokuj_szkodliwe_klawisze(self):
        def petla_blokowania():
            while True:
                for kombinacja in [
                    "alt", "tab", "alt+tab", "left windows", "right windows", "windows",
                    "ctrl+esc", "alt+esc", "alt+f4"
                ]:
                    try:
                        keyboard.block_key(kombinacja)
                    except:
                        pass
                time.sleep(0.1)

        threading.Thread(target=petla_blokowania, daemon=True).start()

    def generate_question(self):
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.timer_label = tk.Label(self.root, text="", font=("Helvetica", 28), fg="yellow", bg="black")
        self.timer_label.pack(pady=20)

        label = tk.Label(self.root, text=f"{IMIE.upper()}! Rozwiąż działanie, by dalej korzystać z komputera.", font=("Helvetica", 32), fg="white", bg="black")
        label.pack(pady=40)

        a, b = random.randint(1, 10), random.randint(1, 10)
        self.answer = a * b

        frame = tk.Frame(self.root, bg="black")
        frame.pack(pady=10)

        label = tk.Label(frame, text=f"{a} × {b} =", font=("Helvetica", 32), fg="white", bg="black")
        label.pack(side="left")

        self.entry = tk.Entry(frame, font=("Helvetica", 32), width=5, justify="center")
        self.entry.pack(side="left")
        self.entry.bind("<Return>", lambda e: self.sprawdz())
        self.entry.bind("<Key>", self.blokuj_litery)
        self.entry.focus_set()

        self.feedback = tk.Label(self.root, text="", font=("Helvetica", 32), fg="white", bg="black")
        self.feedback.pack(pady=30)

        self.submit_btn = tk.Button(self.root, text="Sprawdź", font=("Helvetica", 32), command=self.sprawdz)
        self.submit_btn.pack(pady=20)

    def blokuj_litery(self, event):
        if not event.char.isdigit() and event.keysym not in ("BackSpace", "Return"):
            return "break"

    def sprawdz(self):
        tekst = self.entry.get().strip()
        if tekst == "":
            return

        try:
            user_value = int(tekst)
            if user_value == self.answer:
                self.entry.config(fg="green")
                self.feedback.config(
                    text=f"✅ Brawo {IMIE}! Zaczynasz wymiatać w tabliczce mnożenia!",
                    fg="lightgreen"
                )
                self.odblokuj()
                self.root.after(2000, self.root.destroy)
            else:
                self.entry.config(fg="red")
                self.feedback.config(
                    text=f"❌ Zła odpowiedź!Poprawna odpowiedź to: {self.answer}",
                    fg="red"
                )
                self.odliczanie(5)
        except ValueError:
            self.entry.config(fg="red")
            self.feedback.config(text="❌ Wpisz liczbę.", fg="red")
            self.odliczanie(5)

    def odliczanie(self, sekundy):
        if sekundy < 0:
            self.generate_question()
        else:
            self.timer_label.config(text=f"Nowe pytanie za {sekundy} sekund...")
            self.countdown_job = self.root.after(1000, self.odliczanie, sekundy - 1)

    def odblokuj(self):
        keyboard.unhook_all()

if __name__ == "__main__":
    root = tk.Tk()
    app = Wygaszacz(root)
    root.mainloop()
