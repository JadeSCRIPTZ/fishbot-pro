"""
FishBot Pro - Pixel Detection Fishing Macro
Compatible with Minecraft & similar games
"""

import tkinter as tk
import threading
import time
import sys

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
except ImportError:
    print("ERROR: Run:  pip install pyautogui pillow")
    sys.exit(1)

# ── Palette ────────────────────────────────────────────────────
BG       = "#0f1117"
PANEL    = "#1a1d27"
ACCENT   = "#00c8ff"
GREEN    = "#00e676"
GREEN_D  = "#00a854"
RED      = "#ff3d5a"
RED_D    = "#c0002e"
YELLOW   = "#ffd740"
TEXT     = "#e8eaf0"
TEXT_DIM = "#7a7f99"
BORDER   = "#2a2f45"
INPUT_BG = "#12151f"


def flat_btn(parent, label, cmd, bg=ACCENT, fg=BG,
             abg=None, width=22, padx=8, pady=6):
    """Simple tk.Button with custom colours — no Canvas, no crashes."""
    b = tk.Button(
        parent, text=label, command=cmd,
        bg=bg, fg=fg,
        activebackground=abg or bg,
        activeforeground=fg,
        relief="flat", bd=0,
        font=("Consolas", 10, "bold"),
        cursor="hand2",
        width=width, padx=padx, pady=pady,
        disabledforeground="#555a77",
    )
    return b


def make_entry(parent, label_text, default="0", width=8):
    frame = tk.Frame(parent, bg=PANEL)
    tk.Label(frame, text=label_text, fg=TEXT_DIM, bg=PANEL,
             font=("Consolas", 9)).pack(side="left", padx=(0, 4))
    var = tk.StringVar(value=str(default))
    tk.Entry(frame, textvariable=var, width=width,
             bg=INPUT_BG, fg=TEXT, insertbackground=ACCENT,
             relief="flat", bd=4, font=("Consolas", 10),
             justify="center").pack(side="left")
    return frame, var


def sep(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=7)


class ColorSwatch(tk.Frame):
    def __init__(self, master, size=26, **kw):
        super().__init__(master, width=size, height=size,
                         bg="#000000", bd=1, relief="flat", **kw)
        self.pack_propagate(False)
        self._lbl = tk.Label(self, bg="#000000", width=size, height=size)
        self._lbl.pack(fill="both", expand=True)

    def set_color(self, r, g, b):
        hex_c = f"#{r:02x}{g:02x}{b:02x}"
        self.config(bg=hex_c)
        self._lbl.config(bg=hex_c)


# ── Main App ───────────────────────────────────────────────────
class FishBotApp:
    POLL     = 0.05
    TOLERACE = 15

    def __init__(self, root: tk.Tk):
        self.root      = root
        self._running  = False
        self._thread   = None
        self._build_window()
        self._build_ui()

    # ── Window ─────────────────────────────────────────────────
    def _build_window(self):
        self.root.title("FishBot Pro")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        w, h = 430, 650
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x")

    # ── UI ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(12, 2))
        tk.Label(hdr, text="🎣  FISHBOT PRO", fg=ACCENT, bg=BG,
                 font=("Consolas", 16, "bold")).pack(side="left")
        self.dot = tk.Label(hdr, text="●", fg=TEXT_DIM, bg=BG,
                            font=("Consolas", 14))
        self.dot.pack(side="right")
        tk.Label(self.root, text="Pixel-detection fishing automation",
                 fg=TEXT_DIM, bg=BG, font=("Consolas", 9)).pack(anchor="w", padx=20)

        # Card
        card  = tk.Frame(self.root, bg=PANEL)
        card.pack(fill="both", expand=True, padx=14, pady=10)
        inner = tk.Frame(card, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=14, pady=14)

        # ── Coordinates ──────────────────────────────────────
        tk.Label(inner, text="PIXEL COORDINATES", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w")
        sep(inner)

        cr = tk.Frame(inner, bg=PANEL)
        cr.pack(fill="x", pady=(0, 6))
        xf, self.x_var = make_entry(cr, "X:", "0", 7)
        xf.pack(side="left", padx=(0, 16))
        yf, self.y_var = make_entry(cr, "Y:", "0", 7)
        yf.pack(side="left")

        self.coord_lbl = tk.Label(inner, text="No coordinates captured yet.",
                                  fg=TEXT_DIM, bg=PANEL, font=("Consolas", 8))
        self.coord_lbl.pack(anchor="w", pady=(0, 5))

        self.pos_btn = flat_btn(inner, "🖱  Get Mouse Position",
                                self._start_capture, bg=ACCENT, fg=BG,
                                abg="#0090bb", width=24)
        self.pos_btn.pack(anchor="w", pady=3)

        # ── Target colour ─────────────────────────────────────
        tk.Label(inner, text="TARGET COLOUR", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(12, 0))
        sep(inner)

        rgbr = tk.Frame(inner, bg=PANEL)
        rgbr.pack(fill="x", pady=(0, 5))
        rf, self.r_var = make_entry(rgbr, "R:", "255", 5)
        rf.pack(side="left", padx=(0, 8))
        gf, self.g_var = make_entry(rgbr, "G:", "0",   5)
        gf.pack(side="left", padx=(0, 8))
        bf, self.b_var = make_entry(rgbr, "B:", "0",   5)
        bf.pack(side="left", padx=(0, 10))
        self.swatch = ColorSwatch(rgbr, size=26)
        self.swatch.pack(side="left", padx=4)

        self.color_lbl = tk.Label(inner, text="No colour sampled yet.",
                                  fg=TEXT_DIM, bg=PANEL, font=("Consolas", 8))
        self.color_lbl.pack(anchor="w", pady=(0, 5))

        self.col_btn = flat_btn(inner, "🎨  Get Colour Under Mouse",
                                self._sample_color, bg=ACCENT, fg=BG,
                                abg="#0090bb", width=26)
        self.col_btn.pack(anchor="w", pady=3)

        # ── Tolerance ─────────────────────────────────────────
        tk.Label(inner, text="COLOUR TOLERANCE", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(12, 0))
        sep(inner)
        tolr = tk.Frame(inner, bg=PANEL)
        tolr.pack(fill="x", pady=(0, 6))
        tf, self.tol_var = make_entry(tolr, "±", str(self.TOLERACE), 5)
        tf.pack(side="left")
        tk.Label(tolr, text="per RGB channel  (0–255)",
                 fg=TEXT_DIM, bg=PANEL, font=("Consolas", 8)).pack(side="left", padx=8)

        # ── Macro buttons ─────────────────────────────────────
        tk.Label(inner, text="MACRO CONTROL", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(12, 0))
        sep(inner)
        br = tk.Frame(inner, bg=PANEL)
        br.pack(fill="x", pady=3)

        self.start_btn = flat_btn(br, "▶  START MACRO",
                                  self._start_macro,
                                  bg=GREEN, fg=BG, abg=GREEN_D, width=18)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = flat_btn(br, "■  STOP MACRO",
                                 self._stop_macro,
                                 bg=RED, fg="#ffffff", abg=RED_D, width=18)
        self.stop_btn.pack(side="left")
        self.stop_btn.config(state="disabled")

        # ── Log ───────────────────────────────────────────────
        tk.Label(inner, text="ACTIVITY LOG", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(12, 0))
        sep(inner)
        self.log = tk.Text(inner, bg=INPUT_BG, fg=TEXT,
                           font=("Consolas", 8), relief="flat",
                           state="disabled", wrap="word", bd=4, height=7)
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("info",   foreground=TEXT_DIM)
        self.log.tag_config("ok",     foreground=GREEN)
        self.log.tag_config("warn",   foreground=YELLOW)
        self.log.tag_config("error",  foreground=RED)
        self.log.tag_config("accent", foreground=ACCENT)

        # Footer
        tk.Label(self.root,
                 text="⚠  Failsafe: mută mouse-ul în colțul stânga-sus pentru oprire urgentă",
                 fg=YELLOW, bg=BG, font=("Consolas", 7)).pack(pady=(0, 6))

        self._log("FishBot Pro gata. Setează coordonatele și culoarea.", "info")
        self._log("Sfat: Aruncă undița ÎNAINTE să apeși START.", "accent")

    # ── Logging ────────────────────────────────────────────────
    def _log(self, msg, tag="info"):
        ts = time.strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{ts}] {msg}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ── Capture position ───────────────────────────────────────
    def _start_capture(self):
        self.pos_btn.config(state="disabled")
        self._countdown(3)

    def _countdown(self, n):
        if n > 0:
            self.coord_lbl.config(
                text=f"Mută mouse-ul pe bobber… captură în {n}s", fg=YELLOW)
            self.root.after(1000, self._countdown, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.x_var.set(str(x))
                self.y_var.set(str(y))
                self.coord_lbl.config(text=f"Capturat: X={x}, Y={y}", fg=GREEN)
                self._log(f"Coordonate → X={x}, Y={y}", "ok")
            except Exception as e:
                self.coord_lbl.config(text=f"Eroare: {e}", fg=RED)
                self._log(f"Eroare captură: {e}", "error")
            finally:
                self.pos_btn.config(state="normal")

    # ── Sample colour ──────────────────────────────────────────
    def _sample_color(self):
        try:
            x, y = int(self.x_var.get()), int(self.y_var.get())
        except ValueError:
            self._log("Coordonate invalide — introdu numere întregi.", "error")
            return
        try:
            px = pyautogui.pixel(x, y)
            r, g, b = px[0], px[1], px[2]
            self.r_var.set(str(r))
            self.g_var.set(str(g))
            self.b_var.set(str(b))
            self.swatch.set_color(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self.color_lbl.config(
                text=f"Eșantion la ({x},{y}): RGB({r},{g},{b})  {hx}", fg=GREEN)
            self._log(f"Culoare → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self.color_lbl.config(text=f"Eroare: {e}", fg=RED)
            self._log(f"Eroare culoare: {e}", "error")

    # ── Validate inputs ────────────────────────────────────────
    def _parse(self):
        x   = int(self.x_var.get())
        y   = int(self.y_var.get())
        r   = int(self.r_var.get())
        g   = int(self.g_var.get())
        b   = int(self.b_var.get())
        tol = int(self.tol_var.get())
        sc  = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) în afara ecranului.")
        for n, v in (("R", r), ("G", g), ("B", b)):
            if not 0 <= v <= 255:
                raise ValueError(f"{n}={v} trebuie să fie 0-255.")
        if not 0 <= tol <= 255:
            raise ValueError(f"Toleranță {tol} invalidă.")
        return x, y, r, g, b, tol

    # ── Macro loop ─────────────────────────────────────────────
    # State machine cu 2 stari:
    #   "RESET" → asteapta ca pixelul sa NU mai fie culoarea tinta
    #             (bobberul disparut / aruncat din nou)
    #   "WATCH" → asteapta ca pixelul sa DEVINA culoarea tinta
    #             (bobberul se scufunda = pesti!)
    # Astfel nu poate triggera de doua ori pe acelasi eveniment.
    def _loop(self, x, y, tr, tg, tb, tol):
        self._log("Macro pornit. Astept bobber nou…", "ok")
        catches = 0

        # Pornim in RESET: asteptam mai intai ca pixelul sa nu fie match
        # (in cazul in care il pornesti cu bobberul deja in apa)
        state = "RESET"
        self.root.after(0, self._log, "Stare: RESET — astept ca pixelul sa fie normal…", "dim")

        while self._running:
            try:
                px = pyautogui.pixel(x, y)
                cr, cg, cb = px[0], px[1], px[2]
                is_match = (abs(cr - tr) <= tol and
                            abs(cg - tg) <= tol and
                            abs(cb - tb) <= tol)

                if state == "RESET":
                    # Asteptam ca pixelul sa NU mai fie culoarea tinta
                    if not is_match:
                        state = "WATCH"
                        self.root.after(0, self._log,
                            "Stare: WATCH — monitorizez bobberul…", "accent")

                elif state == "WATCH":
                    # Asteptam ca pixelul sa DEVINA culoarea tinta
                    if is_match:
                        catches += 1
                        self.root.after(0, self._log,
                            f"[#{catches}] Bobber scufundat! RGB({cr},{cg},{cb}) — trag…",
                            "warn")

                        # ── Secventa fishing ─────────────────────────
                        pyautogui.rightClick()        # 1. Trage undita
                        time.sleep(0.5)               # 2. Pauza 0.5s
                        pyautogui.rightClick()        # 3. Arunca din nou
                        time.sleep(3.0)               # 4. Cooldown 3s (bobber se asaza)
                        # ─────────────────────────────────────────────

                        self.root.after(0, self._log,
                            f"[#{catches}] Re-aruncat. Astept resetare pixel…", "ok")

                        # Dupa actiune ne intoarcem in RESET pentru a evita
                        # re-triggerarea pe acelasi pixel (bug original)
                        state = "RESET"

            except pyautogui.FailSafeException:
                self.root.after(0, self._log, "FailSafe! Mouse în colț.", "error")
                break
            except Exception as e:
                self.root.after(0, self._log, f"Eroare: {e}", "error")
                break

            time.sleep(self.POLL)

        self._running = False
        self.root.after(0, self._stopped)

    # ── Start / Stop ───────────────────────────────────────────
    def _start_macro(self):
        if self._running:
            return
        try:
            args = self._parse()
        except ValueError as e:
            self._log(f"Eroare input: {e}", "error")
            return
        self._running = True
        self._set_ui(running=True)
        self._thread = threading.Thread(target=self._loop, args=args, daemon=True)
        self._thread.start()
        x, y, r, g, b, tol = args
        self._log(f"START → ({x},{y}) RGB({r},{g},{b}) ±{tol}", "accent")

    def _stop_macro(self):
        self._running = False
        self._log("Oprire solicitată…", "warn")

    def _stopped(self):
        self._set_ui(running=False)
        self._log("Macro oprit.", "info")

    def _set_ui(self, running):
        if running:
            self.dot.config(fg=GREEN)
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.pos_btn.config(state="disabled")
            self.col_btn.config(state="disabled")
        else:
            self.dot.config(fg=TEXT_DIM)
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.pos_btn.config(state="normal")
            self.col_btn.config(state="normal")

    def on_close(self):
        self._running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app  = FishBotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
