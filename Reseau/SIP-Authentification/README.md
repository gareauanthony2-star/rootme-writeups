# Root-Me : Authentification SIP (Asterisk)

Write-up d'un challenge d'analyse de capture réseau SIP (téléphonie sur IP), extraction d'identifiants depuis un échange d'authentification Digest.

## Présentation

| | |
|---|---|
| **Catégorie** | Réseau / VoIP |
| **Protocole** | SIP (Session Initiation Protocol) |
| **Serveur** | Asterisk (IPBX) |
| **Outil utilisé** | sipdump (extraction depuis une capture `.pcap`) |
| **Objectif** | Retrouver le mot de passe d'un compte SIP |

**Énoncé (reconstitué) :** à partir d'une capture réseau contenant des échanges SIP entre un client (`172.25.105.3`) et un serveur Asterisk (`172.25.105.40`), retrouver le mot de passe du compte SIP 555.

## Notions utiles

### L'authentification SIP Digest

SIP utilise le même mécanisme d'authentification que HTTP Digest :

1. Le client envoie une requête (`REGISTER`, `INVITE`, `BYE`...).
2. Le serveur répond `401 Unauthorized` avec un **nonce** (valeur aléatoire) et un **realm** (domaine d'authentification).
3. Le client recalcule une réponse chiffrée et la renvoie dans un en-tête `Authorization` :

```
HA1 = MD5(username:realm:password)
HA2 = MD5(method:uri)
response = MD5(HA1:nonce:HA2)
```

Le mot de passe en clair ne circule normalement jamais sur le réseau : seul le `response` (un hash) est transmis. C'est pour cela qu'un outil comme **sipcrack** permet de le casser hors ligne, par dictionnaire, à partir de ce hash.

### Le format d'extraction (sipdump)

L'outil `sipdump` lit une capture `.pcap` et en extrait les échanges d'authentification SIP sous forme de lignes `"`-séparées :

```
IP_source"IP_dest"utilisateur"realm"méthode"uri"nonce""""TYPE"valeur
```

Le champ `TYPE` vaut :
- **`MD5`** si la valeur qui suit est le hash `response` (cas normal, à casser par dictionnaire)
- **`PLAIN`** si la valeur qui suit est le mot de passe en clair (cas plus rare, révélé directement)

## Données capturées

```
172.25.105.3"172.25.105.40"555"asterisk"REGISTER"sip:172.25.105.40"4787f7ce""""PLAIN"[masqué]
172.25.105.3"172.25.105.40"555"asterisk"INVITE"sip:1000@172.25.105.40"70fbfdae""""MD5"aa533f6efa2b2abac675c1ee6cbde327
172.25.105.3"172.25.105.40"555"asterisk"BYE"sip:1000@172.25.105.40"70fbfdae""""MD5"0b306e9db1f819dd824acf3227b60e07
```

| Méthode | Nonce | Type | Valeur |
|---|---|---|---|
| REGISTER | `4787f7ce` | **PLAIN** | `[masqué]` |
| INVITE | `70fbfdae` | MD5 | `aa533f6efa2b2abac675c1ee6cbde327` |
| BYE | `70fbfdae` | MD5 | `0b306e9db1f819dd824acf3227b60e07` |

## Résolution

### 1. Identifier le compte ciblé

Les trois lignes concernent le même utilisateur SIP : **555**, sur le serveur Asterisk `172.25.105.40` (realm `asterisk`).

### 2. Repérer la ligne la plus facile à exploiter

Sur les trois échanges, deux sont en `MD5` (INVITE et BYE) : il faudrait les casser par dictionnaire avec `sipcrack` ou `hashcat -m 11400`, ce qui ne réussit que si le mot de passe figure dans la wordlist utilisée.

La ligne `REGISTER` est en revanche marquée **`PLAIN`** : la valeur qui suit n'est pas un hash, c'est le mot de passe du compte, transmis tel quel.

### 3. Lire le mot de passe

```
...REGISTER"sip:172.25.105.40"4787f7ce""""PLAIN"[masqué]
```

Le champ après `PLAIN` donne directement le mot de passe, en clair.

### 4. Vérifier la cohérence

Les deux nonces différents (`4787f7ce` pour REGISTER, `70fbfdae` partagé par INVITE/BYE) montrent qu'il s'agit de deux échanges distincts : l'enregistrement du poste, puis l'ouverture et la fermeture d'un appel. C'est normal dans une session SIP complète, et les trois lignes correspondent bien au même utilisateur et au même mot de passe.

## Résultat

**Compte :** 555
**Mot de passe :** `[masqué]`

Conformément aux règles de Root-Me, la solution n'est pas publiée. La méthode ci-dessus permet de la retrouver en quelques secondes à partir de la capture.

## Conclusion

- SIP s'appuie sur une authentification Digest proche de HTTP : un nonce envoyé par le serveur, une réponse `MD5` calculée par le client.
- Dans une extraction `sipdump`, une ligne marquée `PLAIN` donne le mot de passe directement, sans calcul ni cassage. C'est le cas le plus simple, mais aussi le plus rare : la plupart des lignes réelles sont en `MD5` et demandent une attaque par dictionnaire.
- Ce challenge illustre un mot de passe faible et trivial, un classique en sécurité : même un mécanisme d'authentification correctement implémenté ne protège rien si le secret est faible ou exposé en clair.
