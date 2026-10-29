# Write-up — Root-Me : Kerberos - Authentification

**Catégorie :** Réseau
**Points :** 10
**Format du flag :** `RM{userPrincipalName:password}`

> Le nom d'utilisateur et le mot de passe trouvés ne sont pas reproduits en clair dans ce write-up (politique de Root-Me / pour éviter de spoiler la solution). Ils sont remplacés par `<username>` et `<password>`.

## Contexte

Le challenge fournit une capture réseau (`.pcap`) d'une authentification Kerberos jugée suspecte au sein d'un domaine Active Directory. L'objectif est de retrouver, à partir du trafic capturé, l'identifiant de l'utilisateur ainsi que son mot de passe en clair.

---

## Moyens utilisés

- **Wireshark** pour l'analyse de la capture réseau et la lecture des échanges Kerberos / SMB
- **WSL (Windows Subsystem for Linux)** avec une distribution **Ubuntu**, pour disposer d'un environnement Linux sur un poste Windows
- **hashcat** pour casser le mot de passe par attaque en dictionnaire
- **rockyou.txt** comme dictionnaire de mots de passe

---

## Explication des outils et notions clés

### Le protocole Kerberos

Kerberos est un protocole d'authentification réseau utilisé par Active Directory. Il repose sur un tiers de confiance, le **KDC** (Key Distribution Center, hébergé sur le contrôleur de domaine), qui délivre des tickets sans jamais faire transiter le mot de passe de l'utilisateur sur le réseau.

Le principe clé exploité dans ce challenge est la **pré-authentification** (PA-ENC-TIMESTAMP) : avant de délivrer un ticket, le KDC exige que le client prouve qu'il connaît le mot de passe. Pour cela, le client chiffre un horodatage avec une clé dérivée de son mot de passe (algorithme AES256, `etype 18`) et l'envoie dans l'`AS-REQ`. Ce chiffré circule sur le réseau et constitue la donnée exploitable : il permet de tester des mots de passe candidats hors ligne en vérifiant lequel permet de déchiffrer correctement l'horodatage.

Ce n'est **pas** un AS-REP Roasting (qui exploite l'absence de pré-authentification) : ici la pré-authentification est active (`KRB5KDC_ERR_PREAUTH_REQUIRED` renvoyé au premier essai), donc l'attaque porte sur le PA-ENC-TIMESTAMP de l'`AS-REQ`, exploitable par **hashcat** en mode `19900` (Kerberos 5, etype 18, Pre-Auth).

### Wireshark

Utilisé pour filtrer et isoler le trafic Kerberos (`kerberos`, ou `tcp.port == 88 || udp.port == 88`) au sein d'une capture mêlant aussi du trafic SMB2/NTLM (authentification machine-machine, sans rapport avec Kerberos) et du DCERPC (ouverture de canal RPC, trafic normal après une session SMB).

### hashcat

Outil de cassage de mots de passe par calcul massivement parallèle (GPU/CPU). Il prend un hash normalisé dans un format spécifique à chaque type d'attaque et teste des mots de passe candidats issus d'un dictionnaire, en recalculant le chiffrement correspondant jusqu'à trouver une correspondance.

### rockyou.txt

Dictionnaire de référence en sécurité offensive, issu d'une fuite de données du site RockYou en 2009 (mots de passe stockés en clair à l'époque). Il contient environ 14 millions de mots de passe réels, souvent efficace contre des mots de passe faibles ou communs.

### WSL / Ubuntu

Environnement Linux complet exécuté nativement sous Windows (sans VM classique type VirtualBox), utilisé ici pour disposer de `apt`, `hashcat` et d'un shell Linux fonctionnel.

---

## Manipulation des codes

### Identification du flux Kerberos pertinent dans Wireshark

Filtre appliqué :

```
kerberos
```

Séquence observée :

```
AS-REQ                         (sans succès, pré-auth requise)
KRB Error: KRB5KDC_ERR_PREAUTH_REQUIRED
AS-REQ                         (avec PA-ENC-TIMESTAMP)
AS-REP
TGS-REQ
TGS-REP
```

### Extraction des données utiles

Dans le second `AS-REQ` (celui contenant le `PA-ENC-TIMESTAMP`) :

- **cname** : `<username>`
- **realm** : `<REALM>`
- **etype** : `eTYPE-AES256-CTS-HMAC-SHA1-96 (18)`
- **cipher** : valeur hexadécimale du champ `padata-value` sous `PA-ENC-TIMESTAMP`

### Construction du hash au format hashcat

```
$krb5pa$18$<username>$<REALM>$<cipher_hex>
```

Enregistrement dans un fichier (sous Ubuntu/WSL, avec `nano` pour éviter toute interprétation du `$` par le shell) :

```bash
nano hash.txt
# coller la ligne, Ctrl+O puis Entrée pour sauvegarder, Ctrl+X pour quitter
cat hash.txt
```

### Installation de l'environnement de cassage

```bash
sudo apt update
sudo apt install hashcat -y
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
```

### Lancement de l'attaque

```bash
hashcat -m 19900 hash.txt ~/rockyou.txt
```

### Résultat

```
$krb5pa$18$<username>$<REALM>$<cipher_hex>:<password>
```

Le mot de passe en clair est retrouvé dans la liste `rockyou.txt`.

### Construction du flag

Le format demandé par Root-Me est `RM{userPrincipalName:password}`, en minuscules pour l'`userPrincipalName`. Le `cname` extrait de la capture correspond au nom court (sAMAccountName) plutôt qu'à l'UPN complet, qui prend généralement la forme `utilisateur@domaine` :

```
RM{<username>@<realm_minuscule>:<password>}
```

---

## Conclusion

Ce challenge illustre une faiblesse classique du protocole Kerberos : même lorsque la pré-authentification est activée, le mécanisme de preuve de connaissance du mot de passe (PA-ENC-TIMESTAMP) expose un texte chiffré exploitable hors ligne par une attaque par dictionnaire, en particulier lorsque le mot de passe de l'utilisateur est faible ou présent dans des dictionnaires connus comme rockyou.txt.

D'un point de vue défensif, ce type d'attaque souligne l'importance d'imposer des mots de passe robustes et longs sur les comptes de domaine, afin de rendre ce type de cassage hors ligne impraticable, ainsi que la surveillance des échecs d'authentification répétés (`KRB5KDC_ERR_PREAUTH_REQUIRED`) qui peuvent trahir une tentative de ce type.

La principale difficulté pratique a été la mise en place de l'environnement d'outils (hashcat non disponible nativement sous Windows, nécessité de passer par WSL/Ubuntu), plus que l'analyse Kerberos elle-même une fois le bon paquet identifié dans Wireshark.
