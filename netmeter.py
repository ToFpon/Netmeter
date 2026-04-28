def fmt_speed(speed, unit="B/s"):
    """
    Format speed with appropriate unit
    Arguments:
    speed -- speed value
    unit -- unit of speed (default is B/s)
    """
    if unit == "B/s":
        return f"{speed} {unit}"
    elif unit == "KiB/s":
        return f"{speed / 1024:.2f} {unit}"
    elif unit == "MiB/s":
        return f"{speed / (1024 ** 2):.2f} {unit}"
    elif unit == "GiB/s":
        return f"{speed / (1024 ** 3):.2f} {unit}"
    else:
        return f"{speed} {unit}"

MENU_OPTIONS = {
    "EN": {
        "option_1": "Speed Test",
        "option_2": "Settings",
    },
    "FR": {
        "option_1": "Test de Vitesse",
        "option_2": "Paramètres",
    },
    "DE": {
        "option_1": "Geschwindigkeitstest",
        "option_2": "Einstellungen",
    }
}

# Example usage:
print(fmt_speed(2048, "KiB/s"))  # Expected output: '2.00 KiB/s'

# for translations
for lang, options in MENU_OPTIONS.items():
    print(f'{lang} Menu: {options}')