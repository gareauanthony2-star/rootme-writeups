# FTP - Authentification

**Plateforme :** Root-Me | **Catégorie :** Réseau | **Outil :** Wireshark

## 1. Énoncé

Un échange authentifié de fichier réalisé grâce au protocole FTP.
Retrouver le mot de passe utilisé par l'utilisateur à partir d'une capture réseau (`.pcap`).

## 2. Solution trouvée

Le mot de passe est visible en clair dans le paquet n°11 :

```
Request: USER cdts3500
Request: PASS cdts3500
Response: 230 CDTS3500 logged on.
```

**Mot de passe :** `RM{...}` (masqué, à retrouver avec la méthode ci-dessous)

## 3. Comment j'ai trouvé

1. J'ai ouvert la capture dans **Wireshark**.
2. J'ai repéré le protocole `FTP` dans la colonne *Protocol* de la liste des paquets.
3. J'ai appliqué un filtre d'affichage pour isoler la commande qui contient le mot de passe :

```
ftp.request.command == "PASS"
```

4. Le paquet n°11 s'affiche seul. Le mot de passe est dans la colonne *Info* : `Request: PASS <mot de passe>`.
5. Vérification : le serveur répond `230 ... logged on` au paquet suivant, donc le mot de passe est accepté.

**Piège évité :** en lisant la colonne ASCII du panneau hexadécimal, j'ai cru voir un `0a` collé au mot de passe. En réalité, `0d 0a` est le saut de ligne (`\r\n`) de fin de commande FTP, il ne fait pas partie du mot de passe. Pour éviter cette erreur, on peut déplier `File Transfer Protocol (FTP)` et lire `Request arg`.

## 4. Explication

**Les 3 fenêtres de Wireshark :**
- **Haut (Packet List)** : un paquet par ligne, vue d'ensemble.
- **Bas gauche (Packet Details)** : le paquet décortiqué couche par couche (Ethernet, IP, TCP, FTP).
- **Bas droite (Packet Bytes)** : le contenu brut en hexadécimal et ASCII.

**Pourquoi ça marche :** FTP est un protocole **non chiffré**. Les commandes
(`USER`, `PASS`, `PWD`, `SYST`...) circulent en texte brut sur le réseau.
Quiconque capture le trafic peut lire l'identifiant et le mot de passe.

`PASS` est une commande du protocole FTP, pas un mot de Wireshark : elle s'appelle toujours ainsi, quel que soit le serveur.

**Alternative :** clic droit sur un paquet FTP > *Suivre > Flux TCP* affiche toute la conversation en texte lisible.

**Limites :** la méthode fonctionne pour les protocoles non chiffrés (FTP, Telnet, HTTP, POP3, IMAP). Elle ne fonctionne pas pour SFTP, FTPS, SSH ou HTTPS.

## 5. Conclusion

**Ce que j'ai appris :**
- à utiliser les 3 panneaux de Wireshark,
- à filtrer un protocole et une commande précise,
- que les protocoles non chiffrés exposent les identifiants,
- à lire de l'hexadécimal et à distinguer données et fin de ligne.

**Point de vue DevSecOps (parade) :**
- remplacer FTP par **SFTP** (via SSH) ou **FTPS** (FTP + TLS),
- désactiver FTP, Telnet et HTTP simples sur les serveurs,
- segmenter le réseau et limiter les accès pour réduire les risques de capture.
