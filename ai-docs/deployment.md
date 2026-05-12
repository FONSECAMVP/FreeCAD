# AI Addon v0.1.0 — Deployment Steps (DEC-011: Addon Manager package)

Pre-deploy gate: CLV validation-004 PASS. Manual soak checklist in cycle-a4.md must complete first.

---

## Step 1 — Complete manual soak (A4.1)

Run the checklist in `cycles/cycle-a4.md § A4.1` against a real FreeCAD instance with
a live LLM endpoint. Confirm all 6 items before proceeding.

---

## Step 2 — Create external GitHub repo

```bash
# On GitHub: create new repo named FreeCAD-AI-Addon (public)
# Then locally:
mkdir ~/FreeCAD-AI-Addon
cp -r src/Mod/AIAddon/. ~/FreeCAD-AI-Addon/
cd ~/FreeCAD-AI-Addon

# Edit package.xml — replace [user] with your GitHub username
sed -i 's/\[user\]/YOUR_GITHUB_USERNAME/g' package.xml

git init
git add .
git commit -m "feat: FreeCAD AI Addon v0.1.0 initial release"
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/FreeCAD-AI-Addon.git
git push -u origin main
```

---

## Step 3 — Tag v0.1.0 release

```bash
cd ~/FreeCAD-AI-Addon
git tag -a v0.1.0 -m "FreeCAD AI Addon v0.1.0

LLM-driven FreeCAD tool execution via natural language chat panel.
142 tests, 72% coverage. Supports Part, PartDesign, Sketcher, Draft, BIM.
Requires OpenAI-compatible API key (openai>=1.30, keyring>=24).
"
git push origin v0.1.0
```

Create a GitHub Release from the tag with:
- Title: `v0.1.0 — AI Addon for FreeCAD`
- Body: copy from PRD Goals + success metrics + install instructions

---

## Step 4 — Install instructions for end users

Users install via FreeCAD Tools → Addon Manager → search "AI Addon", or manually:

```bash
# Manual install (until Addon Manager index submission is approved):
cd ~/.local/share/FreeCAD/Mod/   # Linux
# or ~/Library/Application Support/FreeCAD/Mod/  on macOS
# or %APPDATA%\FreeCAD\Mod\  on Windows

git clone https://github.com/YOUR_GITHUB_USERNAME/FreeCAD-AI-Addon AIAddon
pip install openai keyring

# Then restart FreeCAD
```

---

## Step 5 — Submit to FreeCAD Addon index (optional, when ready)

```bash
# Fork https://github.com/FreeCAD/FreeCAD-addons
# Add entry to addons.json with your repo URL and package.xml path
# Open PR to FreeCAD-addons repo
```

---

## Step 6 — Post-deploy monitoring

Monitor for 2 weeks per PRD success metrics. Fill in `cycles/cycle-a5.md` after window.

Watch for:
- GitHub Issues on the external repo
- FreeCAD forum thread (create one under "Python scripting and Macros")
- keyring errors on unusual OS configurations
- PySide6 compatibility issues (FreeCAD 1.0+ moved from PySide2)

---

## Rollback

User-facing: uninstall via Addon Manager, or `rm -rf ~/.local/share/FreeCAD/Mod/AIAddon/`.
Git-based (dev): `git checkout main && git clean -fdx src/Mod/AIAddon/` (< 1s, A4.2).
