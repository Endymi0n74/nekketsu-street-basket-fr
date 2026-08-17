# 03 — Routines d'input et injection

*Voir aussi [`docs/03-input.md`](https://github.com/Endymi0n74/nekketsu-street-basket-fr/blob/main/docs/03-input.md).*

## Routines (banque 7)

Le jeu poll la manette **chaque frame** :

```asm
$F973: lecture brute $4016/$4017 → accumulation dans $04/$05 (P1/P2)
$F8EA: détection d'edge
       $04/$05 = appuis du frame courant
       $06/$07 = état maintenu
$FF80: selon $058D bit 1 → $F949 ou $F911,
       puis copie $06/$07 → $00/$01 (ce que la logique lit)
$FF98: fin de poll (hook exec utile : ~1×/frame)
```

### Mapping des bits

| Bit | Bouton | | Bit | Bouton |
|---|---|---|---|---|
| 7 | A | | 3 | Up |
| 6 | B | | 2 | Down |
| 5 | Select | | 1 | Left |
| 4 | Start | | 0 | Right |

La logique des écrans lit l'input dans `$04+Y` avec des masques
(ex. SORT : `AND #$03` = curseur, `AND #$90` = A/Start).

## Le problème : API Lua Mesen cassée

Sur **Mesen 2.1.1 Desktop**, `emu.setInput`, `emu.read`, `emu.write` et
`emu.addCheat` sont des no-ops (vérifié). Ni les hooks ni les callbacks
d'écriture ne peuvent injecter d'input.

## Solution : pilote clavier PowerShell

Le chemin input manager → `$4016` est indépendant de l'API Lua. Contraintes
découvertes :

1. **Mapping2** (défaut Mesen 2.1.1) : A=**S**, B=**A**, Start=**W**,
   Select=**Q**, D-pad = flèches, Turbo A/B = X/Z.
2. **Focus fenêtre indispensable** : `AllowBackgroundInput` seul ne suffit
   pas, et chaque `powershell.exe` séparé vole le focus. Solution qui marche :
   **focus + touches dans le même processus** (`AttachThreadInput` +
   `SetForegroundWindow` + `SendKeys`).

Vérifié : un tap S pendant le poll produit `$04 = 0x80` (A) dans les hooks.

## Pilotes fournis

| Fichier | Rôle |
|---|---|
| `tools/_focus.ps1` | Focus de la fenêtre Mesen |
| `tools/_sendkey.ps1` | Envoi d'une touche |
| `tools/_drive_test.ps1` | Démo : focus + tap S |
| `tools/_drive2.ps1` | Pilote adaptatif (lit le log Lua, retries) |

## Séquences connues

- **BizHawk (joypad API)** : titre → Start → A → A → A×4 → match → Select ;
  écran MEMBERS après 14 A.
- **Mesen (clavier)** : taps A pendant le quiz → titre → A → menu SORT.

> Ne pas attendre la fin du quiz (~8 000 frames) : taps A toutes les ~2 s.
