# Contributing

Thanks for taking an interest in this project! This repository documents the
reverse-engineering and French translation of *Nekketsu! Street Basket —
Ganbare Dunk Heroes* (Famicom). All contributions that help the community —
better documentation, sharper tooling, deeper analysis — are welcome.

## Ways to contribute

- **Report issues**: broken links in the docs, inaccurate addresses in the
  disassembly notes, a tool that fails on your setup.
- **Ask questions**: open an issue if something in the docs is unclear.
- **Pull requests**: docs improvements, new analysis, tool fixes, translations
  (English/French).

## Before opening an issue

1. Read the README (`README.md` / `README.en.md`) and the status table.
2. Check `docs/` and `docs/en/` — the answer may already be there.
3. Search existing issues for a duplicate.

## Pull request workflow

1. Fork the repository and create a branch (`git checkout -b topic/...`).
2. Make focused changes — one topic per PR.
3. For tools:

   - Python: keep them dependency-light (stdlib preferred); Python 3 only.
   - Lua (Mesen 2.1.1): read `docs/05-emulator-notes.md` first — several
     APIs (`emu.read`, `emu.write`, `emu.setInput`) are **broken** on that
     build. Test with the GUI-mode harness described there.
   - PowerShell: **avoid non-ASCII characters** in `.ps1` files (encoding
     breaks the parser); keep focus/key-sending inside the same process.
4. Commit with a concise, descriptive message.
5. Open the PR against `main`.

## Testing

- **Text/IPS tooling** (`tools/make_ips.py`, `tools/patch_rom.py`): the
  patches must reproduce `fr.nes` (CRC32 `83B935AD`) from the base ROMs
  (CRC32 `A2952508` JAP / `A4680CA5` EN). If your change alters output,
  state the new CRC32 in the PR.
- **Emulator scripts**: run against the harness described in
  `docs/05-emulator-notes.md` (Mesen 2.1.1 GUI mode) and paste the relevant
  log excerpt.

## What is NOT accepted

- ROM dumps or reproductions of copyrighted game content (no `.nes` files,
  ever — see `LICENSE`).
- Changes that remove translator credits (see CREDITS in the README).

## Code of conduct

Be respectful. This is a hobby project made by people sharing their free time;
disagreements should stay technical and constructive.
