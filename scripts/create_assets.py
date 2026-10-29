import os

def create_svg_assets():
    target_dir = os.path.join("secureshop", "static", "img")
    os.makedirs(target_dir, exist_ok=True)

    icons = {
        "yubikey.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="25" y="15" width="50" height="70" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="4"/>
            <rect x="35" y="10" width="30" height="15" rx="3" fill="#06b6d4"/>
            <circle cx="50" cy="55" r="14" fill="#6366f1" fill-opacity="0.3" stroke="#6366f1" stroke-width="3"/>
            <path d="M44 55h12M50 49v12" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
            <circle cx="50" cy="76" r="4" fill="#10b981"/>
        </svg>""",
        
        "wallet.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="20" y="25" width="60" height="50" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="4"/>
            <rect x="28" y="32" width="44" height="20" rx="3" fill="#1e293b" stroke="#334155" stroke-width="2"/>
            <circle cx="50" cy="62" r="5" fill="#10b981"/>
            <circle cx="65" cy="62" r="4" fill="#64748b"/>
            <path d="M35 42h30" stroke="#10b981" stroke-width="2" stroke-linecap="round"/>
        </svg>""",

        "privacy_screen.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="15" y="20" width="70" height="50" rx="4" fill="#090d16" stroke="#6366f1" stroke-width="4"/>
            <path d="M15 35h70M15 50h70M15 65h70" stroke="#334155" stroke-width="2"/>
            <path d="M30 70l-8 15h56l-8-15" fill="#1e293b" stroke="#6366f1" stroke-width="3"/>
            <circle cx="50" cy="45" r="10" fill="#f43f5e" fill-opacity="0.3" stroke="#f43f5e" stroke-width="2"/>
            <path d="M45 40l10 10M55 40l-10 10" stroke="#f43f5e" stroke-width="2" stroke-linecap="round"/>
        </svg>""",

        "faraday.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <path d="M25 20h50l-5 65H30z" fill="#1e293b" stroke="#f59e0b" stroke-width="4"/>
            <path d="M30 35h40M32 50h36M34 65h32" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4 4"/>
            <circle cx="50" cy="50" r="12" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
            <path d="M44 50h12" stroke="#ffffff" stroke-width="3"/>
        </svg>""",

        "keyboard.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="15" y="30" width="70" height="42" rx="6" fill="#0f172a" stroke="#06b6d4" stroke-width="4"/>
            <rect x="22" y="37" width="8" height="6" rx="1" fill="#6366f1"/>
            <rect x="34" y="37" width="8" height="6" rx="1" fill="#6366f1"/>
            <rect x="46" y="37" width="8" height="6" rx="1" fill="#6366f1"/>
            <rect x="58" y="37" width="8" height="6" rx="1" fill="#6366f1"/>
            <rect x="70" y="37" width="8" height="6" rx="1" fill="#6366f1"/>
            <rect x="22" y="47" width="8" height="6" rx="1" fill="#38bdf8"/>
            <rect x="34" y="47" width="8" height="6" rx="1" fill="#38bdf8"/>
            <rect x="46" y="47" width="8" height="6" rx="1" fill="#38bdf8"/>
            <rect x="58" y="47" width="8" height="6" rx="1" fill="#38bdf8"/>
            <rect x="70" y="47" width="8" height="6" rx="1" fill="#38bdf8"/>
            <rect x="30" y="57" width="40" height="7" rx="2" fill="#06b6d4"/>
        </svg>""",

        "headphones.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <path d="M25 55v-10a25 25 0 0 1 50 0v10" stroke="#a855f7" stroke-width="5" stroke-linecap="round"/>
            <rect x="18" y="50" width="14" height="26" rx="7" fill="#1e293b" stroke="#a855f7" stroke-width="3"/>
            <rect x="68" y="50" width="14" height="26" rx="7" fill="#1e293b" stroke="#a855f7" stroke-width="3"/>
            <circle cx="50" cy="30" r="4" fill="#a855f7"/>
        </svg>""",

        "book.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <path d="M20 20h30v60H20z" fill="#1e293b" stroke="#ef4444" stroke-width="3"/>
            <path d="M50 20h30v60H50z" fill="#0f172a" stroke="#ef4444" stroke-width="3"/>
            <path d="M28 35h14M28 45h14M28 55h10" stroke="#fca5a5" stroke-width="2"/>
            <path d="M58 35h14M58 45h14M58 55h10" stroke="#fca5a5" stroke-width="2"/>
            <circle cx="50" cy="50" r="16" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
            <path d="M46 50l3 3 6-6" stroke="#10b981" stroke-width="2" stroke-linecap="round"/>
        </svg>""",

        "datablocker.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="30" y="35" width="40" height="30" rx="4" fill="#1e293b" stroke="#10b981" stroke-width="4"/>
            <rect x="42" y="22" width="16" height="13" rx="2" fill="#64748b"/>
            <rect x="42" y="65" width="16" height="13" rx="2" fill="#64748b"/>
            <path d="M40 50h20" stroke="#f43f5e" stroke-width="3" stroke-linecap="round"/>
            <path d="M50 40l-5 10h10l-5 10" fill="#f59e0b"/>
        </svg>""",

        "mouse.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="32" y="20" width="36" height="60" rx="18" fill="#1e293b" stroke="#06b6d4" stroke-width="4"/>
            <path d="M50 20v22" stroke="#06b6d4" stroke-width="3"/>
            <rect x="46" y="28" width="8" height="14" rx="4" fill="#6366f1"/>
        </svg>""",

        "monitor.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="12" y="20" width="76" height="46" rx="4" fill="#0a0f1d" stroke="#6366f1" stroke-width="4"/>
            <path d="M40 66l-5 18h30l-5-18" fill="#1e293b" stroke="#6366f1" stroke-width="3"/>
            <circle cx="50" cy="43" r="10" fill="#06b6d4" fill-opacity="0.2" stroke="#06b6d4" stroke-width="2"/>
            <path d="M22 32h15M22 40h20" stroke="#475569" stroke-width="2" stroke-linecap="round"/>
        </svg>""",

        "token.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <circle cx="50" cy="50" r="35" fill="#1e293b" stroke="#f43f5e" stroke-width="4"/>
            <circle cx="50" cy="50" r="22" stroke="#f43f5e" stroke-width="2" stroke-dasharray="4 4"/>
            <path d="M50 35v18l10 5" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        </svg>""",

        "product-default.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
            <rect x="20" y="20" width="60" height="60" rx="8" fill="#1e293b" stroke="#64748b" stroke-width="4"/>
            <path d="M35 50h30M50 35v30" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>
        </svg>"""
    }

    for fname, content in icons.items():
        path = os.path.join(target_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
    print("Vector SVG assets generated successfully.")

if __name__ == "__main__":
    create_svg_assets()
