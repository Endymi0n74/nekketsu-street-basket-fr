# Mémoire de session

> ⏱️ **Règle : mettre à jour ce fichier toutes les ~2 h pendant les sessions de
> travail longues** (et à chaque jalon important). C'est la « mémoire » qui
> permet de reprendre une session interrompue sans repasser par les mêmes
> recherches.
>
> La copie miroir côté atelier de travail est `nes_translate/MEMO.md`.

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
