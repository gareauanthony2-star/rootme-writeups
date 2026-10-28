# HTTP - Authentification Basic (capture hexdump)

**Plateforme :** Root-Me | **Catégorie :** Réseau | **Outils :** Wireshark, Python

## 1. Énoncé

Retrouver le mot de passe de l'utilisateur dans une capture réseau fournie sous forme de fichier texte (`ch12.txt`).

## 2. Solution trouvée

La capture contient une seule requête HTTP avec un en-tête `Authorization: Basic`. La valeur qui suit est du **base64** de `identifiant:motdepasse`.

```
GET / HTTP/1.1
Authorization: Basic <chaîne base64 masquée>
User-Agent: InsaneBrowser
Host: www.myipv6.org
Accept: */*
```

**Mot de passe :** `RM{...}` (masqué, à retrouver avec la méthode ci-dessous)

## 3. Comment j'ai trouvé

1. J'ai essayé d'ouvrir `ch12.txt` dans Wireshark : erreur *"isn't a capture file in a format Wireshark understands"*. Ce n'est pas une capture `.pcap`, mais un **hexdump** (les octets d'un paquet écrits en texte).
2. J'ai importé le fichier avec **Fichier > Importer à partir d'un dump hexadécimal**.
3. Dans le panneau des octets (en bas à droite), la colonne **ASCII** affiche la requête HTTP. J'y ai repéré la ligne `Authorization: Basic` suivie d'une chaîne se terminant par `==`.
4. J'ai recopié la chaîne base64 (coupée sur deux lignes dans Wireshark, donc à recoller).
5. Je l'ai décodée avec Python :

```python
import base64

encoded = "CHAINE_BASE64"
print(base64.b64decode(encoded).decode())
```

6. Résultat au format `identifiant:motdepasse`. Le mot de passe est la partie **après les deux-points**.

**Pièges rencontrés :**
- **Filtre resté actif** : après un "Suivre le flux TCP", le filtre `tcp.stream eq 0` masquait le paquet (*Affichés : 0*). Il suffit de l'effacer.
- **Import mal réglé** : mon fichier contenait déjà une trame complète, mais Wireshark a ajouté un faux en-tête Ethernet et n'a pas reconnu HTTP (il affichait seulement `Data`). Pour un décodage automatique, il fallait choisir *Décalages : Aucun* et *Aucune entête factice*. La lecture dans le panneau ASCII suffisait ici.
- **Caractères ambigus** : `I`/`l` et `0`/`O` se confondent facilement. Il faut recopier la chaîne avec soin.

## 4. Explication

**Authentification HTTP Basic :** le navigateur envoie

```
Authorization: Basic base64(identifiant:motdepasse)
```

**Le base64 est un encodage, pas un chiffrement.** Il n'y a aucune clé : n'importe qui peut le décoder en une seconde.

**Les `==` à la fin** sont le *padding* du base64, un indice pour reconnaître cet encodage.

**Le mot de passe est-il toujours après `Authorization` ?** Non. C'est le cas ici parce que c'est du Basic Auth. Ailleurs, il peut se trouver :

| Où | Exemple |
|---|---|
| Formulaire de login (HTTP POST) | `username=admin&password=1234` dans le corps |
| Cookie | `Cookie: session=...` |
| Token | `Authorization: Bearer ...` (un token, pas un mot de passe) |
| FTP, POP3 | commande `PASS ...` |
| Telnet | frappes envoyées une par une (Suivre le flux TCP) |
| URL | `?password=...` |

**Filtres Wireshark utiles :**
- `http.authorization` : les en-têtes Authorization
- `http.request.method == "POST"` : les formulaires
- *Suivre > Flux TCP* : toute la conversation en texte
- `Ctrl+F` puis chaîne `pass` : recherche dans les paquets

**Lien avec les autres write-ups :**

| | FTP | Telnet | HTTP Basic |
|---|---|---|---|
| Chiffrement | non | non | non (base64 = simple encodage) |
| Où est le mot de passe | commande `PASS` | frappes séparées | en-tête `Authorization` |
| Méthode | filtre `ftp.request.command == "PASS"` | Suivre le flux TCP | lire l'en-tête puis décoder le base64 |

## 5. Conclusion

**Ce que j'ai appris :**
- reconnaître un hexdump et l'importer dans Wireshark,
- lire des données dans les panneaux hexadécimal et ASCII,
- la différence entre **encodage** (base64) et **chiffrement**,
- où chercher des identifiants selon le protocole.

**Point de vue DevSecOps (parade) :**
- utiliser **HTTPS** : le contenu de la requête, en-têtes compris, est chiffré,
- éviter Basic Auth sur HTTP simple, préférer des sessions, des tokens ou OAuth,
- ne jamais faire transiter de mot de passe sur un réseau non chiffré (Wi-Fi public, réseau partagé).
