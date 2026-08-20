# NES Translation — Rétro-ingénierie & outillage de traduction

[![CI](https://github.com/Endymi0n74/nes-translation/actions/workflows/ci.yml/badge.svg)](https://github.com/Endymi0n74/nes-translation/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
[![Langue](https://img.shields.io/badge/langue-Fran%C3%A7ais-blue)](README.md)
[![EN](https://img.shields.io/badge/langue-English-lightgrey)](README.en.md)

📚 [Docs](docs/) · 🛠️ [Outils](tools/) · 📦 [Patches](patch/) · ⚖️ [Licence](LICENSE) · 🤝 [Contribuer](CONTRIBUTING.md)

Kit d'outils **générique** pour la rétro-ingénierie et la traduction de jeux
**NES** : désassembleur 6502, génération de patches IPS, harnais d'émulateur
(Mesen 2.1.1 / BizHawk), pilote d'injection clavier, et un guide de portage
pour appliquer la méthode à n'importe quel jeu.

**Cas d'étude complet :** la **traduction française** de
*Nekketsu! Street Basket — Ganbare Dunk Heroes* (Famicom, 1993, Technos Japan),
menée de bout en bout avec ce kit — du désassemblage jusqu'au patch IPS publié.

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
| Outillage générique (désassemblage, IPS, hooks, pilote clavier) | ✅ Réutilisable |
| Guide de portage vers un autre jeu NES | ✅ `docs/06-porting-guide.md` |
| Traduction FR de Nekketsu Street Basket (patch v1.2) | ✅ Publié (16/08/2026) |
| Patch IPS JPN→FR et EN→FR | ✅ `patch/` |
| Désassemblage banques 3 & 7 | ✅ `analysis/` |
| Machine à états (dispatcher, états/sous-états) | ✅ Cartographiée |
| Routines d'input + injection clavier | ✅ Résolue (pilote PowerShell) |
| Vérification de l'écran TACTIQUES en match | 🔄 En cours |

Objectif en cours : naviguer mode histoire → quiz → équipe → match, ouvrir le
menu **TACTIQUES** en match et vérifier les 5 tactiques
« **offensif marque frimeur automatic defensif** » (5 cases de 9 caractères).

---

## Captures d'écran

Le flux mode histoire → équipe → match, sur le patch FR appliqué :

| Quiz (dialogue) | Équipe (SORT) | Match (VS) |
|---|---|---|
| <img src="screenshots/quiz-dialogue.png" width="220"> | <img src="screenshots/sort.png" width="220"> | <img src="screenshots/match.png" width="220"> |

> L'écran **TACTIQUES** en match (5 cases : « offensif marque frimeur
> automatic defensif ») sera ajouté ici une fois la navigation terminée.

---

## Structure du dépôt

```
├── README.md                     ← ce fichier (FR) / README.en.md (EN)
├── CONTRIBUTING.md               ← guide de contribution (issues/PR)
├── LICENSE                       ← MIT
├── docs/
│   ├── 01-disassembly.md         ← structure ROM, banques, désassemblage
│   ├── 02-state-machine.md       ← machine à états ($0588/$0589, dispatcher)
│   ├── 03-input.md               ← routines d'input, injection clavier
│   ├── 04-text-pipeline.md       ← police, extraction texte, patch
│   ├── 05-emulator-notes.md      ← pièges Mesen 2.1.1 / BizHawk (API cassée)
│   ├── 06-porting-guide.md       ← comment traduire un autre jeu NES
│   ├── session-memory.md         ← mémoire de session (MAJ ~2 h, en FR)
│   └── en/                       ← versions anglaises des docs ci-dessus
├── tools/                        ← scripts réutilisables (Lua/PowerShell/Python)
│   ├── dis6502.py                ← désassembleur 6502 minimal
│   ├── make_ips.py               ← génération des patches IPS
│   ├── patch_rom.py              ← application des traductions sur la ROM
│   ├── translations.py           ← table de traductions FR (source de vérité)
│   ├── nes_state_hook.lua        ← harnais Mesen générique (hooks par adresses)
│   ├── nes_driver.ps1            ← pilote clavier générique (séquences par données)
│   ├── _mesen_dump.lua           ← harnais de capture Mesen (navigation + shots)
│   ├── _mt_hook.lua              ← trace machine à états (hooks WRAM)
│   ├── _tact.lua                 ← hooks état/sous-état + screenshots
│   ├── _drive2.ps1               ← pilote clavier adaptatif (focus + SendKeys)
│   ├── _focus.ps1                ← focus fenêtre Mesen (AttachThreadInput)
│   └── ...                       ← voir docs/05-emulator-notes.md pour la liste
├── analysis/
│   ├── bank3_dis.txt             ← désassemblage banque 3 (16 384 lignes)
│   └── bank7_dis.txt             ← désassemblage banque 7 (fixe, 16 384 lignes)
├── screenshots/                  ← captures FR (titre, quiz, SORT, match)
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

---

## Licence & crédits

- Code, outils et documentation : [MIT](LICENSE). **Aucune ROM incluse** —
  appliquez le patch sur votre propre dump du jeu original (CRC32 dans la
  section ROMs de base).
- **Traduction française** : libre d'utilisation et de redistribution avec
  mention des traducteurs. Elle s'appuie sur la traduction anglaise
  **v1.2 Final de Farid** (octobre 2010) comme base.
- Jeu original : *Nekketsu! Street Basket — Ganbare Dunk Heroes* © 1993
  Technos Japan.
- Contributions bienvenues — voir [CONTRIBUTING](CONTRIBUTING.md).
