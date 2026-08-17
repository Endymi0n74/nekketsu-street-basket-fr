# 01 — Structure du ROM et désassemblage

*Voir aussi le fichier [`docs/01-disassembly.md`](https://github.com/Endymi0n74/nekketsu-street-basket-fr/blob/main/docs/01-disassembly.md) du dépôt.*

## Vue d'ensemble

- **Jeu** : Nekketsu! Street Basket — Ganbare Dunk Heroes (Famicom, 1993,
  Technos Japan). Licence : « Nekketsu Street Basket ».
- **ROM** : 262 160 octets = en-tête iNES (16 o) + 256 Ko de PRG.
- Le travail de désassemblage a porté sur les **8 premières banques de 16 Ko**
  (`data[16:16+8*16384]` dans `patch_rom.py`), la banque 7 étant fixe.

## Banques

| Banque | Offset ROM | Espace CPU | Rôle observé |
|---|---|---|---|
| 0-2 | 0x00000-0x0BFFF | $8000-$BFFF (commutable) | — |
| 3 | 0x0C000-0x0FFFF | $8000-$BFFF | Handlers d'écrans (menu, SORT, titre, quiz…) |
| 4 | 0x10000-0x13FFF | $8000-$BFFF | Dialogues (Downtown Quiz, avion, crédits) |
| 5-6 | 0x14000-0x1BFFF | $8000-$BFFF | — |
| 7 | 0x1C000-0x1FFFF | $C000-$FFFF (fixe) | Input, dispatcher d'états, trampolines |

Adresses CPU : `base + (off % 0x4000)` avec `base = 0x8000` (ou 0xC000 pour la
banque fixe).

## Outil

`tools/dis6502.py` : désassembleur 6502 minimal (table d'opcodes complète).
Les désassemblages complets des banques 3 et 7 (16 384 lignes chacun) sont
dans [`analysis/`](https://github.com/Endymi0n74/nekketsu-street-basket-fr/tree/main/analysis).

⚠️ Le désassemblage **linéaire** dérive dans les zones de données (tables de
pointeurs, texte) : les régions utiles ont été re-désassemblées en suivant les
branches (voir [[Machine-a-etats]] et [[Input]]).

## Routines clés localisées (banque 7)

| Adresse | Rôle |
|---|---|
| `$F8D0-$F9A0` | Bloc input |
| `$F973` | Lecture brute `$4016/$4017` → `$04/$05` |
| `$F8EA` | Détection d'edge → `$04/$05` = appuis du frame |
| `$FF80` | Copie `$06/$07` → `$00/$01` (état maintenu) |
| `$FF98` | Fin de poll (hook exec utile, ~1×/frame) |
| `$CA79` | Dispatcher d'états (LDA `$0588` → table `$CA8B`) |
| `$FC38` | Trampoline : bascule de banque vers le vrai handler |

## WRAM utilisée par la machine à états

| Adresse | Rôle |
|---|---|
| `$0588` | État principal |
| `$0589` | Sous-état |
| `$058D` | Flags (bit 1 → routine de lecture input) |
| `$00/$01` | État maintenu P1 lu par la logique |
| `$04/$05` | Appuis du frame P1/P2 (edge) |
| `$06/$07` | État maintenu P1/P2 |
