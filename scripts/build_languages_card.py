"""Render profile/languages.svg from aggregated cloc output.

Usage: python build_languages_card.py <cloc-merged.json> <output.svg>
The input is a JSON object mapping language name -> lines of code,
as produced by the workflow's cloc aggregation step.
"""
import json
import sys

# GitHub linguist colors for languages we care about; anything not
# listed here (JSON, Markdown, YAML, ...) is treated as data, not code.
LANGUAGES = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "C#": "#178600",
    "HTML": "#e34c26",
    "CSS": "#663399",
    "SCSS": "#c6538c",
    "Vue": "#41b883",
    "JSX": "#f1e05a",
    "Bourne Shell": "#89e051",
    "Bourne Again Shell": "#89e051",
    "PowerShell": "#012456",
    "GDScript": "#355570",
    "Razor": "#512be4",
    "SQL": "#e38c00",
    "Java": "#b07219",
    "C": "#555555",
    "C++": "#f34b7d",
    "C/C++ Header": "#555555",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Kotlin": "#A97BFF",
    "Swift": "#F05138",
    "Dockerfile": "#384d54",
    "Lua": "#000080",
}
DISPLAY_NAMES = {
    "Bourne Shell": "Shell",
    "Bourne Again Shell": "Shell",
    "C/C++ Header": "C",
    "JSX": "JavaScript",
}
LIMIT = 8

# github_dark_dimmed palette, matching the other cards
BG, TITLE, TEXT, MUTED = "#22272e", "#539bf5", "#adbac7", "#768390"


def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def main() -> None:
    raw = json.loads(open(sys.argv[1], encoding="utf-8").read())

    merged: dict[str, int] = {}
    colors: dict[str, str] = {}
    for lang, lines in raw.items():
        if lang not in LANGUAGES or lines <= 0:
            continue
        name = DISPLAY_NAMES.get(lang, lang)
        merged[name] = merged.get(name, 0) + lines
        colors[name] = LANGUAGES[lang]

    ranked = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)[:LIMIT]
    total = sum(n for _, n in ranked)
    if not total:
        sys.exit("no code lines found")

    bar_w, bar_x = 420, 30
    col_w, row_h, top = 210, 22, 110
    rows = (len(ranked) + 1) // 2
    height = top + rows * row_h + 18

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" '
        f'viewBox="0 0 480 {height}" role="img" aria-label="Lines of code per language">',
        f'<rect width="480" height="{height}" rx="4.5" fill="{BG}"/>',
        f'<text x="30" y="37" font-family="Segoe UI,Ubuntu,sans-serif" '
        f'font-size="18" font-weight="600" fill="{TITLE}">Lines of Code per Language</text>',
        f'<text x="30" y="60" font-family="Segoe UI,Ubuntu,sans-serif" '
        f'font-size="12" fill="{MUTED}">{fmt(total)} lines across all repositories '
        f'(private included)</text>',
        f'<mask id="bar"><rect x="{bar_x}" y="74" width="{bar_w}" height="10" rx="5" fill="#fff"/></mask>',
    ]

    x = float(bar_x)
    for name, lines in ranked:
        w = bar_w * lines / total
        parts.append(
            f'<rect mask="url(#bar)" x="{x:.1f}" y="74" width="{w + 1:.1f}" '
            f'height="10" fill="{colors[name]}"/>'
        )
        x += w

    for i, (name, lines) in enumerate(ranked):
        cx = 30 + (i % 2) * col_w
        cy = top + (i // 2) * row_h
        pct = 100 * lines / total
        parts.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{colors[name]}"/>')
        parts.append(
            f'<text x="{cx + 18}" y="{cy}" font-family="Segoe UI,Ubuntu,sans-serif" '
            f'font-size="12" fill="{TEXT}">{name.replace("&", "&amp;")} '
            f'<tspan fill="{MUTED}">{fmt(lines)} lines · {pct:.1f}%</tspan></text>'
        )

    parts.append("</svg>")
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


if __name__ == "__main__":
    main()
