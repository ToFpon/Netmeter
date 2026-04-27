#!/usr/bin/env python3
"""
netmeter.py — Network bandwidth monitor for Linux / GTK4
v2 — fenêtre redimensionnable, always-on-top corrigé,
     vue lignes ET vue barres avec graduation Y
Requires: python3-gi (GTK4), python3-gi-cairo, python3-psutil
          wmctrl  (apt install wmctrl)
License: GPLv3
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio
import cairo
import psutil
import subprocess
import time
import math
from collections import deque

# ── Constants ────────────────────────────────────────────────────────────────

HISTORY      = 120        # secondes conservées dans le graphe
TICK_MS      = 1000       # intervalle de rafraîchissement (ms)
WIN_W, WIN_H = 460, 230   # taille par défaut (resizable)
LM           = 62         # left margin pour les labels Y (px)

# Couleurs (R, G, B[, A]) entre 0 et 1
C_DL    = (0.25, 0.73, 0.31)
C_UL    = (0.97, 0.50, 0.40)
C_BG    = (0.05, 0.07, 0.09)
C_LABEL = (0.45, 0.52, 0.60, 0.85)
C_AXIS  = (1.0,  1.0,  1.0,  0.18)


# ── Helpers ──────────────────────────────────────────────────────────────────

def fmt_speed(bps: float, unit: str) -> str:
    if unit == 'Mbit/s':
        return f"{bps * 8 / 1e6:.2f} Mbit/s"
    kbps = bps / 1024
    if kbps >= 1024:
        return f"{kbps / 1024:.2f} MB/s"
    return f"{kbps:.1f} KB/s"


def fmt_total(b: float) -> str:
    if b >= 1024 ** 3:
        return f"{b / 1024**3:.2f} GB"
    if b >= 1024 ** 2:
        return f"{b / 1024**2:.2f} MB"
    return f"{b / 1024:.1f} KB"


def nice_ceil(value: float) -> float:
    """Arrondit au-dessus à une valeur 'ronde' pour l'échelle Y."""
    if value <= 0:
        return 1024.0
    mag = 10 ** math.floor(math.log10(value))
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        c = m * mag
        if c >= value:
            return float(c)
    return float(value * 1.1)


# ── Graph widget ─────────────────────────────────────────────────────────────

class NetGraph(Gtk.DrawingArea):
    """
    Graphe réseau défilant — deux modes :
      'lines' → courbes remplies (style oscilloscope)
      'bars'  → barres verticales colorées avec graduation Y
    """

    MODES = ['lines', 'bars']

    def __init__(self):
        super().__init__()
        self.dl:   deque = deque([0.0] * HISTORY, maxlen=HISTORY)
        self.ul:   deque = deque([0.0] * HISTORY, maxlen=HISTORY)
        self.mode  = 'lines'
        self._unit = 'KB/s'

        self.set_draw_func(self._draw)
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_size_request(-1, 110)

    # ── API publique ──────────────────────────────────────────────────────────

    def push(self, dl: float, ul: float):
        self.dl.append(dl)
        self.ul.append(ul)
        self.queue_draw()

    def cycle_mode(self) -> str:
        self.mode = self.MODES[(self.MODES.index(self.mode) + 1) % len(self.MODES)]
        self.queue_draw()
        return self.mode

    # ── Dispatch principal ────────────────────────────────────────────────────

    def _draw(self, _area, cr, w: int, h: int):
        cr.set_source_rgb(*C_BG)
        cr.paint()

        peak = nice_ceil(max(max(self.dl, default=0),
                             max(self.ul, default=0), 1024))

        self._draw_yaxis(cr, w, h, peak)

        if self.mode == 'bars':
            self._draw_bars(cr, w, h, peak)
        else:
            self._draw_lines(cr, w, h, peak)

        self._draw_legend(cr, h)

    # ── Vue lignes ────────────────────────────────────────────────────────────

    def _draw_lines(self, cr, w: int, h: int, peak: float):
        n = len(self.dl)
        if n < 2:
            return
        gw = w - LM
        top, bot = 10, 6

        def _curve(data, colour):
            pts = [
                (LM + i * gw / (n - 1),
                 h - bot - (v / peak) * (h - top - bot))
                for i, v in enumerate(data)
            ]
            r, g, b = colour

            # aire remplie sous la courbe
            cr.set_source_rgba(r, g, b, 0.14)
            cr.move_to(pts[0][0], h - bot)
            for x, y in pts:
                cr.line_to(x, y)
            cr.line_to(pts[-1][0], h - bot)
            cr.close_path()
            cr.fill()

            # ligne principale
            cr.set_source_rgba(r, g, b, 0.92)
            cr.set_line_width(1.7)
            cr.move_to(*pts[0])
            for x, y in pts[1:]:
                cr.line_to(x, y)
            cr.stroke()

        _curve(self.ul, C_UL)   # UL derrière
        _curve(self.dl, C_DL)   # DL devant

    # ── Vue barres ────────────────────────────────────────────────────────────

    def _draw_bars(self, cr, w: int, h: int, peak: float):
        n   = len(self.dl)
        gw  = w - LM
        bot = 6

        bpw = max(3.0, gw / n)          # largeur d'une paire
        sw  = max(1.0, (bpw - 2) / 2)   # largeur d'une barre

        for i, (dl, ul) in enumerate(zip(self.dl, self.ul)):
            x = LM + i * bpw

            bh = (dl / peak) * (h - bot - 4)
            if bh > 0.5:
                r, g, b = C_DL
                self._bar(cr, x, h - bot - bh, sw, bh, r, g, b)

            bh = (ul / peak) * (h - bot - 4)
            if bh > 0.5:
                r, g, b = C_UL
                self._bar(cr, x + sw + 1, h - bot - bh, sw, bh, r, g, b)

    @staticmethod
    def _bar(cr, x, y, w, h, r, g, b):
        """Barre avec coins supérieurs arrondis et reflet."""
        rad = min(2.5, w / 2, h / 2)
        cr.set_source_rgba(r, g, b, 0.82)
        if rad > 0 and h > rad * 2:
            cr.move_to(x + rad, y)
            cr.arc(x + w - rad, y + rad,     rad, -math.pi / 2, 0)
            cr.arc(x + w - rad, y + h - rad, rad, 0,            math.pi / 2)
            cr.arc(x + rad,     y + h - rad, rad, math.pi / 2,  math.pi)
            cr.arc(x + rad,     y + rad,     rad, math.pi,      3 * math.pi / 2)
            cr.close_path()
        else:
            cr.rectangle(x, y, w, h)
        cr.fill()

        # highlight sommital
        ht = min(4.0, h * 0.25)
        cr.set_source_rgba(min(1, r + 0.25), min(1, g + 0.15), min(1, b + 0.1), 0.40)
        cr.rectangle(x + 1, y + 1, max(0, w - 2), ht)
        cr.fill()

    # ── Axe Y + graduation ────────────────────────────────────────────────────

    def _draw_yaxis(self, cr, w: int, h: int, peak: float):
        cr.select_font_face("monospace",
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(9)

        ticks = 4
        bot, top = 6, 10

        for i in range(1, ticks + 1):
            frac = i / ticks
            y    = h - bot - frac * (h - top - bot)
            val  = peak * frac

            # Ligne de grille pointillée
            alpha = 0.11 if i % 2 == 0 else 0.05
            cr.set_source_rgba(1, 1, 1, alpha)
            cr.set_line_width(0.5)
            cr.set_dash([4.0, 5.0])
            cr.move_to(LM, y)
            cr.line_to(w, y)
            cr.stroke()
            cr.set_dash([])

            # Label de vitesse
            label = fmt_speed(val, self._unit)
            ext   = cr.text_extents(label)
            cr.set_source_rgba(*C_LABEL)
            cr.move_to(LM - ext.width - 5, y + ext.height / 2)
            cr.show_text(label)

        # Axe vertical
        cr.set_source_rgba(*C_AXIS)
        cr.set_line_width(0.8)
        cr.set_dash([])
        cr.move_to(LM, top)
        cr.line_to(LM, h - bot)
        cr.stroke()

        # Baseline
        cr.move_to(LM, h - bot)
        cr.line_to(w,  h - bot)
        cr.stroke()

    # ── Légende inline ────────────────────────────────────────────────────────

    def _draw_legend(self, cr, h: int):
        cr.select_font_face("monospace",
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(9)
        x = LM + 8
        for label, colour in (("↓ DL", C_DL), ("↑ UL", C_UL)):
            r, g, b = colour
            cr.set_source_rgba(r, g, b, 0.85)
            cr.rectangle(x, h - 18, 8, 8)
            cr.fill()
            cr.set_source_rgba(*C_LABEL)
            cr.move_to(x + 11, h - 10)
            cr.show_text(label)
            x += 58


# ── Fenêtre principale ────────────────────────────────────────────────────────

class NetMeterWindow(Gtk.ApplicationWindow):

    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="NetMeter")
        self.set_decorated(True)
        self.set_default_size(WIN_W, WIN_H)
        self.set_resizable(True)

        # Always-on-top via wmctrl (signal 'map' + délai 150ms pour le WM)
        self.connect('map', lambda *_: GLib.timeout_add(150, self._set_above))

        self._iface:       str | None  = None
        self._unit                     = 'KB/s'
        self._prev_bytes:  tuple | None = None
        self._prev_t:      float | None = None
        self._session_dl   = 0.0
        self._session_ul   = 0.0
        self._ifaces: list[str] = sorted(psutil.net_if_stats().keys())

        self._build_ui()
        self._load_css()
        self._register_actions()

        GLib.timeout_add(TICK_MS, self._tick)
        self._tick()

    # ── Construction UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(root)

        # ── Barre de titre ────────────────────────────────────────────────
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        hdr.set_css_classes(['nm-header'])

        self._title = Gtk.Label(label="🌐 NetMeter — All interfaces")
        self._title.set_css_classes(['nm-title'])
        self._title.set_hexpand(True)
        self._title.set_xalign(0.0)
        hdr.append(self._title)

        self._btn_mode = Gtk.Button(label="▊ Barres")
        self._btn_mode.set_css_classes(['nm-btn'])
        self._btn_mode.set_tooltip_text("Changer de vue (Lignes / Barres)")
        self._btn_mode.connect('clicked', self._toggle_mode)
        hdr.append(self._btn_mode)

        btn_close = Gtk.Button(label="×")
        btn_close.set_css_classes(['nm-close'])
        btn_close.connect('clicked', lambda _: self.get_application().quit())
        hdr.append(btn_close)

        root.append(hdr)

        # ── Graphe ────────────────────────────────────────────────────────
        self._graph = NetGraph()
        root.append(self._graph)

        # ── Ligne vitesses actuelles ───────────────────────────────────────
        speeds = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        speeds.set_css_classes(['nm-speeds'])
        speeds.set_homogeneous(True)

        self._dl_lbl = Gtk.Label(label="↓   ---")
        self._dl_lbl.set_css_classes(['nm-dl'])

        self._ul_lbl = Gtk.Label(label="↑   ---")
        self._ul_lbl.set_css_classes(['nm-ul'])

        speeds.append(self._dl_lbl)
        speeds.append(self._ul_lbl)
        root.append(speeds)

        # ── Totaux de session ─────────────────────────────────────────────
        totals = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        totals.set_css_classes(['nm-totals'])
        totals.set_homogeneous(True)

        self._tot_dl = Gtk.Label(label="Session ↓  0 B")
        self._tot_dl.set_css_classes(['nm-tot'])

        self._tot_ul = Gtk.Label(label="Session ↑  0 B")
        self._tot_ul.set_css_classes(['nm-tot'])

        totals.append(self._tot_dl)
        totals.append(self._tot_ul)
        root.append(totals)

        # Clic droit → menu contextuel
        rclick = Gtk.GestureClick()
        rclick.set_button(3)
        rclick.connect('pressed', self._on_rclick)
        self.add_controller(rclick)

    def _load_css(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            window {
                background: #0d1117;
                border: 1px solid #21262d;
                border-radius: 6px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }
            window headerbar {
                background: transparent;
                border: none;
                box-shadow: none;
                margin: 0;
                padding: 0;
                min-height: 0;
            }
            window headerbar button {
                background: transparent;
                border: none;
                box-shadow: none;
                margin: 0;
                padding: 0;
                min-width: 0;
                min-height: 0;
            }
            .nm-header {
                background: #161b22;
                padding: 3px 5px;
                border-bottom: 1px solid #21262d;
                border-radius: 6px 6px 0 0;
            }
            .nm-title { color: #8b949e; font-size: 10px; }
            .nm-btn {
                background: #21262d;
                border: 1px solid #30363d;
                box-shadow: none;
                color: #8b949e;
                font-size: 10px;
                padding: 1px 7px;
                min-height: 20px;
                border-radius: 4px;
            }
            .nm-btn:hover { background: #30363d; color: #c9d1d9; }
            .nm-close {
                background: transparent;
                border: none;
                box-shadow: none;
                color: #6e7681;
                font-size: 15px;
                padding: 0 3px;
                min-width: 22px;
                min-height: 22px;
            }
            .nm-close:hover { color: #f85149; background: transparent; }
            .nm-speeds   { padding: 4px 14px 2px; }
            .nm-dl {
                color: #3fb950;
                font-family: monospace;
                font-size: 14px;
                font-weight: bold;
            }
            .nm-ul {
                color: #f78166;
                font-family: monospace;
                font-size: 14px;
                font-weight: bold;
            }
            .nm-totals { padding: 0 14px 6px; }
            .nm-tot {
                color: #484f58;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # ── Actions Gio ───────────────────────────────────────────────────────────

    def _register_actions(self):
        app = self.get_application()

        a = Gio.SimpleAction.new('quit', None)
        a.connect('activate', lambda *_: app.quit())
        app.add_action(a)

        iface_act = Gio.SimpleAction.new_stateful(
            'iface', GLib.VariantType('s'), GLib.Variant('s', 'All'))
        def _set_iface(action, param):
            val = param.get_string()
            self._iface = None if val == 'All' else val
            self._prev_bytes = None
            action.set_state(param)
            self._update_title()
        iface_act.connect('activate', _set_iface)
        app.add_action(iface_act)

        unit_act = Gio.SimpleAction.new_stateful(
            'unit', GLib.VariantType('s'), GLib.Variant('s', 'KB/s'))
        def _set_unit(action, param):
            self._unit = param.get_string()
            self._graph._unit = param.get_string()
            action.set_state(param)
        unit_act.connect('activate', _set_unit)
        app.add_action(unit_act)

        reset_act = Gio.SimpleAction.new('reset', None)
        reset_act.connect('activate', lambda *_: self._reset_session())
        app.add_action(reset_act)

    # ── Polling réseau ────────────────────────────────────────────────────────

    def _read_bytes(self) -> tuple[float, float]:
        counters = psutil.net_io_counters(pernic=True)
        if self._iface and self._iface in counters:
            c = counters[self._iface]
            return float(c.bytes_recv), float(c.bytes_sent)
        recv = sum(c.bytes_recv for c in counters.values())
        sent = sum(c.bytes_sent for c in counters.values())
        return float(recv), float(sent)

    def _tick(self) -> bool:
        now  = time.monotonic()
        curr = self._read_bytes()

        if self._prev_bytes is not None:
            dt = now - self._prev_t
            if dt > 0:
                dl = max(0.0, (curr[0] - self._prev_bytes[0]) / dt)
                ul = max(0.0, (curr[1] - self._prev_bytes[1]) / dt)
                self._session_dl += dl * dt
                self._session_ul += ul * dt

                self._graph.push(dl, ul)
                self._dl_lbl.set_text(f"↓  {fmt_speed(dl, self._unit)}")
                self._ul_lbl.set_text(f"↑  {fmt_speed(ul, self._unit)}")
                self._tot_dl.set_text(f"Session ↓  {fmt_total(self._session_dl)}")
                self._tot_ul.set_text(f"Session ↑  {fmt_total(self._session_ul)}")

        self._prev_bytes = curr
        self._prev_t = now
        return GLib.SOURCE_CONTINUE

    # ── Contrôles fenêtre ─────────────────────────────────────────────────────

    def _set_above(self) -> bool:
        """Always-on-top via wmctrl (envoie le bon ClientMessage EWMH).
        Fallback sur xprop si wmctrl absent."""
        try:
            subprocess.Popen(
                ['wmctrl', '-r', 'NetMeter', '-b', 'add,above'],
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            try:
                xid = self.get_surface().get_xid()
                subprocess.Popen(
                    ['xprop', '-id', str(xid),
                     '-f', '_NET_WM_STATE', '32a',
                     '-set', '_NET_WM_STATE', '_NET_WM_STATE_ABOVE'],
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        except Exception:
            pass
        return False   # ne pas répéter

    def _toggle_mode(self, _btn=None):
        mode = self._graph.cycle_mode()
        self._btn_mode.set_label("〰 Lignes" if mode == 'bars' else "▊ Barres")

    def _reset_session(self):
        self._session_dl = 0.0
        self._session_ul = 0.0

    def _update_title(self):
        name = self._iface or "All interfaces"
        self._title.set_text(f"🌐 NetMeter — {name}")

    # ── Menu contextuel ───────────────────────────────────────────────────────

    def _on_rclick(self, gesture, _n, x, y):
        pop = Gtk.PopoverMenu.new_from_model(self._build_menu())
        pop.set_parent(self)
        rect = Gdk.Rectangle()
        rect.x, rect.y, rect.width, rect.height = int(x), int(y), 1, 1
        pop.set_pointing_to(rect)
        pop.popup()

    def _build_menu(self) -> Gio.Menu:
        menu = Gio.Menu()

        ifaces = Gio.Menu()
        ifaces.append("All interfaces", "app.iface::All")
        for iface in self._ifaces:
            ifaces.append(iface, f"app.iface::{iface}")
        menu.append_submenu("Interface", ifaces)

        units = Gio.Menu()
        units.append("KB/s  (auto MB/s)", "app.unit::KB/s")
        units.append("Mbit/s", "app.unit::Mbit/s")
        menu.append_submenu("Unité", units)

        menu.append("Réinitialiser session", "app.reset")
        menu.append("Quitter", "app.quit")
        return menu


# ── Application ───────────────────────────────────────────────────────────────

class NetMeterApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.tof.netmeter')

    def do_activate(self):
        NetMeterWindow(self).present()


if __name__ == '__main__':
    import sys
    sys.exit(NetMeterApp().run(sys.argv))