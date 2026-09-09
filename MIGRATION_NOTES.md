# Applying this to your real repo & server

## 1. Merging the code changes
This zip is the reorganized version of your repo (built from your `main`
branch). Easiest way to apply it:
- Copy these files over your local clone (or diff them file-by-file), then
  `git add -A`, review `git status`/`git diff`, commit, and push as normal.
- All the moves below are tracked-file moves, so once you push, a normal
  `git pull` on your server rearranges them automatically.

## 2. One-time step on your server (do this once, right after `git pull`)
Your gitignored data files (`feedback.json`, `notifications.json`, etc.)
are **not tracked by git**, so pulling this code will NOT move your real,
live data — it'll just sit in the old root-level location while the code
now looks in `data/`. Run the included script once, before restarting the
app:

```bash
git pull
bash migrate_to_new_layout.sh
# then restart your container / service
```

It's safe to re-run and won't overwrite anything. `site.db` doesn't need
to move — it stays in the project root.

## 3. What changed, at a glance
- `templates/` split into `pages/`, `auth/`, `admin/`, `blog/`, `games/`,
  `guestbook/`, `home/`, `forum/` (forum was already organized).
- `static/style.css` -> `static/css/style.css`, `static/index.js` -> `static/js/index.js`.
- All JSON data files now live in `data/` (`achievement_list.json` etc. are
  still git-tracked there; the gitignored ones are listed in `.gitignore`
  with a `data/` prefix now).
- Added `helpers.py: data_path() / load_json() / save_json()` so file
  locations are defined in one place instead of as scattered string
  literals across every route file.
- Fixed ~20 spots where a missing data file (normal on a fresh clone)
  would 500 the whole page — they now fall back to sensible empty defaults.
- Fixed the Alembic migration chain so `flask db upgrade`-equivalent setup
  works from a totally empty database (previously required manually
  running `db.create_all()` first). This now happens automatically on
  first boot if no tables exist yet; it's a no-op on your existing server.
- `debug=True` is no longer hardcoded — set `FLASK_DEBUG=1` in your `.env`
  if you want it locally; leave it unset in production.
- Removed dead/junk files: unused `templates/profile.html`, empty
  `routes/main.py`, stray `.DS_Store`/`._*` AppleDouble files, and
  `uandp.json.save` (0 bytes).

## 4. Things I flagged but deliberately did NOT change
- `static/IMG_0294.png` (13MB) doesn't seem to be referenced anywhere in
  the templates/CSS/JS — worth checking if you still need it, since it's
  a big chunk of your repo's 37MB+ size.
- `migrate_uandp_to_db.py` and `migrations.py` (root-level) look like
  one-off scripts from your JSON-to-database migration, which your commit
  history says is done. Consider deleting them or moving them to an
  `archive/` folder if you don't need them anymore.
- `templates/pages/error.html` isn't wired to any `@app.errorhandler` or
  route — it currently never renders. Worth hooking up or removing.
