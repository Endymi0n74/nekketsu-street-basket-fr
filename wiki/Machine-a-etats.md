# 02 — Machine à états

*Voir aussi [`docs/02-state-machine.md`](https://github.com/Endymi0n74/nekketsu-street-basket-fr/blob/main/docs/02-state-machine.md).*

## Variables

- `$0588` : état principal (écrit à chaque changement d'écran).
- `$0589` : sous-état (sous-machine de l'écran courant).
- Les écritures sont hookables via
  `emu.addMemoryCallback(..., emu.callbackType.write, addr, addr, emu.memType.InternalRam)`
  (voir `tools/_tact.lua`, `tools/_mt_hook.lua`).

## Dispatcher

Banque 7, `$CA79` : `LDA $0588` → indexe une table à `$CA8B` → `JMP (handler)`.
Les handlers sont des **stubs de commutation de banque** : ex. l'état 2
(menu/SORT) pointe `$CAB0` → stub `$FC38` → bascule → vrai handler à `$8000`
en **banque 3**. Les sous-états du menu passent par une table à `$802A`.

## Flux observé

```
boot ──► état 04 (quiz Downtown) ──► état 03 (titre, attract)
        état 03 ── sous-états 0x80-0x84 ──► état 00 (attract) ──► 03...
        [Start/A au titre] ──► état 02 (menu SORT — triage d'équipe)
```

- Le **quiz** (état 04) dure ~8 000 frames (~133 s) sans input sur Mesen ;
  des taps A répétés le font avancer beaucoup plus vite (fini à f2206).
- Le **titre** (état 03) boucle en attract (sous-états 80-84).
- Le **menu SORT** (état 02) : sous-états 08 → 07 → 05, curseur à 3 positions ;
  A déclenche le SELECT (88 → 07) et enregistre un pick de personnage. La
  sortie d'état (→ match) n'a pas encore été déclenchée.

## Handlers localisés (banque 3)

| Adresse | Sous-état | Rôle |
|---|---|---|
| `$81C6` | 0 | Entrée du menu (dessin) |
| `$87B2` | 4 | Dessin des 4 personnages du SORT |
| `$88CE` | 5 | Phase curseur (`AND #$03` / `AND #$90`) |
| `$89C5` / `$8A80` | 7 | Sélection (chemin actif `$8B38`) |
| `$8BA2` | 8 | Handler actif pendant le menu (~1×/frame) |

## Piège d'analyse

Le désassemblage linéaire dérive dans les tables de données : les adresses
ci-dessus ont été confirmées par **hooks exec** et par l'observation des
écritures `$0588/$0589`, pas par le désassemblage brut seul.
