# Mémoire de session

> ⏱️ **Règle : mettre à jour ce fichier toutes les ~2 h pendant les sessions de
> travail longues** (et à chaque jalon important). C'est la « mémoire » qui
> permet de reprendre une session interrompue sans repasser par les mêmes
> recherches.
>
> La copie miroir côté atelier de travail est `nes_translate/MEMO.md`.

---

## 17/08 — outillage générique + guide de portage (dernier jalon)

- **Duo générique pour tout jeu NES** (défauts = Nekketsu, config par env) :
  - `tools/nes_state_hook.lua` — harnais Lua : hooks d'écriture WRAM par
    adresses (`HOOK_ADDRS="nom:addr[:snap]"`), screenshots périodiques + à
    chaque changement, compteur d'exécutions (`HOOK_EXEC`), `HOOK_MAX_FRAMES`.
  - `tools/nes_driver.ps1` — pilote clavier : séquences par données
    (`wait`/`tap`/`hold`/`taps`/`until`), mapping bouton→touche (`$KEYMAP`),
    env `NESDRV_LOG`/`NESDRV_DLOG`/`NESDRV_PROC`. Piège évité : `$LOG` et
    `$log` = même variable en PowerShell (insensible à la casse) → logger
    renommé `$logger`.
  - `_drive2.ps1`/`_tact.lua` restent les versions Nekketsu-spécifiques.
- **Guide de portage** : `docs/06-porting-guide.md` (FR) + `docs/en/06-porting-guide.md`
  (EN) = version canonique ; `wiki/Guide-portage.md` = miroir. Les 7 étapes :
  préparation → machine à états → texte → patcher → vérif émulateur → CI →
  publication, avec ce qui se réutilise vs à refaire.
- **Tests locaux PS1** : parser PS pour la syntaxe, dot-source (garde
  `$MyInvocation.InvocationName -ne "."`), `GetState` parse les 2 formats de
  log (ancien `STATE=XX` et nouveau `state $0588=XX`).

---

## 17/08 — wiki GitHub : BLOCQUÉ par un incident GitHub (état à l'arrêt)

- **Contexte** : l'utilisateur a créé la 1re page du wiki via le navigateur
  (« C'est fait »). Mais rien ne persiste côté GitHub :
  - `*.wiki.git` → **« Repository not found »** (clone ET push direct avec
    token, dépôt local `git init` + commit fait avant push).
  - `/wiki` → **302 vers la racine du repo** (avec et sans auth) ; la
    navigation du repo n'a **aucun onglet Wiki** (7 onglets : Code, Issues,
    Pulls, Actions, Projects, Security, Insights).
  - `/wiki/Home` et `/wiki/_new` (avec auth) → **503/504/« Unicorn »**
    (erreurs backend).
- **Cause racine identifiée : incident GitHub en cours** (githubstatus.com :
  « Partial System Outage », « Incident with GitHub.com | investigating |
  critical », ~20 % d'erreurs web/API, Webhooks/API/Issues/PRs/Actions
  dégradés). Le wiki (backend Pages/API) est incohérent à cause de ça.
- **Déjà tenté sans effet** : toggles `has_wiki` off/on (×2, avec pauses),
  push direct `.wiki.git` (avec et sans token), vérifs `/wiki`, `/wiki/Home`,
  `/wiki/_new`, `wiki.atom`, raw.githubusercontent, GraphQL `hasWikiEnabled`
  (= true mais UI non servie), page Settings (404).
- **Quand GitHub sera revenu à la normale** (vérifier githubstatus.com) :
  1. `git clone https://github.com/Endymi0n74/nekketsu-street-basket-fr.wiki.git`
  2. Si OK → copier `wiki/*.md` (7 pages) → commit → push.
  3. Si toujours « Repository not found » → redemander à l'utilisateur de
     re-créer la page web (Home) — la 1re sauvegarde web reste la seule voie
     de provisionnement si le push direct ne suffit pas.
- Le contenu n'est PAS perdu : les 7 notes FR vivent dans `wiki/` du dépôt
  principal (commit `21c58b9`), README pointe vers l'onglet wiki.

---

## 17/08 — clôture : dépôt GitHub, docs FR/EN, CI, wiki

### Dépôt GitHub
- **`Endymi0n74/nekketsu-street-basket-fr`** (public) — local
  `D:/Codex/nekketsu-street-basket-fr`. Créé et poussé ce jour.
- Structure : `README.md`/`README.en.md`, `docs/` (FR + `docs/en/`), `tools/`
  (20 scripts Lua/PowerShell/Python), `analysis/` (bank3_dis.txt, bank7_dis.txt),
  `patch/` (2 IPS), `screenshots/` (captures FR ×2), `wiki/` (notes FR),
  `.github/` (workflow + 3 scripts de check).
- **Licence MIT** (`LICENSE`, avec notes ROM/crédits) + `CONTRIBUTING.md`
  (issues/PR). Crédits : base EN de Farid (v1.2 Final), jeu © 1993 Technos Japan.

### CI (workflow `ci.yml`, badge sur les README) — TOUT VERT
1. `py_compile` tools/*.py + import `translations.py` (206 entrées)
2. `luac5.3 -p` sur tools/*.lua (7 scripts)
3. `check_ips.py` : structure des IPS (records/RLE/EOF)
4. `test_roundtrip.py` : ROMs **synthétiques** → patch_rom.py + make_ips.py →
   réapplication IPS = fr.nes octet pour octet (vérifié : JPN 141 774 o, EN
   1 225 o). ⚠️ le test câble les magic bytes de patch_rom (0xF5B7, 0x1CA08,
   0x0C00F, 0x1FE02) et une zone box35 avec overrun garanti (budgets liés aux
   longueurs actuelles de translations.py) — ajuster si patch_rom/translations changent.
5. `check_links.py` : liens internes + images des markdown.

### Galerie d'écrans & wiki
- Galerie README réalignée (FR+EN) : **Quiz | Équipe (SORT) | Match** ←
  quiz-dialogue.png / sort.png / match.png. `title.png` conservé dans
  `screenshots/` et référencé dans docs/02-state-machine.
- **Wiki GitHub activé** (`has_wiki=true`), notes FR commitées dans `wiki/`
  (Home, Desassemblage, Machine-a-etats, Input, Pipeline-texte, Notes-emulateurs).
  ⚠️ Le dépôt git du wiki (`*.wiki.git`) n'est créé par GitHub qu'à la **1re
  sauvegarde web** d'une page : ensuite `git clone` → copier `wiki/*.md` → push.

### Reste à faire (inchangé)
1. **Lancer un match** depuis le menu SORT → ouvrir **TACTIQUES** en match →
   vérifier « offensif marque frimeur automatic defensif » (B3:00F732).
2. Police : vraie table de caractères (transformation palette/ombre).
3. Nettoyer les scripts jetables de `nes_translate/`.

---

## 17/08/2026 — session désassemblage + input (état à la clôture)

### Fait
- **Patch FR v1.2 Final publié** (16/08) : `Nekketsu Street Basket (JPN) FR.ips`
  (19 Ko, sur ROM JAP `A2952508`) et `(v1.2 Final) FR.ips` (4 Ko, sur ROM EN de
  Farid `A4680CA5`). Résultat `fr.nes` = `83B935AD`.
- **Diagnostic API Mesen 2.1.1** : `setInput`, `read`, `write`, `addCheat`
  cassés (no-op / adresse ignorée). Marchent : `takeScreenshot` (octets PNG),
  memory callbacks (write), event callbacks (endFrame), exec callbacks.
- **Input résolu** : pilote clavier PowerShell = focus fenêtre
  (AttachThreadInput + SetForegroundWindow) + `SendKeys`, **dans le même
  processus**. Mapping2 : S=A, A=B, W=Start, Q=Select, flèches.
- **Machine à états cartographiée** : `$0588` état, `$0589` sous-état.
  Dispatcher `$CA79` / table `$CA8B` (banque 7) ; trampoline `$FC38` → banque 3.
  Flux : boot → quiz (04) → titre (03, attract) → menu SORT (02).
- **Menu SORT** (état 02) : sous-états 08→07→05, A = SELECT (pick de
  personnage), curseur à 3 positions. La sortie d'état (→ match) n'a **pas
  encore** été déclenchée.
- **Désassemblages** : banques 3 et 7 complets (16 384 lignes chacun) →
  `analysis/`.

### Reste à faire (priorité)
1. **Lancer un match** depuis le menu SORT (mode histoire → quiz → équipe →
   match) et ouvrir le menu **TACTIQUES** en match.
2. Vérifier l'affichage « **offensif marque frimeur automatic defensif** »
   (5 cases de 9 caractères) — patché à `B3:00F732`.
3. Police : extraire la vraie table de caractères (écart glyphes affichés vs
   CHR ROM — transformation palette/ombre à élucider).
4. Nettoyer les scripts jetables de `nes_translate/` (les `_api*`, `_in_test*`,
   `_probe*`, `_exec_probe`…) ; garder ceux copiés dans `tools/` de ce repo.

### Détails techniques à ne pas reperdre
- Quiz : ~8 000 frames sans input sur Mesen ; taps A toutes les ~2 s → fini à
  f2206. Ne jamais attendre la fin du quiz passivement.
- `emu.read` cassé → pas de navigation auto-adaptative en Lua ; le driver
  PowerShell lit le log Lua et branche selon l'écran.
- Le « log lines: 0 » du driver était transitoire → retries (5×) dans
  `_drive2.ps1`.
- Éviter le non-ASCII dans les `.ps1` (erreur de parsing PowerShell ligne 114).
- BizHawk (fr3/fr4, joypad.set) a déjà atteint match + MEMBERS : garder ces
  captures comme référence du flux d'écrans.
