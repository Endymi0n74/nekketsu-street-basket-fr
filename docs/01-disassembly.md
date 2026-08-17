# 01 — Structure du ROM et désassemblage

[English](en/01-disassembly.md)

## Vue d'ensemble

- **Jeu** : Nekketsu! Street Basket — Ganbare Dunk Heroes (Famicom, 1993,
  Technos Japan). Licence : « Nekketsu Street Basket ».
- **ROM** : 262 160 octets = en-tête iNES (16 o) + 256 Ko de PRG.
- **Cartouche** : pas de CHR ROM dans ce fichier (128 Ko PRG + 128 Ko PRG ? —
  à clarifier ; le CHR est lu via la banque 7 / données graphiques).

> À préciser : la partition exacte PRG/CHR du fichier. Le travail de
> désassemblage a porté sur les **8 premières banques de 16 Ko** (`data[16:16+8*16384]`
> dans `patch_rom.py`), la banque 7 étant fixe (`$C000-$FFFF` CPU).

## Banques

| Banque | Offset ROM | Espace CPU | Rôle observé |
|---|---|---|---|
| 0-2 | 0x00000-0x0BFFF | $8000-$BFFF (commutable) | — |
| 3 | 0x0C000-0x0FFFF | $8000-$BFFF | Handlers d'écrans (menu, SORT, titre, quiz…) |
| 4 | 0x10000-0x13FFF | $8000-$BFFF | Dialogues (Downtown Quiz, avion, crédits), texte |
| 5-6 | 0x14000-0x1BFFF | $8000-$BFFF | — |
| 7 | 0x1C000-0x1FFFF | $C000-$FFFF (fixe) | Routines système : input, dispatcher d'états, trampolines de banque |

Les adresses CPU dans le désassemblage sont `base + (off % 0x4000)` avec
`base = 0x8000` (ou 0xC000 pour la banque fixe).

## Outil

`tools/dis6502.py` : désassembleur 6502 minimal (table d'opcodes complète,
modes d'adressage, `disasm_line(prg, off, base, cpu)`).

Utilisation typique :

```python
import sys; sys.path.insert(0, "tools")
from dis6502 import disasm_line
prg = open("fr.nes", "rb").read()[16:16+8*16384]
for off in range(0x1C000, 0x1C100):  # banque 7
    addr, size, text = disasm_line(prg, off)
    print(f"{addr:04X}: {text}")
```

⚠️ Le désassemblage **linéaire** (1 instruction par octet) dérive dans les
zones de données (tables de pointeurs, texte). Les sorties `analysis/*.txt`
sont donc brutes : les régions utiles ont été re-désassemblées en suivant les
branches (voir `docs/02-state-machine.md` et `docs/03-input.md`).

## Routines clés localisées (banque 7)

| Adresse | Rôle |
|---|---|
| `$F8D0-$F9A0` | Bloc input (voir 03-input.md) |
| `$F973` | Lecture brute `$4016/$4017` → `$04/$05` |
| `$F8EA` | Détection d'edge → `$04/$05` = appuis du frame |
| `$FF80` | Copie `$06/$07` → `$00/$01` (état maintenu pour la logique) |
| `$FF98` | Fin de poll (hook exec utile : tourne ~1×/frame) |
| `$CA79` | Dispatcher d'états (LDA `$0588` → table `$CA8B`) |
| `$FC38` | Trampoline : bascule de banque vers le vrai handler d'état |

## Adresses WRAM utilisées par la machine à états

| Adresse | Rôle |
|---|---|
| `$0588` | État principal |
| `$0589` | Sous-état |
| `$058D` | Flags (bit 1 → choix de la routine de lecture input) |
| `$00/$01` | État maintenu P1 lu par la logique |
| `$04/$05` | Appuis du frame P1/P2 (edge) |
| `$06/$07` | État maintenu P1/P2 |
