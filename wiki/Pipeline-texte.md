# 04 — Pipeline texte, police et patch

*Voir aussi [`docs/04-text-pipeline.md`](https://github.com/Endymi0n74/nekketsu-street-basket-fr/blob/main/docs/04-text-pipeline.md).*

## Police

- Police **outline** (lettres creuses), 16 px = 2 rangées de tuiles.
- Seuil de lecture : `max(r,g,b) > 60`.
- Encodage : `a-z`, espace, `0-9`, `! ? . '` — **pas d'accents, de virgules
  ni de tirets** (police limitée).

## Outils

| Outil | Rôle |
|---|---|
| `tools/_read_text.py` | Glyphes 8×8 d'un écran |
| `tools/_decode_all.py` | Référence de glyphes EN → décodage FR |
| `tools/_decode_screen_text.py` | Décodage d'écran avec la police du patch |
| `tools/_ascii_preview.py` | Aperçu ASCII rapide dans un terminal |

> Note : la correspondance bitmap contre le CHR ROM n'a pas été concluante
> (transformation palette/ombre probable) — à ré-étudier.

## Table de traductions (`tools/translations.py`)

Source de vérité. Clé = `(banque:offset, ligne)`, valeur = liste de chaînes FR,
une par **morceau de lettres (L)**. Les octets de contrôle et les **tokens de
noms (K)** sont préservés.

```python
# Tactiques de jeu (5 cases de 9 caractères)
T[('B3:00F732', 0)] = ['offensif marque frimeur automatic defensif']
# Dialogues du Downtown Quiz (banque 4)
T[('B4:0126FE', 34)] = ['exact!']
```

### Tokens de noms

```python
NAME_PATTERNS = [
    bytes([0xD7, 0xD8, 0x1F]),   # [KUNIO]
    bytes([0xDA, 0xD6]),         # [RIKI]
    bytes([0xD5, 0xD3, 0xD9]),   # [JOHNNY]
    bytes([0xD4, 0xDB, 0xDC]),   # [HOTE:]
    bytes([0xD2, 0xD1, 0x19]),   # [?2]
]
```

## Application (`tools/patch_rom.py`)

Garde chaque octet non-lettre en place, ne remplace que les lettres par le
français, dans le budget d'octets de chaque morceau L. Gère aussi des
réécritures spécifiques : menu de commandes (9 cases alignées + pointeurs),
boîtes du quiz (`patch_quiz_box`, `patch_box9`…), table DTE (« HOST: » →
« HOTE: »), et le démarrage direct dans l'état 4 (`patch_boot_state`,
`patch_skip_intro`).

## Génération IPS (`tools/make_ips.py`)

Produit les deux patches avec auto-vérification (réapplication de l'IPS →
comparaison octet à octet) :

- `orig_jp.nes → fr.nes` → `Nekketsu Street Basket (JPN) FR.ips` (19 Ko),
- `en.nes → fr.nes` → `Nekketsu Street Basket (v1.2 Final) FR.ips` (4 Ko).
