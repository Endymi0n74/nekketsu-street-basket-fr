# Comment traduire un autre jeu NES — guide de portage

Ce guide explique comment réutiliser l'outillage du dépôt pour traduire un
**autre jeu NES**. Il suit la méthode utilisée pour Nekketsu Street Basket,
étape par étape, en précisant ce qui se réutilise tel quel et ce qui doit être
refait à chaque jeu.

## Ce que tu réutilises tel quel

- `tools/dis6502.py` — désassembleur 6502 (n'importe quelle ROM 6502).
- `tools/make_ips.py` — génération IPS avec auto-vérification (universel).
- `tools/nes_state_hook.lua` — harnais Mesen générique (adresses par env).
- `tools/_focus.ps1`, `tools/_drive2.ps1`, `tools/_sendkey.ps1` — pilotes
  clavier PowerShell (n'importe quel émulateur sur Windows).
- `tools/_ascii_preview.py`, `tools/_read_text.py` — analyse de screenshots.
- `.github/` — workflow CI + `check_ips.py` + `check_links.py`.
- Le savoir émulateur : API Mesen 2.1.1 cassée / BizHawk → voir
  [[Notes-emulateurs]].

## Ce que tu refais à chaque jeu

- Les **adresses** (état, input, dispatcher, trampolines).
- La **carte du texte** : blocs, octets de contrôle, tokens de noms, police.
- `translations.py` (le contenu) et les constantes de `patch_rom.py`
  (BLOCKS, LETTER, NAME_PATTERNS, EN/OUT).
- Les magic bytes du test round-trip CI.

---

## Étape 1 — Préparer l'environnement

1. Clone le dépôt : `git clone https://github.com/Endymi0n74/nekketsu-street-basket-fr`.
2. Copie `tools/` et `.github/` dans ton projet.
3. Prépare ta ROM de base (dump du jeu original) et Mesen 2.1.1 (mode GUI).
4. Lance le harnais générique pour vérifier qu'il tourne (défauts = Nekketsu ;
   change les adresses dès que tu les connais) :

```bash
HOOK_OUTDIR=D:/tmp ./Mesen.exe ta_rom.nes tools/nes_state_hook.lua --enableStdout
```

## Étape 2 — Cartographier la machine à états (le plus long)

1. **Trouve la routine de lecture manette.** Désassemble la banque fixe avec
   `dis6502.py` et cherche le pattern classique : écriture `$4016` suivie de
   8 lectures shiftées (le protocole NES est universel, seules les adresses de
   stockage changent). Pour Nekketsu : `$F973` (lecture brute) →
   `$04/$05` (appuis du frame) → `$06/$07` (état maintenu) → `$00/$01`.
2. **Confirme le poll avec le harnais** : `HOOK_EXEC=<fin de la routine>` →
   le compteur doit approcher ~60/frame.
3. **Trouve l'adresse d'état.** Hooke les écritures WRAM sur les adresses
   où le code stocke l'état ; quand tu vois un octet qui change uniquement aux
   transitions d'écran, c'est l'état (`$0588` chez Nekketsu). Le sous-état
   (`$0589`) change souvent juste après.
4. **Localise le dispatcher** : `LDA état` → indexation d'une table → `JMP`.
   Chez Nekketsu : `$CA79` / table `$CA8B`. Les handlers sont souvent des
   **trampolines de banque** (ex. `$FC38`) qui basculent vers une autre banque.
5. **Dessine le flux** : boot → écrans → menus, avec les captures du harnais
   (`HOOK_ADDRS="state:0x0588:snap,sub:0x0589"`) et `_ascii_preview.py` pour
   identifier chaque écran sans ouvrir d'image.

> Astuce Nekketsu : le quiz dure ~8 000 frames sans input — ne jamais attendre
> passivement, envoyer des taps A toutes les ~2 s via le pilote clavier.

## Étape 3 — Trouver et extraire le texte

1. **Scanner les banques** pour repérer les zones de texte. L'atelier contient
   des scripts d'exploration one-shot à adapter : `scan_ascii_text.py`
   (textes ASCII), `find_text.py` (plages de tuiles-lettres), `find_font.py` /
   `find_chtab.py` (localisation de la police dans les banques CHR),
   `find_ptr_tables.py` (tables de pointeurs), `diff_roms.py` (comparer deux
   ROMs pour voir ce qu'un patch modifie).
2. **Identifie l'encodage** : la police NES limite souvent le jeu de
   caractères (`a-z`, `0-9`, espace, `!?.'` chez Nekketsu). Note les limites —
   le texte FR doit s'y adapter.
3. **Structure le texte** : repère les octets de contrôle (fins de ligne, fins
   de boîte), les tokens de noms (petits motifs comme `D7 D8 1F` = [KUNIO]) et
   les budgets d'octets par morceau de lettres.
4. **Crée `translations.py`** pour ton jeu : clés `(banque:offset, ligne)`,
   valeurs = listes de chaînes FR par morceau de lettres, dans l'ordre.

## Étape 4 — Adapter le patcher

1. Dans `patch_rom.py` : change `EN`/`OUT`, `LETTER` (jeu de caractères),
   `NAME_PATTERNS` (tokens de noms), `BLOCKS` (les zones de texte patchées).
2. Traite les cas spéciaux comme chez Nekketsu :
   - **Menus à cases alignées** (9 commandes, pointeurs) → réécrire chaînes +
     pointeurs explicitement (`patch_command_menu`).
   - **Boîtes de dialogue dépassant le budget** → réécrire la boîte avec des
     lignes rééquilibrées (`patch_quiz_box`, `patch_box9`…).
   - **Tables DTE** (compression de noms) → ajuster les paires (`HOST:` →
     `HOTE:`).
3. Génère les IPS : `make_ips.py` (vérifie lui-même la réapplication).

## Étape 5 — Vérifier en émulateur

1. Lance la ROM patchée avec le harnais + le pilote clavier générique
   (`tools/nes_driver.ps1`, séquences configurables par données).
2. Compare les screenshots FR vs base (découpe, `_ascii_preview.py`).
3. Vérifie les écrans critiques : menus, dialogues, écran de fin.

## Étape 6 — Mettre en place la CI

1. Copie `.github/workflows/ci.yml` + `.github/scripts/`.
2. Adapte `test_roundtrip.py` : les **magic bytes** (octets que ton
   `patch_rom.py` vérifie avec des asserts) et la zone box spéciale (dépassement
   garanti). Le principe — ROMs synthétiques, aucun contenu copyrighté — reste
   identique.

## Étape 7 — Publier

- `make_ips.py` → deux IPS (sur ROM JAP et/ou EN de base).
- README avec les CRC32 des ROMs requises et du résultat (ne jamais inclure
  les ROMs elles-mêmes).
- Licence + crédits (voir `LICENSE` et `CONTRIBUTING.md` du dépôt).

---

## Temps estimé (retour d'expérience Nekketsu)

| Phase | Difficulté |
|---|---|
| Cartographie de la machine à états | ⭐⭐⭐ la plus longue (injection d'input comprise) |
| Extraction du texte / police | ⭐⭐ |
| Adaptation du patcher | ⭐⭐ |
| Vérification + CI | ⭐ |

L'outillage déjà prêt évite de repartir de zéro : l'essentiel du travail restant
est la **lecture du jeu** (adresses + texte), pas l'écriture des outils.
