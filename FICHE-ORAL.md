# Fiche oral — NutriRecettes

> Aide-mémoire pour la présentation devant le prof. Tu peux lire chaque section telle quelle, pas besoin de tout retenir par cœur.

---

## 1 · Le pitch (30 secondes)

> "NutriRecettes, c'est un site qui résout un problème simple : on ouvre le frigo, on a quelques ingrédients, et on ne sait pas quoi cuisiner. L'utilisateur coche ce qu'il a, choisit une cuisine du monde — la française, l'algérienne, la japonaise — et une intelligence artificielle écrit une recette inédite à partir de ses ingrédients. Avec le tableau nutritionnel, le coût estimé, une anecdote culturelle sur le plat, et même un mode pas-à-pas pour cuisiner. C'est le pendant nutrition d'une plateforme bien-être complète, l'autre partie de notre groupe développe l'app sport."

---

## 2 · La démo à montrer (3 minutes)

URL du site : **https://nutrirecettes.vercel.app**

Étapes à dérouler devant le prof :

1. **L'écran d'entrée** — splash cinématique sur fond violet/aubergine. Cliquer n'importe où pour entrer.
2. **La page d'accueil** — une **planète Terre 3D** qui tourne, avec 19 points oranges qui représentent les 19 cuisines du monde couvertes. Faire pivoter la planète à la souris pour montrer l'interactivité.
3. **Cliquer sur "Composer une recette"** ou un point pays (par exemple l'Algérie).
4. **Page de composition** — cocher 4-5 ingrédients (un par catégorie : Poulet, Tomate, Riz, Curry, Basilic). Montrer l'indicateur d'équilibre nutritionnel en bas qui passe au vert.
5. **Cliquer "GÉNÉRER LA RECETTE"** — l'IA met 5 à 10 secondes pour écrire la recette.
6. **Page recette** — montrer le titre serif italique avec dégradé or-rose, la vraie photo du plat à droite, l'anecdote culturelle, le tableau nutritionnel avec les barres de progression, le coût estimé, et le score d'authenticité.
7. **Cliquer "Mode pas-à-pas"** — montrer l'écran plein écran avec les grandes étapes une par une, le minuteur intégré, et la navigation au clavier (touches flèches).
8. **Revenir et cliquer "Sauver au carnet"** — montrer le carnet avec la recette enregistrée.

**Si le wifi est lent ou que ça plante** : montrer les screenshots préparés à la fin de cette fiche.

---

## 3 · Les fonctionnalités clés (pour les bullet points)

- **19 cuisines du monde** couvertes (Europe, Asie, Maghreb, Afrique de l'Est, Amériques, Moyen-Orient)
- **Planète Terre 3D interactive** sur la page d'accueil
- **IA Claude** d'Anthropic qui écrit la recette en fonction des ingrédients
- **Vraies photos de plats** récupérées via une API spécialisée cuisine (Spoonacular)
- **Tableau nutritionnel complet** : calories, protéines, glucides, lipides, fibres
- **Indicateur santé** vert / orange / rouge selon l'équilibre du plat
- **Anecdote culturelle** générée par l'IA sur chaque plat
- **Score d'authenticité** : Traditionnel / Adapté / Fusion
- **Coût estimé** en euros
- **Substitutions intelligentes** pour chaque ingrédient
- **Mode cuisine pas-à-pas** avec minuteur intégré et navigation clavier
- **Carnet de recettes** sauvegardé dans le navigateur
- **Responsive** : adapté mobile (swipe horizontal entre catégories, liste de cuisines tap-friendly)
- **Filtres régime** : végétarien, halal, sans gluten, sans lactose

---

## 4 · La stack technique (vulgarisée)

Tu n'as pas besoin de tout retenir, juste piocher ce qui te plaît.

### Front (ce que l'utilisateur voit)

- **Next.js 16** : framework web moderne basé sur React, c'est ce qui fait fonctionner toutes les pages. Utilisé aussi par TikTok, Notion, OpenAI.
- **TypeScript** : version de JavaScript plus sûre, qui détecte les bugs avant qu'ils n'arrivent.
- **Tailwind CSS** : système de design qui permet de styler les éléments rapidement et de garder une cohérence visuelle.
- **Three.js** : bibliothèque pour faire de la 3D dans le navigateur, c'est ça qui fait tourner la planète Terre.
- **GSAP** + **Framer Motion** : libs d'animation, pour les transitions de page et les effets au scroll.

### Back (ce qui se passe en coulisses)

- **Python serverless function** hébergée sur Vercel. Une seule fonction qui gère tous les appels à l'IA.
- **FastAPI** : framework Python pour créer des APIs propres.
- **Anthropic Claude** (modèle Haiku 4.5) : l'IA qui rédige les recettes.
- **Spoonacular API** : base de données mondiale de recettes avec photos.
- **Pollinations.ai** : IA générative d'images en secours si Spoonacular ne trouve pas le plat.

### Hébergement

- Tout est hébergé sur **Vercel** (la même plateforme que Next.js).
- Le code source est sur **GitHub** : https://github.com/YanraSystem/nutrirecettes
- Pas de base de données traditionnelle : les recettes sont générées à la volée, le carnet personnel est stocké dans le navigateur de l'utilisateur (localStorage).

---

## 5 · Les questions probables du prof — et les réponses

### Q : "Pourquoi avoir choisi Next.js et pas un autre framework ?"

> "Next.js permet de faire un site rapide grâce à la pré-génération des pages, et il s'intègre directement avec Vercel pour l'hébergement. C'est aussi un standard de l'industrie, utilisé par des sites comme TikTok ou Notion. Pour un projet où on voulait du visuel premium, des animations, et une intégration IA simple, c'était le meilleur choix."

### Q : "C'est quoi exactement une serverless function ?"

> "C'est du code Python qui ne tourne pas en permanence sur un serveur. Il se réveille uniquement quand quelqu'un l'appelle, exécute la requête, puis se rendort. Avantage : on paye seulement quand c'est utilisé, et ça scale automatiquement si beaucoup de gens viennent en même temps."

### Q : "Comment l'IA génère la recette ?"

> "On envoie à Claude — l'IA d'Anthropic — un prompt qui contient les ingrédients cochés, la cuisine choisie, le nombre de personnes et le régime. On lui demande de répondre en JSON avec une structure précise : nom du plat, étapes, nutrition, anecdote, coût, etc. Claude est entraîné sur des milliards de documents donc il connaît la cuisine du monde, et il sait formater sa réponse comme on le demande."

### Q : "Et si l'IA invente n'importe quoi ?"

> "On encadre l'IA avec un prompt très précis qui fixe le format de réponse et donne des règles : score de compatibilité entre les ingrédients et la cuisine choisie, niveau d'authenticité Traditionnel/Adapté/Fusion. Si l'IA propose un plat fusion, elle le dit explicitement. Et on récupère les vraies photos sur Spoonacular qui est une base de données réelle, pas générée."

### Q : "C'est combien le coût d'une recette générée ?"

> "Environ 0.001 dollar par recette avec Claude Haiku 4.5. Avec 5 dollars de crédit on peut générer 5000 recettes. Spoonacular est gratuit jusqu'à 150 requêtes par jour."

### Q : "Pourquoi avoir mis une planète 3D ?"

> "C'est le côté wow visuel qui rend l'application immersive. L'idée c'est que l'utilisateur voyage à travers les cuisines du monde, donc voir la planète tourner avec les pays cliquables matérialise cette idée. Techniquement c'est du Three.js avec un shader personnalisé qui peint les continents en vert et les mers en bleu."

### Q : "Comment vous avez fait pour relier au projet de l'app sport de votre groupe ?"

> "Conceptuellement c'est lié : sport et nutrition vont ensemble, on ne peut pas progresser physiquement sans bien manger. Mais techniquement les deux apps sont autonomes, elles peuvent être consultées séparément. Dans une suite logique, on pourrait imaginer une plateforme unifiée bien-être où les deux se complètent."

### Q : "C'est responsive sur mobile ?"

> "Oui, complètement. Sur mobile la planète reste affichée mais on a ajouté un menu horizontal en bas qui liste les 19 cuisines pour qu'on puisse taper directement dessus. Sur la page de composition, les catégories d'ingrédients deviennent un slider qu'on fait défiler horizontalement, et la bottom bar est simplifiée pour gagner de la place."

### Q : "Est-ce qu'on peut sauvegarder ses recettes ?"

> "Oui, dans un carnet personnel. C'est stocké dans le navigateur de l'utilisateur — le localStorage — donc ça reste privé et ça fonctionne sans avoir besoin de créer un compte."

### Q : "Pourquoi pas de compte utilisateur, pas de base de données ?"

> "Pour rester simple et anonyme. Le carnet en localStorage couvre 90% des usages sans demander à l'utilisateur de s'inscrire. Si on voulait synchroniser entre appareils on rajouterait Supabase ou Firebase, mais ce n'était pas l'objectif du MVP."

### Q : "Combien de temps avez-vous mis ?"

> Réponds honnêtement selon votre temps réel.

---

## 6 · Si le prof pose une question pointue tech que tu ne sais pas

**Réponse type à apprendre par cœur :**

> "Cette partie-là, c'est mon collègue qui l'a développée, je peux te montrer le code source sur GitHub si tu veux, mais je ne maîtrise pas le détail technique. Ce que je sais c'est que [reformule ce que tu sais]."

Pas de honte à dire "je ne sais pas" si c'est sur du code pointu. Mieux vaut être honnête que d'inventer un truc faux.

---

## 7 · Les points forts à mettre en avant

- **Utilisation d'une vraie IA en production** (Claude d'Anthropic, modèle Haiku 4.5)
- **Architecture moderne** : Next.js 16 + serverless function Python
- **Design éditorial premium** : palette night gastronomique, typographie magazine (Cormorant Garamond + Inter)
- **3D interactive** dans le navigateur sans plugin
- **19 cuisines du monde** couvertes dont l'Algérie
- **Responsive** mobile et desktop
- **Déployé en production** sur Vercel avec URL publique
- **Code open source** sur GitHub
- **Cohérent avec le projet sport du groupe** : sport + nutrition = bien-être global

---

## 8 · Screenshots à montrer (en backup si le wifi rame)

À sauvegarder sur ton téléphone avant la présentation :

- Page d'accueil avec la planète
- Page composition avec ingrédients cochés
- Page recette générée avec la photo du plat
- Mode cuisine pas-à-pas

---

## 9 · Si on te demande "tu peux me montrer le code ?"

Va sur **https://github.com/YanraSystem/nutrirecettes** et montre :

1. Le **README** à la racine — il explique tout proprement
2. Le dossier `web/app/` — c'est là où sont les pages
3. Le fichier `web/components/Planet3D.tsx` — c'est le code de la planète 3D, c'est joli à montrer
4. Le fichier `web/api/index.py` — c'est l'API qui parle à Claude

---

## 10 · Phrase de conclusion (30 secondes)

> "NutriRecettes répond à un besoin du quotidien — quoi cuisiner avec ce qu'on a — en combinant une intelligence artificielle qui rédige les recettes, une vraie base de données de photos de plats, et une expérience visuelle premium qui donne envie de voyager culinairement. C'est aussi la moitié nutrition d'un projet plus large où l'autre partie du groupe développe le pendant sportif."

Respire, parle posément. Bonne chance.
