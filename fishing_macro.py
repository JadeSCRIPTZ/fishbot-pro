"""
╔══════════════════════════════════════════════════════════════╗
║           FishBot Pro - Pixel Detection Fishing Macro        ║
║           Compatible with Minecraft & similar games          ║
║           Requires: pyautogui, tkinter (built-in)            ║
╚══════════════════════════════════════════════════════════════╝

Install dependencies:
    pip install pyautogui pillow

Run:
    python fishing_macro.py
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import sys

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to top-left corner to emergency stop
    pyautogui.PAUSE = 0.05
except ImportError:
    print("ERROR: pyautogui is not installed.")
    print("Run: pip install pyautogui pillow")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────
#  COLOUR PALETTE  (dark industrial theme)
# ──────────────────────────────────────────────────────────────
BG          = "#0f1117"
PANEL       = "#1a1d27"
ACCENT      = "#00c8ff"
ACCENT_DIM  = "#0090bb"
GREEN       = "#00e676"
GREEN_DIM   = "#00a854"
RED         = "#ff3d5a"
RED_DIM     = "#c0002e"
YELLOW      = "#ffd740"
TEXT        = "#e8eaf0"
TEXT_DIM    = "#7a7f99"
BORDER      = "#2a2f45"
INPUT_BG    = "#12151f"


# ──────────────────────────────────────────────────────────────
#  HELPER — styled rounded button (drawn on a Canvas)
# ──────────────────────────────────────────────────────────────
class FlatButton(tk.Canvas):
    """A flat, coloured button with hover animation built on Canvas."""

    def __init__(self, master, text, command,
                 bg=ACCENT, hover=ACCENT_DIM, fg=BG,
                 width=180, height=36, radius=8, **kw):
        super().__init__(master, width=width, height=height,
                         bg=PANEL, bd=0, highlightthickness=0, **kw)
        self._bg      = bg
        self._hover   = hover
        self._fg      = fg
        self._text    = text
        self._cmd     = command
        self._r       = radius
        self._w       = width
        self._h       = height
        self._enabled = True

        # Build canvas items ONCE — update via itemconfig, never delete/redraw
        pts = self._poly_pts(1, 1, width-1, height-1, radius)
        self._rect_id = self.create_polygon(pts, smooth=True,
                                            fill=bg, outline="")
        self._text_id = self.create_text(width//2, height//2,
                                         text=text, fill=fg,
                                         font=("Consolas", 10, "bold"))

        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    @staticmethod
    def _poly_pts(x1, y1, x2, y2, r):
        return [x1+r, y1,  x2-r, y1,
                x2,   y1,  x2,   y1+r,
                x2,   y2-r, x2,  y2,
                x2-r, y2,   x1+r, y2,
                x1,   y2,   x1,   y2-r,
                x1,   y1+r, x1,   y1]

    def _set_color(self, colour):
        self.itemconfig(self._rect_id, fill=colour)

    def _on_enter(self, _):
        if self._enabled:
            self._set_color(self._hover)

    def _on_leave(self, _):
        if self._enabled:
            self._set_color(self._bg)

    def set_enabled(self, state: bool):
        self._enabled = state
        self._set_color(self._bg if state else "#333655")
        self.itemconfig(self._text_id,
                        fill=self._fg if state else TEXT_DIM)

    def _on_click(self, _):
        if self._enabled and self._cmd:
            self._cmd()


# ──────────────────────────────────────────────────────────────
#  HELPER — styled label + entry pair
# ──────────────────────────────────────────────────────────────
def make_entry(parent, label_text, default="0", width=8):
    frame = tk.Frame(parent, bg=PANEL)
    tk.Label(frame, text=label_text, fg=TEXT_DIM, bg=PANEL,
             font=("Consolas", 9)).pack(side="left", padx=(0, 4))
    var = tk.StringVar(value=str(default))
    e = tk.Entry(frame, textvariable=var, width=width,
                 bg=INPUT_BG, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", bd=4,
                 font=("Consolas", 10), justify="center")
    e.pack(side="left")
    return frame, var


# ──────────────────────────────────────────────────────────────
#  HELPER — separator line
# ──────────────────────────────────────────────────────────────
def sep(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=8)


# ──────────────────────────────────────────────────────────────
#  COLOUR PREVIEW SWATCH
# ──────────────────────────────────────────────────────────────
class ColorSwatch(tk.Canvas):
    def __init__(self, master, size=22, **kw):
        super().__init__(master, width=size, height=size,
                         bg=PANEL, bd=0, highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        self._s = size
        self.set_color(0, 0, 0)

    def set_color(self, r, g, b):
        self.delete("all")
        hex_c = f"#{r:02x}{g:02x}{b:02x}"
        self.create_rectangle(0, 0, self._s, self._s, fill=hex_c, outline="")


# ──────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ──────────────────────────────────────────────────────────────
class FishBotApp:
    # Check interval in seconds
    POLL_INTERVAL = 0.05
    # Colour tolerance per channel
    TOLERANCE = 15

    def __init__(self, root: tk.Tk):
        self.root = root
        self._running   = False
        self._thread    = None
        self._countdown = None

        self._build_window()
        self._build_ui()

    # ── Window setup ──────────────────────────────────────────
    def _build_window(self):
        r = self.root
        r.title("FishBot Pro")
        r.configure(bg=BG)
        r.resizable(False, False)
        r.attributes("-topmost", True)

        # Centre on screen
        w, h = 420, 640
        sw, sh = r.winfo_screenwidth(), r.winfo_screenheight()
        r.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        # Custom title bar feel — thin accent strip at top
        tk.Frame(r, bg=ACCENT, height=3).pack(fill="x")

    # ── Full UI build ─────────────────────────────────────────
    def _build_ui(self):
        # ── Title ─────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(12, 4))

        tk.Label(header, text="🎣  FISHBOT PRO", fg=ACCENT, bg=BG,
                 font=("Consolas", 16, "bold")).pack(side="left")
        self.status_dot = tk.Label(header, text="●", fg=TEXT_DIM, bg=BG,
                                   font=("Consolas", 14))
        self.status_dot.pack(side="right")

        tk.Label(self.root, text="Pixel-detection fishing automation",
                 fg=TEXT_DIM, bg=BG, font=("Consolas", 9)).pack(anchor="w", padx=20)

        # ── Main card ─────────────────────────────────────────
        card = tk.Frame(self.root, bg=PANEL, bd=0)
        card.pack(fill="both", expand=True, padx=16, pady=12)

        inner = tk.Frame(card, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        # ── Section: Pixel Coordinates ────────────────────────
        tk.Label(inner, text="PIXEL COORDINATES", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w")
        sep(inner)

        coord_row = tk.Frame(inner, bg=PANEL)
        coord_row.pack(fill="x", pady=(0, 8))

        xf, self.x_var = make_entry(coord_row, "X:", "0", width=7)
        xf.pack(side="left", padx=(0, 16))
        yf, self.y_var = make_entry(coord_row, "Y:", "0", width=7)
        yf.pack(side="left")

        self.coord_status = tk.Label(inner, text="No coordinates captured yet.",
                                     fg=TEXT_DIM, bg=PANEL, font=("Consolas", 8))
        self.coord_status.pack(anchor="w", pady=(0, 6))

        self.get_pos_btn = FlatButton(inner, "🖱  Get Mouse Position",
                                       self._start_position_capture,
                                       bg=ACCENT, hover=ACCENT_DIM, fg=BG,
                                       width=210, height=34)
        self.get_pos_btn.pack(anchor="w", pady=4)

        # ── Section: Target Colour ────────────────────────────
        tk.Label(inner, text="TARGET COLOUR", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(14, 0))
        sep(inner)

        rgb_row = tk.Frame(inner, bg=PANEL)
        rgb_row.pack(fill="x", pady=(0, 6))

        rf, self.r_var = make_entry(rgb_row, "R:", "255", width=5)
        rf.pack(side="left", padx=(0, 8))
        gf, self.g_var = make_entry(rgb_row, "G:", "0",   width=5)
        gf.pack(side="left", padx=(0, 8))
        bf, self.b_var = make_entry(rgb_row, "B:", "0",   width=5)
        bf.pack(side="left", padx=(0, 12))

        self.swatch = ColorSwatch(rgb_row, size=28)
        self.swatch.pack(side="left", padx=4)

        self.color_status = tk.Label(inner, text="No colour sampled yet.",
                                     fg=TEXT_DIM, bg=PANEL, font=("Consolas", 8))
        self.color_status.pack(anchor="w", pady=(0, 6))

        self.get_color_btn = FlatButton(inner, "🎨  Get Colour Under Mouse",
                                         self._sample_color,
                                         bg=ACCENT, hover=ACCENT_DIM, fg=BG,
                                         width=220, height=34)
        self.get_color_btn.pack(anchor="w", pady=4)

        # ── Section: Tolerance ────────────────────────────────
        tk.Label(inner, text="COLOUR TOLERANCE", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(14, 0))
        sep(inner)

        tol_row = tk.Frame(inner, bg=PANEL)
        tol_row.pack(fill="x", pady=(0, 8))
        tf, self.tol_var = make_entry(tol_row, "±", str(self.TOLERANCE), width=5)
        tf.pack(side="left")
        tk.Label(tol_row, text="per RGB channel  (0–255)",
                 fg=TEXT_DIM, bg=PANEL, font=("Consolas", 8)).pack(side="left", padx=8)

        # ── Section: Macro Controls ───────────────────────────
        tk.Label(inner, text="MACRO CONTROL", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(14, 0))
        sep(inner)

        btn_row = tk.Frame(inner, bg=PANEL)
        btn_row.pack(fill="x", pady=4)

        self.start_btn = FlatButton(btn_row, "▶  START MACRO",
                                     self._start_macro,
                                     bg=GREEN, hover=GREEN_DIM, fg=BG,
                                     width=180, height=40)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = FlatButton(btn_row, "■  STOP MACRO",
                                    self._stop_macro,
                                    bg=RED, hover=RED_DIM, fg="#ffffff",
                                    width=180, height=40)
        self.stop_btn.pack(side="left")
        self.stop_btn.set_enabled(False)

        # ── Log / Activity ────────────────────────────────────
        tk.Label(inner, text="ACTIVITY LOG", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(14, 0))
        sep(inner)

        log_frame = tk.Frame(inner, bg=INPUT_BG, bd=0)
        log_frame.pack(fill="both", expand=True)

        self.log_box = tk.Text(log_frame, bg=INPUT_BG, fg=TEXT,
                               font=("Consolas", 8), relief="flat",
                               state="disabled", wrap="word",
                               bd=6, height=7,
                               insertbackground=ACCENT)
        self.log_box.pack(fill="both", expand=True)

        # Colour tags for log
        self.log_box.tag_config("info",    foreground=TEXT_DIM)
        self.log_box.tag_config("ok",      foreground=GREEN)
        self.log_box.tag_config("warn",    foreground=YELLOW)
        self.log_box.tag_config("error",   foreground=RED)
        self.log_box.tag_config("accent",  foreground=ACCENT)

        # ── Footer ────────────────────────────────────────────
        tk.Label(self.root,
                 text="⚠  PyAutoGUI failsafe: move mouse to top-left corner to emergency stop",
                 fg=YELLOW, bg=BG, font=("Consolas", 7)).pack(pady=(0, 6))

        self._log("FishBot Pro ready. Configure coordinates & colour, then start.", "info")
        self._log("Tip: Cast your rod first, THEN press START MACRO.", "accent")

    # ──────────────────────────────────────────────────────────
    #  LOGGING
    # ──────────────────────────────────────────────────────────
    def _log(self, message: str, tag: str = "info"):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ──────────────────────────────────────────────────────────
    #  GET MOUSE POSITION  (3-second countdown)
    # ──────────────────────────────────────────────────────────
    def _start_position_capture(self):
        self.get_pos_btn.set_enabled(False)
        self._do_countdown(3)

    def _do_countdown(self, n: int):
        if n > 0:
            self.coord_status.config(
                text=f"Move mouse to target pixel… capturing in {n}s",
                fg=YELLOW)
            self._countdown = self.root.after(1000, self._do_countdown, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.x_var.set(str(x))
                self.y_var.set(str(y))
                self.coord_status.config(
                    text=f"Captured: X={x}, Y={y}", fg=GREEN)
                self._log(f"Coordinates captured → X={x}, Y={y}", "ok")
            except Exception as exc:
                self.coord_status.config(text=f"Error: {exc}", fg=RED)
                self._log(f"Position capture error: {exc}", "error")
            finally:
                self.get_pos_btn.set_enabled(True)

    # ──────────────────────────────────────────────────────────
    #  SAMPLE COLOUR AT CAPTURED COORDINATES
    # ──────────────────────────────────────────────────────────
    def _sample_color(self):
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
        except ValueError:
            self._log("Invalid coordinates — enter integers first.", "error")
            return

        try:
            pixel = pyautogui.pixel(x, y)
            r, g, b = pixel[0], pixel[1], pixel[2]
            self.r_var.set(str(r))
            self.g_var.set(str(g))
            self.b_var.set(str(b))
            self.swatch.set_color(r, g, b)
            hex_c = f"#{r:02x}{g:02x}{b:02x}"
            self.color_status.config(
                text=f"Sampled at ({x},{y}): RGB({r},{g},{b})  {hex_c}", fg=GREEN)
            self._log(f"Colour sampled at ({x},{y}) → RGB({r},{g},{b})  {hex_c}", "ok")
        except Exception as exc:
            self.color_status.config(text=f"Error: {exc}", fg=RED)
            self._log(f"Colour sample error: {exc}", "error")

    # ──────────────────────────────────────────────────────────
    #  PARSE INPUTS (with validation)
    # ──────────────────────────────────────────────────────────
    def _parse_inputs(self):
        """Returns (x, y, r, g, b, tol) or raises ValueError."""
        x   = int(self.x_var.get())
        y   = int(self.y_var.get())
        r   = int(self.r_var.get())
        g   = int(self.g_var.get())
        b   = int(self.b_var.get())
        tol = int(self.tol_var.get())

        sw = pyautogui.size()
        if not (0 <= x < sw.width and 0 <= y < sw.height):
            raise ValueError(
                f"Coordinates ({x},{y}) are outside screen "
                f"({sw.width}×{sw.height}).")
        for name, val in (("R", r), ("G", g), ("B", b)):
            if not 0 <= val <= 255:
                raise ValueError(f"{name} value {val} must be 0–255.")
        if not 0 <= tol <= 255:
            raise ValueError(f"Tolerance {tol} must be 0–255.")

        return x, y, r, g, b, tol

    # ──────────────────────────────────────────────────────────
    #  MACRO LOOP  (runs in background thread)
    # ──────────────────────────────────────────────────────────
    def _macro_loop(self, x, y, tr, tg, tb, tol):
        self._log("Macro loop started. Watching pixel…", "ok")
        catches = 0

        while self._running:
            try:
                # ── Sample current pixel colour ───────────────
                pixel = pyautogui.pixel(x, y)
                cr, cg, cb = pixel[0], pixel[1], pixel[2]

                # ── Colour match check (with tolerance) ───────
                match = (abs(cr - tr) <= tol and
                         abs(cg - tg) <= tol and
                         abs(cb - tb) <= tol)

                if match:
                    catches += 1
                    self.root.after(0, self._log,
                                    f"[#{catches}] Bobber dipped! "
                                    f"Pixel=RGB({cr},{cg},{cb}) — reeling in…",
                                    "warn")

                    # ── Fishing sequence ──────────────────────
                    pyautogui.rightClick()          # 1. Reel in / cast
                    time.sleep(0.5)                 # 2. Wait 0.5 s
                    pyautogui.rightClick()          # 3. Cast again
                    time.sleep(3.0)                 # 4. Settle cooldown (3 s)

                    self.root.after(0, self._log,
                                    f"[#{catches}] Re-cast complete. Watching…",
                                    "ok")

            except pyautogui.FailSafeException:
                self.root.after(0, self._log,
                                "FailSafe triggered! Mouse moved to corner.", "error")
                break
            except OSError as exc:
                # Screen capture can fail if coordinates go off-screen mid-run
                self.root.after(0, self._log,
                                f"Screen capture error: {exc}", "error")
            except Exception as exc:
                self.root.after(0, self._log,
                                f"Unexpected error: {exc}", "error")
                break

            time.sleep(self.POLL_INTERVAL)

        self._running = False
        self.root.after(0, self._on_macro_stopped)

    # ──────────────────────────────────────────────────────────
    #  START / STOP
    # ──────────────────────────────────────────────────────────
    def _start_macro(self):
        if self._running:
            return
        try:
            x, y, r, g, b, tol = self._parse_inputs()
        except ValueError as exc:
            self._log(f"Input error: {exc}", "error")
            return

        self._running = True
        self._update_status(running=True)

        self._thread = threading.Thread(
            target=self._macro_loop,
            args=(x, y, r, g, b, tol),
            daemon=True)
        self._thread.start()

        self._log(
            f"START → watching ({x},{y}) for RGB({r},{g},{b}) ±{tol}", "accent")

    def _stop_macro(self):
        if not self._running:
            return
        self._running = False
        self._log("Stop requested — finishing current cycle…", "warn")

    def _on_macro_stopped(self):
        self._update_status(running=False)
        self._log("Macro stopped.", "info")

    # ──────────────────────────────────────────────────────────
    #  UI STATE  (status dot + button states)
    # ──────────────────────────────────────────────────────────
    def _update_status(self, running: bool):
        if running:
            self.status_dot.config(fg=GREEN, text="●")
            self.start_btn.set_enabled(False)
            self.stop_btn.set_enabled(True)
            self.get_pos_btn.set_enabled(False)
            self.get_color_btn.set_enabled(False)
        else:
            self.status_dot.config(fg=TEXT_DIM, text="●")
            self.start_btn.set_enabled(True)
            self.stop_btn.set_enabled(False)
            self.get_pos_btn.set_enabled(True)
            self.get_color_btn.set_enabled(True)

    # ──────────────────────────────────────────────────────────
    #  CLEAN EXIT
    # ──────────────────────────────────────────────────────────
    def on_close(self):
        self._running = False
        self.root.destroy()


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    app  = FishBotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
