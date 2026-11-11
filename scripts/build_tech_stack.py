"""Rewrite the Tech Stack section of README.md with detected tools.

Usage: python build_tech_stack.py <merged.json> <tools.txt> <README.md>
- merged.json: unused (kept for call compatibility)
- tools.txt: one detected tool key per line (one entry per repo it was
  found in; duplicates rank a tool higher)
The section between TECH:START and TECH:END markers is replaced.
"""
import sys
from collections import Counter

START, END = "<!-- TECH:START -->", "<!-- TECH:END -->"
MAX_TOOLS = 12

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


def main() -> None:
    counts = Counter(
        line.strip()
        for line in open(sys.argv[2], encoding="utf-8-sig")
        if line.strip() in TOOL_BADGES
    )
    tools = [key for key, _ in counts.most_common(MAX_TOOLS)]

    lines_md = ["<div align=\"center\">", ""]
    tool_md = [
        badge(*TOOL_BADGES[k], alt=TOOL_BADGES[k][0].replace("_", " ").replace("--", "-"))
        for k in tools
    ]
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
