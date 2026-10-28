# TCP - Retour au collège

**Plateforme :** Root-Me | **Catégorie :** Programmation | **Langage :** Python

## 1. Énoncé

Se connecter à un programme via une socket TCP :
- calculer la racine carrée du nombre n°1,
- multiplier le résultat par le nombre n°2,
- arrondir à 2 décimales,
- répondre en **moins de 2 secondes**.

| Hôte | Protocole | Port |
|------|-----------|------|
| challenge01.root-me.org | TCP | 52002 |

## 2. Solution trouvée

```python
import socket
import math
import re

HOST = "challenge01.root-me.org"
PORT = 52002

s = socket.create_connection((HOST, PORT))  # ouvre la connexion TCP

data = s.recv(4096).decode()  # lit le message du serveur (bytes -> texte)
print("Reçu :", data)

# extrait les deux nombres de la phrase du serveur
m = re.search(r"square root of (\d+).*?multiply by (\d+)", data, re.S)
n1, n2 = int(m.group(1)), int(m.group(2))

result = round(math.sqrt(n1) * n2, 2)  # calcul + arrondi à 2 décimales
print("Envoi :", result)

s.sendall(f"{result:.2f}\n".encode())  # envoi en texte décimal + retour à la ligne

print("Réponse :", s.recv(4096).decode())  # le flag apparaît ici
s.close()
```

## Résultat obtenu :

```
Calculate the square root of 155 and multiply by 6881 =
Envoi : 85667.76
Réponse : [+] Good job ! Here is your flag: RM{...}
```

## 3. Comment j'ai trouvé

**Analyse :** 2 secondes sont difficiles à la main, donc il faut un script
qui se connecte, lit le calcul, répond tout seul.

**Première version (qui ne marchait pas) :** j'étais parti d'un exemple de
classe `MySocket` trouvé dans la doc Python, avec `bin(int(float(result)))`
pour envoyer la réponse. Erreur obtenue :

```
TypeError: a bytes-like object is required, not 'str'
```

**Les erreurs, une par une :**

| Problème | Ancien code | Correction |
|---|---|---|
| Type envoyé | `str` | `bytes` avec `.encode()` |
| Format du nombre | `bin()` → `0b1111...` | décimal `85667.76` |
| Valeur envoyée | `int(...)`, sans décimales, `final_result` jamais utilisé | `round(..., 2)` envoyé avec `:.2f` |
| Fin de message | pas de `\n` | `\n` ajouté |
| Lecture de la réponse | aucune | `recv` final |
| Extraction des nombres | `split(" ")[-5]`, fragile | regex |
| Lecture | exactement 195 octets, sinon blocage | `recv(4096)` |

## 4. Explication

- **Socket TCP** : un tuyau entre mon programme et le serveur. On y lit et on y écrit des **bytes**, jamais du texte direct.
- **`.decode()` / `.encode()`** : passer de bytes à texte (réception) et de texte à bytes (envoi).
- **Regex** : retrouve les deux nombres dans la phrase, même si la mise en forme change un peu.
- **`:.2f`** : force 2 chiffres après la virgule (`85667.70` et non `85667.7`).
- **`\n`** : indique au serveur que la réponse est terminée.

## 5. Conclusion

**Ce que j'ai appris :**
- le fonctionnement d'une socket TCP en Python,
- la différence entre `str` et `bytes`,
- lire une erreur Python (`TypeError`) pour comprendre le problème,
- extraire des données d'un texte avec une regex.

**Point de vue DevSecOps :** automatiser une interaction réseau est la base
des scripts de test et de scan. Côté défense, une limite de temps est une
protection faible : un script répond en quelques millisecondes.
