# Nekketsu Street Basket — Rétro-ingénierie & Traduction FR

**Français** · [English](README.en.md)

Documentation et outils de la **traduction française** de
*Nekketsu! Street Basket — Ganbare Dunk Heroes* (Famicom, 1993, Technos Japan),
ainsi que du travail de **désassemblage** mené pour y parvenir.

Le patch publié (`patch/`) transforme la ROM japonaise d'origine en version
entièrement française, en prenant la traduction anglaise de Farid (v1.2 Final,
octobre 2010) comme base de travail, puis en remplaçant tout le texte par du
français.

> ⚠️ **Aucune ROM n'est incluse dans ce dépôt** (droits d'auteur).
> Les CRC32 des ROMs de base et les fichiers IPS sont fournis ; appliquez le
> patch sur votre propre dump.

---

## État d'avancement

| Étape | Statut |
|---|---|
| Traduction FR complète (patch v1.2 Final) | ✅ Publié (16/08/2026) |
| Patch IPS JPN→FR et EN→FR | ✅ `patch/` |
| Désassemblage banques 3 & 7 | ✅ `analysis/` |
| Machine à états (dispatcher, états/sous-états) | ✅ Cartographiée |
| Routines d'input + injection clavier | ✅ Résolue (pilote PowerShell) |
| Vérification de l'écran TACTIQUES en match | 🔄 En cours |
| Rétro-ingénierie complète de la police | 🔄 À approfondir |

Objectif en cours : naviguer mode histoire → quiz → équipe → match, ouvrir le
menu **TACTIQUES** en match et vérifier les 5 tactiques
« **offensif marque frimeur automatic defensif** » (5 cases de 9 caractères).

---

## Structure du dépôt

```
├── README.md                     ← ce fichier (FR) / README.en.md (EN)
├── docs/
│   ├── 01-disassembly.md         ← structure ROM, banques, désassemblage
│   ├── 02-state-machine.md       ← machine à états ($0588/$0589, dispatcher)
│   ├── 03-input.md               ← routines d'input, injection clavier
│   ├── 04-text-pipeline.md       ← police, extraction texte, patch
│   ├── 05-emulator-notes.md      ← pièges Mesen 2.1.1 / BizHawk (API cassée)
│   ├── session-memory.md         ← mémoire de session (MAJ ~2 h, en FR)
│   └── en/                       ← versions anglaises des docs ci-dessus
├── tools/                        ← scripts réutilisables (Lua/PowerShell/Python)
│   ├── dis6502.py                ← désassembleur 6502 minimal
│   ├── make_ips.py               ← génération des patches IPS
│   ├── patch_rom.py              ← application des traductions sur la ROM
│   ├── translations.py           ← table de traductions FR (source de vérité)
│   ├── _mesen_dump.lua           ← harnais de capture Mesen (navigation + shots)
│   ├── _mt_hook.lua              ← trace machine à états (hooks WRAM)
│   ├── _tact.lua                 ← hooks état/sous-état + screenshots
│   ├── _drive2.ps1               ← pilote clavier adaptatif (focus + SendKeys)
│   ├── _focus.ps1                ← focus fenêtre Mesen (AttachThreadInput)
│   └── ...                       ← voir docs/05-emulator-notes.md pour la liste
├── analysis/
│   ├── bank3_dis.txt             ← désassemblage banque 3 (16 384 lignes)
│   └── bank7_dis.txt             ← désassemblage banque 7 (fixe, 16 384 lignes)
└── patch/
    ├── Nekketsu Street Basket (JPN) FR.ips         (19 Ko — sur ROM JAP)
    └── Nekketsu Street Basket (v1.2 Final) FR.ips  (4 Ko — sur ROM EN de Farid)
```

---

## ROMs de base requises

| Rôle | Fichier | CRC32 (fichier entier, en-tête inclus) |
|---|---|---|
| Base JAP | `Nekketsu! Street Basket - Ganbare Dunk Heroes (Japan).nes` | `A2952508` |
| Base EN | `... (v1.2 Final).nes` (Farid) | `A4680CA5` (SHA-1 `61c2ce554334266f675e878624a5bbc2e6fbfc73`) |
| Résultat FR | ROM patchée | `83B935AD` |

Taille : 262 160 octets (256 Ko, en-tête iNES de 16 octets).

---

## Ce que le travail a produit (résumé)

1. **Désassemblage** : `dis6502.py` (désassembleur 6502 minimal) appliqué aux
   banques PRG, avec sorties complètes pour les banques 3 (handlers d'écrans) et
   7 (fixe : routine d'input, dispatcher d'états, trampolines de banque).
2. **Machine à états** : `$0588` = état principal, `$0589` = sous-état.
   Dispatcher à `$CA79` (banque 7), table de handlers à `$CA8B`. Le flux
   observé : boot → quiz (état 04) → titre (état 03, attract) → menu SORT
   (état 02).
3. **Input** : routine de poll à `$F973`/`$FF80` (banque 7), bits 7=A 6=B
   5=Sel 4=Start 3=Up 2=Down 1=Left 0=Right. L'API Lua `setInput` de
   Mesen 2.1.1 étant **cassée** (no-op), l'injection se fait par le **clavier
   réel** via un pilote PowerShell (focus fenêtre + `SendKeys`).
4. **Texte** : police outline (16 px), encodage limité à a-z/0-9/espace/!?.',
   table de traductions dans `translations.py`, application par
   `patch_rom.py` (préserve les octets de contrôle et les tokens de noms),
   génération IPS par `make_ips.py`.

Voir `docs/` pour le détail.
