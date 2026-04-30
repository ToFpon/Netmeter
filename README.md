# 🌐 NetMeter

> A real-time network bandwidth monitor for Linux / GTK4,  
> inspired by the legendary [NetMeter](http://www.hootech.com/NetMeter/) by Hootech.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![GTK](https://img.shields.io/badge/GTK-4.0-green?logo=gnome)
![License](https://img.shields.io/badge/License-GPLv3-orange)
![Languages](https://img.shields.io/badge/i18n-EN%20%7C%20FR%20%7C%20DE-lightgrey)

---

## ✨ Features

- **Scrolling graph** — 120-second history
- **Two views**, switchable with one click:
  - `〰 Lines` — filled curves, oscilloscope style
  - `▊ Bars` — DL/UL side-by-side bars with highlight
- **Auto-scaling Y axis** — adapts to current peak, with dotted grid lines
- **Real-time speeds** — KB/s (auto-upgrades to MB/s), Mbit/s or B/s
- **Session counters** — total DL/UL since launch, resettable
- **Interface selector** — all interfaces or one specific (right-click)
- **Always-on-top** — stays visible above your other windows (survives mini mode toggle)
- **Resizable window** with native WM decoration
- **Mini mode** — compact windowless widget, draggable anywhere on screen:
  - `Mini: text` — speeds only (~2×1 cm)
  - `Mini: graph` — full-width graph without axis, lines or bars
- **3 languages** — English 🇬🇧 / Français 🇫🇷 / Deutsch 🇩🇪 (auto-detected, switchable)

---

## 📦 Dependencies

### Required

| Package | Role | Install |
|---------|------|---------|
| `python3` ≥ 3.10 | Interpreter | already there 😄 |
| `python3-gi` | GObject/GTK4 bindings | `sudo apt install python3-gi` |
| `python3-gi-cairo` | Cairo rendering | `sudo apt install python3-gi-cairo` |
| `gir1.2-gtk-4.0` | GTK 4 library | `sudo apt install gir1.2-gtk-4.0` |
| `python3-psutil` | Network counter reading | `sudo apt install python3-psutil` |

### Recommended

| Package | Role | Install |
|---------|------|---------|
| `wmctrl` | Reliable always-on-top (EWMH) | `sudo apt install wmctrl` |
| `x11-utils` | Fallback always-on-top (`xprop`) | `sudo apt install x11-utils` |

> **Note:** `wmctrl` is strongly recommended. Without it, the `xprop` fallback
> is attempted but may not work depending on your window manager.

### One-liner

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-psutil wmctrl
```

---

## 🚀 Installation

### Quick method (provided script)

```bash
chmod +x install.sh
./install.sh
```

The script installs missing dependencies, copies `netmeter.py` to `~/.local/bin/`,
and creates a `.desktop` launcher in `~/.local/share/applications/`.

### Manual method

```bash
cp netmeter.py ~/.local/bin/netmeter
chmod +x ~/.local/bin/netmeter
netmeter
```

---

## 🖱️ Usage

| Action | Effect |
|--------|--------|
| **`▊ Bars` / `〰 Lines` button** | Switch between graph views |
| **Right-click** on the window | Open context menu |
| Menu → **Interface** | Select a network interface |
| Menu → **Unit** | B/s, KB/s (auto MB/s) or Mbit/s |
| Menu → **Language** | Switch UI language (EN / FR / DE) |
| Menu → **Reset session** | Reset DL/UL session counters |
| Menu → **Mini mode** | Enter compact windowless mode |
| Menu → **Mini: graph / Mini: text** | Switch mini sub-mode (in mini mode only) |
| Menu → **Normal mode** | Return to full window (in mini mode) |
| **Left-click drag** | Move window (mini mode, no decoration) |
| Menu → **Quit** | Exit the application |

---

## 🔧 Quick configuration

Constants at the top of the file:

```python
HISTORY      = 120     # Graph history duration (seconds)
TICK_MS      = 1000    # Refresh interval (ms)
WIN_W, WIN_H = 690, 345  # Default window size (px)
MINI_W       = 260     # Mini mode width (px)
MINI_H_GRAPH = 50      # Mini graph height (px)
LM           = 110     # Left margin for Y labels (px)
```

Colours (R, G, B between 0 and 1):

```python
C_DL = (0.25, 0.73, 0.31)   # Green  — Download
C_UL = (0.97, 0.50, 0.40)   # Red    — Upload
```

---

## 🐧 Compatibility

| Environment | Status |
|-------------|--------|
| Zorin OS 17/18 (GNOME, X11) | ✅ Tested |
| Ubuntu 22.04 / 24.04 (GNOME, X11) | ✅ Compatible |
| Wayland | ⚠️ Not tested — drag and always-on-top may differ |
| GTK < 4.0 | ❌ Not supported |

---

## 📄 License

GPLv3 — see [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

---
---

# 🌐 NetMeter *(Français)*

> Un moniteur de bande passante réseau en temps réel pour Linux / GTK4,  
> inspiré du légendaire [NetMeter](http://www.hootech.com/NetMeter/) de Hootech.

---

## ✨ Fonctionnalités

- **Graphe défilant** — 120 secondes d'historique
- **Deux vues** basculables en un clic :
  - `〰 Lignes` — courbes remplies façon oscilloscope
  - `▊ Barres` — barres DL/UL côte à côte avec reflets
- **Graduation Y automatique** — s'adapte au pic courant, grille pointillée
- **Vitesses en temps réel** — B/s, KB/s (auto MB/s) ou Mbit/s
- **Compteurs de session** — total DL/UL depuis le lancement, réinitialisables
- **Sélecteur d'interface** — toutes ou une seule (clic droit)
- **Always-on-top** — reste visible au-dessus des autres fenêtres (survit au mini mode)
- **Fenêtre redimensionnable** avec décoration native du WM
- **Mode mini** — widget compact sans décoration, déplaçable n'importe où :
  - `Mini : texte` — vitesses uniquement (~2×1 cm)
  - `Mini : graphe` — graphe pleine largeur sans axe, lignes ou barres
- **3 langues** — English 🇬🇧 / Français 🇫🇷 / Deutsch 🇩🇪 (détection auto, changeable)

---

## 📦 Dépendances

### Obligatoires

| Paquet | Rôle | Installation |
|--------|------|--------------|
| `python3` ≥ 3.10 | Interpréteur | déjà là 😄 |
| `python3-gi` | Bindings GObject/GTK4 | `sudo apt install python3-gi` |
| `python3-gi-cairo` | Rendu Cairo | `sudo apt install python3-gi-cairo` |
| `gir1.2-gtk-4.0` | Bibliothèque GTK 4 | `sudo apt install gir1.2-gtk-4.0` |
| `python3-psutil` | Lecture des compteurs réseau | `sudo apt install python3-psutil` |

### Recommandées

| Paquet | Rôle | Installation |
|--------|------|--------------|
| `wmctrl` | Always-on-top fiable (EWMH) | `sudo apt install wmctrl` |
| `x11-utils` | Fallback always-on-top (`xprop`) | `sudo apt install x11-utils` |

### En une ligne

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-psutil wmctrl
```

---

## 🚀 Installation

```bash
chmod +x install.sh && ./install.sh
```

Le script installe les dépendances manquantes, copie `netmeter.py` dans `~/.local/bin/`
et crée un lanceur `.desktop` dans `~/.local/share/applications/`.

---

## 🖱️ Utilisation

| Action | Effet |
|--------|-------|
| **Bouton `▊ Barres` / `〰 Lignes`** | Bascule entre les deux vues |
| **Clic droit** sur la fenêtre | Ouvre le menu contextuel |
| Menu → **Interface** | Sélectionne une interface réseau |
| Menu → **Unité** | B/s, KB/s (auto MB/s) ou Mbit/s |
| Menu → **Langue** | Change la langue (EN / FR / DE) |
| Menu → **Réinitialiser session** | Remet les compteurs à zéro |
| Menu → **Mode mini** | Passe en widget compact sans décoration |
| Menu → **Mini : graphe / Mini : texte** | Bascule le sous-mode mini (en mode mini uniquement) |
| Menu → **Mode normal** | Retour à la fenêtre complète |
| **Glisser clic gauche** | Déplace la fenêtre (mode mini, sans décoration) |
| Menu → **Quitter** | Ferme l'application |

---

## 📄 Licence

GPLv3 — voir [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

---

*Inspiré de NetMeter par Hootech (Windows) — réincarné en Python/GTK4 pour Linux.*
