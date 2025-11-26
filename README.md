# Save-Share

Save-Share is a game-save sharing client for H700-based emulation handhelds  
(e.g. Anbernic RG35XX/RG34XX running KNULLI/Batocera-style firmware).

It scans your ROM and save folders, matches games using EmulationStation
`gamelist.xml` files, and connects to a Supabase backend so you can:

- Upload your own saves and savestates with tags like **Boss Fight**, **100%**, **All Items**, etc.
- Browse saves other people have uploaded.
- Download them directly into your handheld’s save folders.

Think of it as a lightweight “Save Game Workshop” for tiny Linux handhelds.

---

## Status

🚧 **Early prototype** – expect bugs and rough edges.  
The goal right now is:

- Solid ROM + save detection
- End-to-end upload / browse / download flow with Supabase
- Running as a Python CLI on the device (a graphical UI can come later)

Contributions, ideas, and issues are very welcome.

---

## Features

- 🔎 **Automatic library scan**  
  Reads every `gamelist.xml` under your ROM folders to discover games.

- 🧬 **Cross-device game matching**  
  Hashes ROMs (MD5) so saves can be shared reliably across different devices and installs.

- 💾 **Save & savestate detection**  
  Scans per-system save folders, grouping normal saves vs savestates and keeping track of slots.

- ☁️ **Supabase-backed sharing**  
  Uploads metadata (system, game, core, tags, description, nickname) and the save file to Supabase Storage + tables.

- 🎯 **Only shows games you actually own**  
  When browsing, you’ll only see shared saves for games that exist in your local library (matched by system + ROM hash).

- 📴 **Offline-friendly**  
  Local scanning and indexing still work with no network connection; online actions fail gracefully.

---

## How it works (high level)

1. Save-Share scans your ROMs folder (e.g. `/userdata/roms`) and parses each
   `gamelist.xml` to figure out:
   - The system (NES, SNES, PSX, etc.)
   - Game title
   - ROM filename and location

2. It hashes each ROM file and stores a local index:  
   `system + rom_hash + rom_name`.

3. It scans per-system save folders (e.g. `/userdata/saves/<system>`) and pairs
   files like `.sav`, `.srm`, `.state`, `.state1`, etc. to ROMs by name.

4. When you upload a save or savestate, it sends:
   - The local metadata (system, rom hash/name, save type, core)
   - Tags and a human-readable description
   - The binary save file to Supabase Storage

5. When you browse, it sends a list of your `(system, rom_hash)` pairs to Supabase
   and gets back just the saves that match games you have installed.

---

## Repository layout

```text
src/save_share/          # Python client modules
supabase/schema.sql      # Database tables and view
supabase/policies.sql    # Row Level Security policies
requirements.txt         # Python dependencies
config.example.json      # Example client configuration
