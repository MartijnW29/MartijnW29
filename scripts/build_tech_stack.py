"""Rewrite the Tech Stack section of README.md from real data.

Usage: python build_tech_stack.py <cloc-merged.json> <tools.txt> <README.md>
- cloc-merged.json: language -> lines of code (workflow aggregation)
- tools.txt: one detected tool key per line (one entry per repo it was
  found in; duplicates rank a tool higher)
The section between TECH:START and TECH:END markers is replaced.
"""
import json
import sys
from collections import Counter

START, END = "<!-- TECH:START -->", "<!-- TECH:END -->"
MIN_PCT = 1.0
MAX_TOOLS = 12

# cloc language name -> (badge label, color, simpleicons logo, logo color)
LANG_BADGES = {
    "Python": ("Python", "3776AB", "python", "white"),
    "JavaScript": ("JavaScript", "F7DF1E", "javascript", "black"),
    "TypeScript": ("TypeScript", "3178C6", "typescript", "white"),
    "C#": ("C%23", "512BD4", "dotnet", "white"),
    "HTML": ("HTML5", "E34F26", "html5", "white"),
    "CSS": ("CSS", "663399", "css", "white"),
    "SCSS": ("SCSS", "C6538C", "sass", "white"),
    "Vue": ("Vue.js", "41B883", "vuedotjs", "white"),
    "Bourne Shell": ("Shell", "4EAA25", "gnubash", "white"),
    "Bourne Again Shell": ("Shell", "4EAA25", "gnubash", "white"),
    "PowerShell": ("PowerShell", "012456", "powershell", "white"),
    "GDScript": ("GDScript", "478CBF", "godotengine", "white"),
    "Java": ("Java", "B07219", "openjdk", "white"),
    "C++": ("C++", "F34B7D", "cplusplus", "white"),
    "C": ("C", "555555", "c", "white"),
    "PHP": ("PHP", "4F5D95", "php", "white"),
    "Go": ("Go", "00ADD8", "go", "white"),
    "Rust": ("Rust", "DEA584", "rust", "black"),
    "Lua": ("Lua", "000080", "lua", "white"),
    "SQL": ("SQL", "E38C00", "mysql", "white"),
}
MERGE = {"Bourne Again Shell": "Bourne Shell"}
# tokei JSON uses enum variant names; normalize them first
TOKEI_NAMES = {
    "CSharp": "C#",
    "Html": "HTML",
    "Css": "CSS",
    "Scss": "SCSS",
    "Sh": "Bourne Shell",
    "Bash": "Bourne Shell",
    "GdScript": "GDScript",
    "Sql": "SQL",
    "Cpp": "C++",
    "Php": "PHP",
    "Tsx": "TypeScript",
}

TOOL_BADGES = {
    "dotnet": (".NET", "512BD4", "dotnet", "white"),
    "maui": (".NET_MAUI", "512BD4", "dotnet", "white"),
    "godot": ("Godot", "478CBF", "godotengine", "white"),
    "nodejs": ("Node.js", "5FA04E", "nodedotjs", "white"),
    "docker": ("Docker", "2496ED", "docker", "white"),
    "actions": ("GitHub_Actions", "2088FF", "githubactions", "white"),
    "django": ("Django", "092E20", "django", "white"),
    "flask": ("Flask", "3BABC3", "flask", "white"),
    "torch": ("PyTorch", "EE4C2C", "pytorch", "white"),
    "opencv": ("OpenCV", "5C3EE8", "opencv", "white"),
    "pandas": ("Pandas", "150458", "pandas", "white"),
    "numpy": ("NumPy", "013243", "numpy", "white"),
    "streamlit": ("Streamlit", "FF4B4B", "streamlit", "white"),
    "selenium": ("Selenium", "43B02A", "selenium", "white"),
    "scikit-learn": ("scikit--learn", "F7931E", "scikitlearn", "white"),
    "discord": ("Discord_bots", "5865F2", "discord", "white"),
    "react": ("React", "61DAFB", "react", "black"),
    "express": ("Express", "000000", "express", "white"),
    "electron": ("Electron", "47848F", "electron", "white"),
    "unity": ("Unity", "000000", "unity", "white"),
}
ALWAYS_TOOLS = ["git"]
EXTRA_BADGES = {"git": ("Git", "F05032", "git", "white")}


def badge(label: str, color: str, logo: str, logo_color: str, alt: str) -> str:
    return (
        f"![{alt}](https://img.shields.io/badge/{label}-{color}"
        f"?style=for-the-badge&logo={logo}&logoColor={logo_color})"
    )


def lang_badge(lang: str, pct: float) -> str:
    label, color, logo, logo_color = LANG_BADGES[lang]
    return (
        f"![{lang} {pct:.0f}%](https://img.shields.io/badge/{label}-{pct:.0f}%25"
        f"-{color}?style=for-the-badge&logo={logo}&logoColor={logo_color}"
        f"&labelColor=2d333b)"
    )


def main() -> None:
    raw = json.loads(open(sys.argv[1], encoding="utf-8-sig").read())
    langs: dict[str, int] = {}
    for lang, lines in raw.items():
        lang = TOKEI_NAMES.get(lang, lang)
        lang = MERGE.get(lang, lang)
        if lang in LANG_BADGES and lines > 0:
            langs[lang] = langs.get(lang, 0) + lines
    total = sum(langs.values()) or 1
    ranked = [
        (lang, 100 * n / total)
        for lang, n in sorted(langs.items(), key=lambda kv: kv[1], reverse=True)
        if 100 * n / total >= MIN_PCT
    ]

    counts = Counter(
        line.strip()
        for line in open(sys.argv[2], encoding="utf-8-sig")
        if line.strip() in TOOL_BADGES
    )
    tools = [key for key, _ in counts.most_common(MAX_TOOLS)]

    lines_md = ["<div align=\"center\">", ""]
    lines_md.append("\n".join(lang_badge(lang, pct) for lang, pct in ranked))
    lines_md.append("")
    tool_md = [badge(*TOOL_BADGES[k], alt=TOOL_BADGES[k][0].replace("_", " ")) for k in tools]
    tool_md += [badge(*EXTRA_BADGES[k], alt=EXTRA_BADGES[k][0]) for k in ALWAYS_TOOLS]
    lines_md.append("\n".join(tool_md))
    lines_md += ["", "</div>"]
    section = "\n".join(lines_md)

    readme_path = sys.argv[3]
    readme = open(readme_path, encoding="utf-8").read()
    pre, _, rest = readme.partition(START)
    _, _, post = rest.partition(END)
    if not pre or not post:
        sys.exit("TECH markers not found in README")
    with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{pre}{START}\n{section}\n{END}{post}")


if __name__ == "__main__":
    main()
