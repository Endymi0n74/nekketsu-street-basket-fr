# 04 — Pipeline texte, police et patch

## Police

- Police **outline** (lettres creuses), 16 px = 2 rangées de tuiles (rangée du
  haut = barre du haut de la lettre).
- Seuil de lecture des screenshots : `max(r,g,b) > 60`.
- Encodage disponible : `a-z`, espace, `0-9`, `! ? . '` — **pas d'accents, de
  virgules ni de tirets** (police limitée). Le texte FR en tient compte.

## Outils de lecture du texte

| Outil | Rôle |
|---|---|
| `tools/_read_text.py` | Glyphes 8×8 d'un écran (screenshot PNG) |
| `tools/_decode_all.py` | Référence de glyphes EN → décodage FR |
| `tools/_decode_screen_text.py` / `_decode_screens.py` | Décodage d'écran avec la police du patch |
| `tools/_ascii_preview.py` | Rendu ASCII d'un screenshot (aperçu rapide dans un terminal) |

> Note : la correspondance bitmap contre le CHR ROM (`_font_match.py`) n'a pas
> été concluante — la police ne se retrouve pas telle quelle dans les banques
> CHR (transformation palette/ombre probable). À ré-étudier.

## Table de traductions (`tools/translations.py`)

Source de vérité des traductions. Clé = `(banque:offset, ligne)`, valeur =
liste de chaînes françaises, une par **morceau de lettres (L)** de la ligne,
dans l'ordre. Les octets de contrôle et les **tokens de noms (K)** sont
préservés par le patcher.

Exemples :

```python
# Tactiques de jeu (5 cases de 9 caractères)
T[('B3:00F732', 0)] = ['offensif marque frimeur automatic defensif']
# Menu de commandes en jeu (9 commandes, cases alignées + pointeurs)
#   tir, ball en l'air, attaque, frappe, passe, ball, dunk, arme, hasard
# Dialogues du Downtown Quiz (banque 4)
T[('B4:0126FE', 34)] = ['exact!']
T[('B4:0126FE', 40)] = ['quel comeback']
```

### Tokens de noms (patterns)

```python
NAME_PATTERNS = [
    bytes([0xD7, 0xD8, 0x1F]),
    bytes([0xDA, 0xD6]),
    bytes([0xD5, 0xD3, 0xD9]),
    bytes([0xD4, 0xDB, 0xDC]),
    bytes([0xD2, 0xD1, 0x19]),
]
```

## Application (`tools/patch_rom.py`)

Stratégie : **garder chaque octet non-lettre en place** (contrôles, tokens de
noms) et ne remplacer que les octets-lettres par le français. Chaque chaîne FR
doit tenir dans le budget d'octets de son morceau L (sinon, complétée
d'espaces).

Blocs patchés (banque 3 et 4), ex. :
`(3, 0x00F6B4, 115)` noms d'équipes/lieux (anglais conservés : noms propres),
`(3, 0x00F732, 46)` tactiques,
`(4, 0x0126FE, 2293)` dialogues du quiz, etc.

## Génération IPS (`tools/make_ips.py`)

Produit les deux patches :
- `orig_jp.nes → fr.nes` → `Nekketsu Street Basket (JPN) FR.ips` (19 Ko, recommandé),
- `en.nes → fr.nes` → `Nekketsu Street Basket (v1.2 Final) FR.ips` (4 Ko).

Format IPS : en-tête `PATCH`, enregistrements `(offset 3 o, taille 2 o, data)`,
records RLE quand taille = 0, trailer `EOF`.
