"""
Claude Code Floating Status Ball
A draggable, always-on-top status indicator with auto-detection via hooks.

Visual states:
  running    Emerald ball, smooth pulse ring
  waiting    Amber ball, blink (Claude needs permission / user input)
  completed  Indigo ball, steady
  error      Red ball, steady

Auto-integration:
  Reads ~/.claude/.floating_ball_status.json (updated by Claude Code hooks).
  PreToolUse → waiting, PostToolUse → running, Stop → completed,
  UserPromptSubmit → running.

Usage:
  pyw floating_ball.py
"""
import ctypes
import json
import math
import os
import sys
import threading
import time
from pathlib import Path

# ── DPI awareness (MUST be called before tkinter import) ──────
# Per-Monitor DPI V2 awareness — eliminates Windows blurry upscaling
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import tkinter as tk

# ── Configuration ──────────────────────────────────────────────
WIN_SIZE = 72
BALL_R = 30        # Ball radius (centered in window)
CENTER = WIN_SIZE // 2
DEFAULT_HPOS = 0.90
DEFAULT_VPOS = 0.70
CONFIG_DIR = Path.home() / '.claude'
STATUS_FILE = CONFIG_DIR / '.floating_ball_status.json'
POS_FILE = CONFIG_DIR / '.floating_ball_position.json'
LOCK_FILE = CONFIG_DIR / '.floating_ball.lock'
POLL_S = 0.8
ANIM_S = 0.05
ALPHA = 0.92

STATES = {
    'running':   {'fill': '#10B981', 'edge': '#059669', 'hi': '#34D399', 'text': 'CC', 'tcolor': '#D1FAE5'},
    'waiting':   {'fill': '#F59E0B', 'edge': '#D97706', 'hi': '#FBBF24', 'text': '?',  'tcolor': '#FEF3C7'},
    'completed': {'fill': '#6366F1', 'edge': '#4F46E5', 'hi': '#818CF8', 'text': '✓', 'tcolor': '#E0E7FF'},
    'error':     {'fill': '#EF4444', 'edge': '#DC2626', 'hi': '#F87171', 'text': '!',  'tcolor': '#FEE2E2'},
}

LABELS = {
    'running':   'Claude Code · Working',
    'waiting':   'Claude Code · Needs Your Input!',
    'completed': 'Claude Code · Task Completed',
    'error':     'Claude Code · Error',
}

# ── Single instance ────────────────────────────────────────────
def ensure_single():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            h = ctypes.windll.kernel32.OpenProcess(0x00100000, False, pid)
            if h:
                ctypes.windll.kernel32.CloseHandle(h)
                sys.exit(0)
        except (ValueError, OSError):
            pass
    LOCK_FILE.write_text(str(os.getpid()))

def cleanup():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass

# ── FloatingBall ───────────────────────────────────────────────
class FloatingBall:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', ALPHA)
        self._TK = '#010101'
        self.root.attributes('-transparentcolor', self._TK)
        self.root.configure(bg=self._TK)

        self.S = WIN_SIZE
        self.C = CENTER
        self.R = BALL_R

        self._status = 'running'
        self._alive = True
        self._drag = False
        self._blink = True
        self._phase = 0.0

        self._load_pos()
        self.root.geometry(f'{self.S}x{self.S}+{self._x}+{self._y}')

        self.canvas = tk.Canvas(
            self.root, width=self.S, height=self.S,
            highlightthickness=0, bg=self._TK, cursor='hand2'
        )
        self.canvas.pack()

        self._draw()
        self._build_menu()
        self._bind()

        self._th_poll = threading.Thread(target=self._poll, daemon=True)
        self._th_poll.start()
        self._th_anim = threading.Thread(target=self._anim, daemon=True)
        self._th_anim.start()

        self.root.deiconify()
        self.root.protocol('WM_DELETE_WINDOW', self._close)

    # ── Position ────────────────────────────────────────────
    def _default_pos(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = int(w * DEFAULT_HPOS) - self.C
        y = int(h * (1.0 - DEFAULT_VPOS)) - self.C
        return max(0, min(x, w - self.S)), max(0, min(y, h - self.S))

    def _load_pos(self):
        try:
            if POS_FILE.exists():
                d = json.loads(POS_FILE.read_text())
                x, y = d.get('x', -999), d.get('y', -999)
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                if -self.S < x < sw and -self.S < y < sh:
                    self._x, self._y = x, y
                    return
        except Exception:
            pass
        self._x, self._y = self._default_pos()

    def _save_pos(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            POS_FILE.write_text(json.dumps({'x': self._x, 'y': self._y}))
        except Exception:
            pass

    # ── Drawing ─────────────────────────────────────────────
    def _draw(self, pulse=0.0):
        self.canvas.delete('all')
        s = STATES.get(self._status, STATES['running'])
        R = self.R
        C = self.C

        # ── Outer glow (running pulse ring) ──
        if self._status == 'running' and pulse > 0.03:
            gr = R + 1 + int(pulse * 5)
            # pulse ring fades as it expands
            alpha_hex = f'{max(0, min(255, int((1.0 - pulse) * 80))):02x}'
            glow_color = f'#{alpha_hex}{s["fill"][1:]}'
            self.canvas.create_oval(
                C - gr, C - gr, C + gr, C + gr,
                fill='', outline=s['fill'], width=2
            )

        # ── Drop shadow ──
        so = 2
        self.canvas.create_oval(
            C - R + so, C - R + so + 1,
            C + R + so, C + R + so + 1,
            fill='#000000', outline='', width=0
        )

        # ── Main sphere ──
        self.canvas.create_oval(
            C - R, C - R, C + R, C + R,
            fill=s['fill'], outline=s['edge'], width=2
        )

        # ── Specular highlight (top-left crescent) ──
        hr = int(R * 0.55)
        hx = C - int(R * 0.22)
        hy = C - int(R * 0.22)
        self.canvas.create_oval(
            hx - hr, hy - hr, hx + hr, hy + hr,
            fill=s['hi'], outline='', width=0
        )

        # ── Inner shadow ring (depth) ──
        ir = R - 2
        self.canvas.create_oval(
            C - ir, C - ir, C + ir, C + ir,
            fill='', outline=s['edge'], width=1
        )

        # ── Center text ──
        fs = 22 if self._status in ('completed', 'error') else 17
        self.canvas.create_text(
            C, C + 1, text=s['text'], fill=s['tcolor'],
            font=('Segoe UI', fs, 'bold')
        )

    # ── Menu ────────────────────────────────────────────────
    def _build_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 9))
        self.menu.add_command(
            label='\U0001f7e2  Working', command=lambda: self.set_status('running'))
        self.menu.add_command(
            label='\U0001f7e0  Waiting for Input', command=lambda: self.set_status('waiting'))
        self.menu.add_command(
            label='\U0001f7e6  Completed', command=lambda: self.set_status('completed'))
        self.menu.add_command(
            label='\U0001f534  Error', command=lambda: self.set_status('error'))
        self.menu.add_separator()
        self.menu.add_command(label='Reset Position', command=self._reset_pos)
        self.menu.add_separator()
        self.menu.add_command(label='Exit', command=self._close)

    # ── Events ──────────────────────────────────────────────
    def _bind(self):
        for w in (self.canvas, self.root):
            w.bind('<ButtonPress-1>', self._press)
            w.bind('<B1-Motion>', self._dragmove)
            w.bind('<ButtonRelease-1>', self._release)
        self.canvas.bind('<Button-3>', self._menu)
        self.canvas.bind('<Double-Button-1>', self._dbl)
        self.canvas.bind('<Enter>', self._enter)
        self.canvas.bind('<Leave>', self._leave)

    def _press(self, ev):
        self._drag = True
        self._dsx, self._dsy = ev.x_root, ev.y_root
        self._dwx, self._dwy = self._x, self._y

    def _dragmove(self, ev):
        if not self._drag:
            return
        self._x = self._dwx + (ev.x_root - self._dsx)
        self._y = self._dwy + (ev.y_root - self._dsy)
        self.root.geometry(f'+{self._x}+{self._y}')

    def _release(self, ev):
        if self._drag:
            self._drag = False
            self._save_pos()

    def _menu(self, ev):
        self.menu.tk_popup(ev.x_root, ev.y_root)

    def _dbl(self, ev):
        order = ['running', 'waiting', 'completed', 'running']
        try:
            self.set_status(order[order.index(self._status) + 1])
        except (ValueError, IndexError):
            self.set_status('running')

    def _enter(self, ev):
        self._tt = tk.Toplevel(self.root)
        self._tt.overrideredirect(True)
        self._tt.attributes('-topmost', True)
        self._tt.configure(bg='#1F2937')
        tk.Label(
            self._tt, text=LABELS.get(self._status, 'Claude Code'),
            bg='#1F2937', fg='#F9FAFB', font=('Segoe UI', 10),
            padx=12, pady=6
        ).pack()
        x = ev.x_root + 18
        y = ev.y_root - 36
        self._tt.geometry(f'+{x}+{y}')

    def _leave(self, ev):
        try:
            if hasattr(self, '_tt') and self._tt:
                self._tt.destroy()
        except Exception:
            pass
        self._tt = None

    # ── Status ──────────────────────────────────────────────
    def set_status(self, status):
        if status not in STATES:
            return
        self._status = status
        self._draw()
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            STATUS_FILE.write_text(json.dumps({
                'status': status, 'timestamp': time.time()
            }))
        except Exception:
            pass

    def _reset_pos(self):
        self._x, self._y = self._default_pos()
        self.root.geometry(f'+{self._x}+{self._y}')
        self._save_pos()

    # ── Background loops ────────────────────────────────────
    def _poll(self):
        last_mtime = 0
        while self._alive:
            try:
                if STATUS_FILE.exists():
                    mtime = STATUS_FILE.stat().st_mtime
                    if mtime > last_mtime:
                        last_mtime = mtime
                        data = json.loads(STATUS_FILE.read_text())
                        ns = data.get('status')
                        if ns == 'exit':
                            self.root.after(0, self._close)
                            return
                        if ns and ns in STATES:
                            self.root.after(0, lambda s=ns: self.set_status(s))
            except Exception:
                pass
            time.sleep(POLL_S)

    def _anim(self):
        while self._alive:
            try:
                if self._status == 'running':
                    self._phase += ANIM_S * 3.0
                    v = 0.5 + 0.5 * math.sin(self._phase)
                    self.root.after(0, lambda p=v: self._draw(p))
                elif self._status == 'waiting':
                    self._blink = not self._blink
                    a = ALPHA if self._blink else 0.30
                    self.root.after(0, lambda a=a: self.root.attributes('-alpha', a))
                else:
                    self.root.after(0, lambda: self.root.attributes('-alpha', ALPHA))
            except Exception:
                pass
            time.sleep(ANIM_S if self._status in ('running', 'waiting') else 0.5)

    # ── Lifecycle ───────────────────────────────────────────
    def _close(self):
        self._alive = False
        self._save_pos()
        cleanup()
        self.root.quit()
        self.root.destroy()
        os._exit(0)

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._close()


def main():
    ensure_single()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    FloatingBall().run()

if __name__ == '__main__':
    main()
