# Authentification Twitter

**Plateforme :** Root-Me | **Catégorie :** Réseau | **Outil :** Wireshark

## 1. Énoncé

Une session d'authentification Twitter a été capturée. Retrouver le mot de passe de l'utilisateur dans cette capture réseau (`.pcap`).

## 2. Solution trouvée

Le mot de passe est encodé en Base64 dans l'en-tête HTTP `Authorization` de la requête.

**Mot de passe :** `password`

## 3. Comment j'ai trouvé

1. J'ai ouvert la capture dans **Wireshark** et appliqué le filtre `http`.
2. Une requête `GET /statuses/replies.xml HTTP/1.1` vers `twitter.com` contient un en-tête `Authorization: Basic dXNlcnRlc3Q6cGFzc3dvcmQ=`.
3. Wireshark décode lui-même cette valeur et affiche en dessous `Credentials: usertest:password`.
4. Pour vérifier par moi-même, j'ai décodé la chaîne en Base64 dans un terminal :
   ```bash
   echo "dXNlcnRlc3Q6cGFzc3dvcmQ=" | base64 -d
   # usertest:password
   ```

**Piège évité :** au début j'ai cru que `Basic` dans l'en-tête voulait dire "mot de passe en clair" — en fait c'est le nom du **schéma d'authentification** (HTTP Basic Auth), et la valeur qui suit est toujours encodée en Base64, jamais écrite telle quelle.

## 4. Explication

**Comment fonctionne l'authentification HTTP Basic ?**
Le client construit la chaîne `login:mot_de_passe`, l'encode en Base64, et l'envoie dans l'en-tête `Authorization: Basic <chaîne encodée>` à chaque requête.

**Est-ce que c'est chiffré ?**
Non. Le Base64 est un **encodage**, pas un chiffrement — il est réversible instantanément, sans clé, par n'importe qui. C'est pour ça que Wireshark le décode automatiquement et l'affiche en clair.

**Pourquoi utiliser ça alors ?**
Ce mécanisme est pensé pour être combiné avec **HTTPS/TLS** : c'est le chiffrement du transport (TLS) qui protège les identifiants, pas le Base64 en lui-même. Ici, la capture étant en HTTP simple (pas HTTPS), tout circule en clair.

**Format de la chaîne décodée :**
`login:mot_de_passe`, séparés par deux-points — ici `usertest:password`.

## 5. Conclusion

**Ce que j'ai appris :**
- L'authentification HTTP Basic encode en Base64, elle ne chiffre pas.
- Un encodage se décode instantanément, sans mot de passe ni calcul — contrairement à un hash ou un chiffrement.
- Toujours vérifier si une capture passe par HTTP (en clair) ou HTTPS (chiffré) avant de chercher un identifiant.

**Point de vue DevSecOps (parade) :**
- interdire l'authentification HTTP Basic sans HTTPS,
- forcer la redirection HTTP → HTTPS sur tous les services,
- préférer des mécanismes d'authentification par token (OAuth, JWT) plutôt que Basic Auth quand c'est possible.
