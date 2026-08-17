# 02 — Machine à états

## Variables

- `$0588` : état principal (écrit à chaque changement d'écran).
- `$0589` : sous-état (sous-machine de l'écran courant).
- Les écritures sont hookables via `emu.addMemoryCallback(..., emu.callbackType.write,
  addr, addr, emu.memType.InternalRam)` (voir `tools/_tact.lua`, `tools/_mt_hook.lua`).

## Dispatcher

Banque 7, `$CA79` :

```asm
CA79: LDA $0588          ; état courant
      ...                ; indexe une table à $CA8B
      JMP (handler)      ; saute au handler de l'état
```

La table `$CA8B` contient les adresses des handlers, qui sont en réalité des
**stubs de commutation de banque** : ex. l'état 2 (menu/SORT) pointe sur
`$CAB0` → stub `$FC38` → bascule de banque → vrai handler à `$8000` en
**banque 3**.

Les sous-états du menu sont dispatchés via une table à `$802A` (banque 3).

## Flux observé (via hooks WRAM + screenshots)

```
boot ──► état 04 (quiz Downtown) ──► état 03 (titre, attract)
        état 03 ── cycle sous-états 0x80-0x84 ──► état 00 (attract) ──► 03...
        [Start/A au titre] ──► état 02 (menu SORT — triage d'équipe)
```

- Le **quiz** (état 04) dure ~8 000 frames (~133 s) sans input sur Mesen ;
  des taps A le font avancer beaucoup plus vite (fini à f2206 dans un run).
- Le **titre** (état 03) boucle en attract : sous-états 80-84, retours vers
  état 00.
- Le **menu SORT** (état 02) : sous-états en cycle 08 → 07 → 05. C'est un
  curseur à 3 positions ; un appui **A** déclenche le SELECT
  (sous-état 88 → 07) et enregistre un choix de personnage (2 picks puis
  retour au menu) — la sortie d'état n'a pas encore été déclenchée.

## Handlers localisés (banque 3)

| Adresse | Sous-état | Rôle |
|---|---|---|
| `$81C6` | 0 | Entrée du menu (dessin) |
| `$87B2` | 4 | Dessin des 4 personnages du SORT |
| `$88CE` | 5 | Phase curseur (lit `$04` avec `AND #$03` / `AND #$90`) |
| `$89C5` / `$8A80` | 7 | Sélection (chemin actif `$8B38`) |
| `$8BA2` | 8 | Handler actif pendant le menu (~1×/frame) ; lecture input `$8C11` |

## Piège d'analyse

Le désassemblage **linéaire** dérive dans les tables de données : les adresses
ci-dessus ont été confirmées par **hooks exec** (le handler sub-8 `$8BA2`
s'exécute ~1×/frame pendant le menu) et par l'observation des écritures
`$0588/$0589`, pas par le désassemblage brut seul.
