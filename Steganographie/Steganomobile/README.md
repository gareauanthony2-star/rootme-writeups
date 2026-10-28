# Steganomobile

**Plateforme :** Root-Me | **Catégorie :** Stéganographie | **Outil :** aucun (lecture manuelle)

## 1. Énoncé

Après avoir extrait les données d'un téléphone mobile retrouvé sur les lieux d'un crime, les enquêteurs ont récupéré cette suite de chiffres :

```
222-33-555-555-7-44-666-66-33
```

Peut-être un numéro de téléphone ?

## 2. Solution trouvée

La suite de chiffres n'est pas un numéro de téléphone mais du texte encodé en **multitap**, la méthode de saisie des anciens claviers téléphoniques.

**Flag :** `xxxxxxxxx`

## 3. Comment j'ai trouvé

1. L'indication "téléphone mobile" + une suite de chiffres groupés par tirets m'a fait penser au clavier **ITU E.161** des anciens téléphones (avant smartphones), où chaque touche porte plusieurs lettres :
   ```
   1        2 ABC    3 DEF
   4 GHI    5 JKL    6 MNO
   7 PQRS   8 TUV    9 WXYZ
   ```
2. J'ai remarqué que les chiffres étaient toujours **répétés d'affilée** (`222`, `33`, `555`...) et séparés par des tirets — le principe du **multitap** : on appuie plusieurs fois de suite sur une touche pour choisir la lettre voulue (1 appui = 1ère lettre, 2 appuis = 2ème lettre, etc.).
3. J'ai décodé chaque groupe séparé par un tiret comme une seule lettre :

**Piège évité :** le titre du challenge ("numéro de téléphone ?") est un leurre volontaire — ce n'est pas un numéro à appeler, mais un indice sur **l'origine du système d'encodage** (le clavier d'un téléphone).

## 4. Explication

**Qu'est-ce que le multitap ?**
C'est la méthode de saisie de texte utilisée sur les téléphones à touches physiques avant les claviers tactiles. Chaque touche numérique correspond à 3 ou 4 lettres ; on appuie plusieurs fois de suite dessus pour choisir laquelle on veut.

**Pourquoi un tiret entre chaque groupe ?**
Sans séparateur, on pourrait pas savoir où une lettre se termine et où la suivante commence (ex : `22` pourrait être "B" ou deux fois "A"). Le tiret joue ici le rôle de **délimiteur de caractère**, comme un espace entre les lettres d'un mot en morse.

**Pourquoi "stéganographie" et pas "cryptographie" ?**
Contrairement à un chiffrement, il n'y a **aucune clé** ici — l'info est seulement **encodée dans un format inhabituel** (une suite de chiffres qui ressemble à un numéro de téléphone) pour la dissimuler aux yeux non avertis. Le but n'est pas de rendre le message indéchiffrable, mais de le faire passer inaperçu sous une autre apparence.

## 5. Conclusion

**Ce que j'ai appris :**
- Reconnaître le pattern "chiffres répétés + tirets" comme signature probable du multitap.
- La différence entre encodage (réversible, sans clé) et chiffrement (nécessite une clé).
- En stéganographie, l'indice de l'énoncé ("téléphone mobile") pointe souvent directement vers le système d'encodage à utiliser.

**Point de vue DevSecOps (parade) :**
- ce challenge est purement pédagogique (pas de vulnérabilité système réelle), mais il illustre un principe utile en analyse forensique : ne jamais prendre une donnée à sa valeur apparente — toujours questionner le format et le contexte de récupération (ici, "données extraites d'un téléphone") avant de l'interpréter.
