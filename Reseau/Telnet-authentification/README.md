# Telnet - Authentification

**Plateforme :** Root-Me | **Catégorie :** Réseau | **Outil :** Wireshark

## 1. Énoncé

Retrouver le mot de passe de l'utilisateur dans une capture réseau (`.pcap`) d'une session **Telnet**.

## 2. Solution trouvée

Le mot de passe est visible en clair dans le flux TCP de la session Telnet, juste après l'invite `Password:`.

**Mot de passe :** `RM{...}` (masqué, à retrouver avec la méthode ci-dessous)

## 3. Comment j'ai trouvé

1. J'ai ouvert la capture dans **Wireshark** et appliqué le filtre `telnet`.
2. Dans la liste, la colonne *Info* n'affiche que `Telnet Data ...` : le contenu n'est pas lisible paquet par paquet.
3. J'ai cliqué sur un paquet Telnet, puis **Analyser > Suivre > Flux TCP**.
4. Wireshark a réassemblé la session en texte lisible (affichage ASCII). J'y ai lu `login:`, l'identifiant, puis `Password:` et la saisie qui suit.

**Piège évité :** au début, j'ai cherché une ligne `PASS xxx` comme en FTP et je pensais que Telnet chiffrait les données. C'est faux : Telnet n'est pas chiffré, mais il envoie les caractères **un par un**, dans des paquets séparés.

## 4. Explication

**Pourquoi le mot de passe n'est pas lisible dans la liste ?**
Chaque touche tapée est envoyée dans son propre petit paquet. Le mot de passe est donc éparpillé sur plusieurs paquets, une lettre chacun.

**Que fait "Suivre le flux TCP" ?**
Ce n'est pas un déchiffrement, c'est un **réassemblage** : Wireshark remet dans l'ordre tous les paquets d'une même conversation et les affiche collés.

**Autres éléments rencontrés dans la capture :**
- Les octets `ff fb ...` / `ff fd ...` sont des **négociations d'options Telnet** (protocole), pas des données utilisateur.
- Le port de destination est **23**, le port standard de Telnet.
- Le texte **rouge** est envoyé par le client, le **bleu** par le serveur.
- L'écho du serveur ou des touches effacées peuvent perturber la lecture : il faut lire la saisie du client.

**Comparaison FTP / Telnet / SSH :**

| | FTP | Telnet | SSH |
|---|---|---|---|
| Chiffrement | non | non | oui |
| Mot de passe dans la liste des paquets | oui (`PASS ...` en un paquet) | non (lettre par lettre) | illisible |
| Méthode | filtre `ftp.request.command == "PASS"` | Suivre le flux TCP | impossible sans la clé |

## 5. Conclusion

**Ce que j'ai appris :**
- Telnet n'est pas chiffré : tout circule en clair.
- Un protocole en clair n'est pas toujours lisible directement : il peut être fragmenté en plusieurs paquets.
- La fonction *Suivre le flux TCP* réassemble une conversation.
- Faire la différence entre chiffrement et fragmentation.

**Point de vue DevSecOps (parade) :**
- remplacer Telnet par **SSH**,
- désactiver Telnet sur les équipements réseau (routeurs, switchs) et n'autoriser que SSH,
- limiter l'accès à l'administration à un VLAN dédié.
