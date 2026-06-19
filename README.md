# L'expension ottomane dans les balkans (1354-1683)
**Projet personnel - Data Science - Université de Neuchâtel - 2026**
---

## 1. Question de recherche

Comment l'expension militaire ottoman dans les balkans a-t-elle progressé géographiquement et temporellement, et quelles différences observe-t-on d'un sultant à l'autre ?

Cette question fait partie du domaine de l'histoire médiévale et moderne. Son but est d'aller plus loin qu'une narration évenementielle pour adopter une perspective quantitative : mesurer des tendances - l'intensité militaire par règne, les guerres traversant plusieurs sultans - plûtot que de décrire les batailles une par une. L'objectif est de voir si les données confirment une expension linéaire ou montrent à l'inverse des phases d'accélération et de rupture liées aux individus.

La période traité, 1354- 1683, correspond aux premières incursions ottomanes en Europe jusqu'au siège de Vienne, moment dans l'histoire qui marque le début du recul ottoman dans les Balkans.

---

## 2. Nature et choix des données

### Source

Les données ont été extraites de **Wikidata**, une base de connaissance open-source et collaborative du projet Wikimedia (licence CC0). Wikidata structure ses données sous forme de triplets RDF interrogables via le langage SPARQL. L'extraction a été effectuer sur le site web https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service à l'aide d'une requête SPARQL puis a été extraite sous forme CSV.

### Corpus brute

Le corpus brut contient **260 entrée**, chacune correspondant à une bataille. Le filtre géographique appliqué dans la requête SPARQL vise la péninsule balkanique (latitude 35-48°N, longitude 13-30°E).
L'attribution de chaque bataille à un sultan à été réalisée automatiquement en comparant la date de la bataille aux dates de règne définies dans l'extracteur.

### Colonnes du jeu de donées

Chaque entrée contient les champs suivant : nom de la bataille ("battleLabel"), date ("date"), précision de la date ("date_precision"), lieu ("locationLabel"), coordonnées géographiques ("lat", "lon"), sultant régnant ("sultan"), identification Wikidata du sultan ("sultan_wikidata"), conflit ou gueurre associé ("part_ofLabel"), et le lien vers l'entité Wikidata ("wikidata_url").

### Représentativité

Wikidata est une base collaborative dont la couverture n'est pas uniforme : Les battaile détailées et documentées sont surreprésentées alors que certains conflits mineurs sont absents. Le corpus reflète d'avantage l'état de la documentation historique que l'activité militaire réelle. Ce biais doit être pris en compte dans l'interprétation.

---

## 3. Traitement des données

Le nettoyage a été réalisé en python avec le script 'clean_ottoman_battles.py', sans bibliothèques externes - uniquement les modules standards 'csv', 'collections' et 'pathlib'. Le script comporte six étapes successives.

**Etape 1 - Résolution des labels non résolus.** Wikidata retourne parfois un identifiant brut (QID) sans libellé anglais. Un dictionnaire de correction manuelles ('LABEL_FIXES') remplace ces QID par leurs noms correctes.

**Etape  2 - Filtre périmètre.** Le filtre géographique SPARQL capture parfois des batailles sans lien ottoman (guerre véniciennes, conflits argonais). Une liste noire ('OUT_OF_SCOPE_WARS') les excluts si aucun mot-clé ottoman n'apparait dans leurs champs.

**Etape 3 - Déduplication.** Une bataille peut apparaître plusieurs fois si associée à plusieurs lieux ou conflits. Les lignes sont groupées par '(wikidata_url, date)' : le lieu le plus spécifique est conservé et les conflits parents sont fusionnés.

**Etape 4 - Résolution des conflits de dates.** Lorsqu'une bataille possède une date approximative ('YYYY-01-01') et une date précise, seule la précise est conservée. Plusieurs dates précises distinctes indiquent des événements différents - toutes sont conservées.

**Etape 5 - Ajout de 'date_precision'.** Une colonne explicite ('year' / 'month' / 'day') est ajoutée : 89 bataille au jour (45%), 87 à l'année (44%), 22 au mois (11%).

**Etape 6 - Harmonisation des noms de guerres.** Un dictionnaire ('WAR_HARMONISATION') normalise les variantes de libellés vers une forme canonique unique, évitant les doublons dans le réseau.

A l'issue de ces six étapes, le corpus passe de **260 à 198 entrées valides**, soit une réduction de 62 ligne (24 %).

---

## 4. Analyse et visualisations

### Analyse A - Distribution temporelle des batailles par sultant

La première analyse quantifie l'intensité militaire de chaque règne. deux visualisation ont été faites avec Matplotlib : un barplot du nombre de batailles par sultan dans l'ordre chronologique, et une courbe cumulative des batailles dans le temps avec les zones de règne colorés en fond.

Le barplot montre des différences marquées : Avec Mehmed II qui occupe 17 % du corpus avec 34 batailles, suivi de Mehmed IV (25) et Soliman Ier (22). La courbe cumulative confirme ces tendances : la pente s'accentue sous les sultans à qui ont beaucoup bataillé nottament avec Mehmed II (1451-1481) où se trouve le pic de l'expansion ottomane. Les sultans à règne court n'ont en général pas beaucoup participé aux conflits apparaissent comme un plateau visible, marquant une rupture dans la progression.

### Analyse B - Réseau sultant <-> conflits

La seconde analyse construit un graphe bipartite qui relie chaque sultan aux conflits ('part_ofLabel') dans lequels il a participé.
Réalisée avec NetworkX et Matplotlib, elle prend 168 sur les 198 entrées disposant d'un conflit associé, formant un réseau de 69 noeuds et 78 arêtes. La taille des noeuds est proportionnelle au nombre de batailles; l'épaisseur des arêtes correspond au nombre de batailles partagées.

Le réseau met en évidence les conflits traversant les sultans : les *Ottoman Wars in Europe* constituent le noeud le plus connecté, reliant de nombreux sultans sur toute la période. Certains conflit sont en revanche limités à un seul règne. L'analyse montre ainsi que l'expansion ottomane est une continuité de conflits partagés entre plusieurs règnes, ce qui nuance l'idée d'une expansion portée uniquement par des individus.

Les deux analyses sont reproductibles à partir des scripts du dossier technique et documentées sur le [site du projet](https://momobendo06.github.io/ottoman-blakans/)

---

#Données : Wikidata (CC0) - Outils : python 3.13, Matplotlib, NetworkX - Date de collecte avril 2026*