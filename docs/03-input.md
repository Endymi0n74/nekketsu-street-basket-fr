# 03 — Routines d'input et injection

## Routines (banque 7)

Le jeu poll la manette **chaque frame** :

```asm
$F973: lecture brute $4016/$4017 → accumulation dans $04/$05 (P1/P2)
$F8EA: détection d'edge
       $04/$05 = appuis du frame courant
       $06/$07 = état maintenu
$FF80: selon $058D bit 1 → $F949 ou $F911 (lectures adaptées),
       puis copie $06/$07 → $00/$01 (ce que la logique du jeu lit)
$FF98: fin du poll (hook exec utile : s'exécute ~1×/frame)
```

### Mapping des bits

| Bit | Bouton |
|---|---|
| 7 | A |
| 6 | B |
| 5 | Select |
| 4 | Start |
| 3 | Up |
| 2 | Down |
| 1 | Left |
| 0 | Right |

La logique des écrans lit l'input dans `$04+Y` avec des masques :
ex. menu SORT : `AND #$03` (Left/Right = déplacer le curseur),
`AND #$90` (A/Start = sélectionner).

## Injection : le problème

Sur **Mesen 2.1.1 Desktop** (build Windows), l'API Lua d'input/mémoire est
cassée :

- `emu.setInput({...}, 1)` → **no-op** (vérifié : `getInput` ne voit rien).
- `emu.read(debug, memType, addr)` → ignore l'adresse (retourne le 1er octet du
  domaine).
- `emu.write(...)` → no-op silencieux (aucun callback déclenché).
- `emu.addCheat(...)` → signature inattendue (erreur).

Ni les hooks d'écriture, ni les exec callbacks ne peuvent donc injecter
d'input, et `emu.read` interdit la navigation auto-adaptative depuis Lua.

## Solution retenue : pilote clavier PowerShell

Le chemin **input manager → $4016** est indépendant de l'API Lua : les touches
réelles du clavier atteignent le jeu. Deux contraintes découvertes :

1. **Mapping clavier actif = Mapping2** (défaut Mesen 2.1.1) :

   | Bouton NES | Touche |
   |---|---|
   | A | **S** |
   | B | **A** |
   | Start | **W** |
   | Select | **Q** |
   | D-pad | flèches |
   | Turbo A / B | X / Z |

2. **Le focus fenêtre est indispensable** : `AllowBackgroundInput` seul ne
   suffit pas ; et chaque `powershell.exe` séparé ouvre une console qui vole le
   focus. La solution qui marche : **focus + envoi des touches dans le même
   processus** PowerShell :

   - `AttachThreadInput` + `ShowWindow` + `BringWindowToTop` +
     `SetForegroundWindow` (voir `tools/_focus.ps1`),
   - puis `[System.Windows.Forms.SendKeys]::SendWait("s")` (touche = S).

Résultat vérifié : un tap S pendant le poll produit `$04 = 0x80` (A) dans les
hooks — l'input atteint bien la logique du jeu.

## Pilotes fournis

| Fichier | Rôle |
|---|---|
| `tools/_focus.ps1` | Focus de la fenêtre Mesen (méthode AttachThreadInput + repli clic) |
| `tools/_sendkey.ps1` | Envoi d'une touche |
| `tools/_drive_test.ps1` | Démo : focus + tap S → vérifier `$04` |
| `tools/_drive2.ps1` | Pilote adaptatif : lit le log Lua, presse selon l'écran (retries) |

## Séquences de navigation connues

- **BizHawk (runs fr3/fr4, joypad API)** : titre → Start → A → A → A×4 →
  match → Select ; `fr4` montre l'écran MEMBERS (sélection d'équipe) après 14 A.
- **Mesen (pilote clavier)** : taps A pendant le quiz → titre → tap A → menu
  SORT (état 02). L'ouverture d'un match est en cours de mise au point.

> Astuce : ne pas attendre la fin du quiz (~8 000 frames). Des taps A répétés
> toutes les ~2 s le font avancer (fini à f2206 dans un run).
