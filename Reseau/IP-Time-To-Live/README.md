# Root-Me : IP - Time To Live

Write-up du challenge **IP - Time To Live** (catégorie Réseau, analyse de capture réseau).

## Présentation

| | |
|---|---|
| **Plateforme** | Root-Me |
| **Catégorie** | Réseau |
| **Challenge** | IP - Time To Live |
| **Points** | 15 |
| **Auteur** | g0uZ (1er septembre 2010) |
| **Outil utilisé** | Wireshark |
| **Fichier fourni** | `ch7.pcap` |

**Énoncé :** retrouver le TTL employé pour atteindre l'hôte ciblé par cet échange de paquets ICMP.

## Notions utiles

Le **TTL** (Time To Live) est un champ de l'en-tête IP, un compteur de sauts.

1. L'émetteur place une valeur de départ dans le paquet.
2. Chaque routeur traversé retire 1.
3. Si le TTL arrive à 0, le routeur jette le paquet et renvoie à l'émetteur un message ICMP **Time-to-live exceeded**.

C'est le principe de `traceroute` : il envoie des paquets avec un TTL de 1, puis 2, puis 3, etc. Chaque routeur qui répond « Time-to-live exceeded » se dévoile, jusqu'à ce que le paquet atteigne la cible.

## Résolution

### 1. Ouvrir la capture

Ouvrir `ch7.pcap` dans Wireshark et filtrer le trafic ICMP :

```
icmp
```

### 2. Observer l'échange

![Capture Wireshark de l'échange ICMP](img/wireshark-ttl.png)

La machine `24.6.126.218` envoie des pings vers `198.173.244.32` avec un TTL qui **augmente** à chaque série : 9, 10, 11, 12, 13. C'est un traceroute.

| TTL envoyé | Réponse | Émetteur de la réponse |
|---|---|---|
| 9 | Time-to-live exceeded | 129.250.4.197 |
| 10 | Time-to-live exceeded | 129.250.5.35 |
| 11 | Time-to-live exceeded | 129.250.27.187 |
| 12 | Time-to-live exceeded | 204.2.121.162 |
| **13** | **Echo (ping) reply** | **198.173.244.32 (la cible)** |

Tant que le TTL est trop faible, un routeur intermédiaire jette le paquet et le signale. Les lignes Wireshark affichent `no response found!`, car la cible n'a pas répondu.

### 3. Trouver le premier TTL qui fonctionne

Les derniers paquets (71, 73 et 75) sont différents : Wireshark indique `reply in ...` au lieu de `no response found!`, et la cible `198.173.244.32` envoie un **Echo reply**.

Le paquet 71 a un **TTL de 13** : c'est la plus petite valeur pour laquelle le paquet arrive jusqu'à l'hôte. Avec 12, il meurt avant d'arriver.

### 4. Le piège : `ttl=51`

Les réponses de la cible affichent `ttl=51`. Ce n'est pas la réponse attendue : c'est le TTL du paquet de **retour**, et non celui employé pour atteindre l'hôte.

La cible répond avec un TTL de départ de 64 (valeur courante sur Linux). Le paquet traverse aussi 13 routeurs au retour : 64 - 13 = 51. Cela confirme que le chemin compte bien 13 sauts.

## Résultat

Le TTL employé pour atteindre l'hôte ciblé est **13**.

## Conclusion

- Le TTL limite la durée de vie d'un paquet, et `traceroute` s'en sert pour cartographier le chemin.
- Un TTL minimal permet de compter le nombre de routeurs entre deux machines.
- Dans une capture, il faut distinguer le TTL des paquets **aller** (requêtes) de celui des paquets **retour** (réponses), qui part d'une autre valeur de départ.
- Ce challenge rappelle l'intérêt de Wireshark pour lire un échange ICMP paquet par paquet.
