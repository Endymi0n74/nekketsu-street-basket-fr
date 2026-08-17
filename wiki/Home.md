# Nekketsu Street Basket — Wiki

Bienvenue sur le wiki du projet **Nekketsu! Street Basket — Ganbare Dunk Heroes**
(Famicom, 1993, Technos Japan) : rétro-ingénierie et traduction française.

> Dépôt principal : [Endymi0n74/nekketsu-street-basket-fr](https://github.com/Endymi0n74/nekketsu-street-basket-fr)
> — code, outils, désassemblages complets et patches IPS.

## Notes de rétro-ingénierie (en français)

- [[Desassemblage]] — structure du ROM, banques, désassemblage 6502
- [[Machine-a-etats]] — machine à états (`$0588`/`$0589`), dispatcher, flux d'écrans
- [[Input]] — routines d'input, injection clavier (pilote PowerShell)
- [[Pipeline-texte]] — police, extraction du texte, application du patch
- [[Notes-emulateurs]] — pièges Mesen 2.1.1 / BizHawk et API qui marchent
- [[Guide-portage]] — comment traduire un autre jeu NES avec cet outillage

## État d'avancement

| Étape | Statut |
|---|---|
| Traduction FR (patch v1.2 Final) | ✅ Publié (16/08/2026) |
| Patches IPS JPN→FR et EN→FR | ✅ `patch/` |
| Désassemblage banques 3 & 7 | ✅ `analysis/` |
| Machine à états | ✅ Cartographiée |
| Injection clavier (Mesen) | ✅ Résolue |
| Vérification écran TACTIQUES en match | 🔄 En cours |
| Rétro-ingénierie complète de la police | 🔄 À approfondir |

## ROMs de base requises

| Rôle | CRC32 (fichier entier) |
|---|---|
| Base JAP | `A2952508` |
| Base EN (Farid v1.2 Final) | `A4680CA5` (SHA-1 `61c2ce554334266f675e878624a5bbc2e6fbfc73`) |
| Résultat FR | `83B935AD` |

Aucune ROM n'est incluse dans le dépôt — appliquez les IPS de `patch/` sur
votre propre dump.
