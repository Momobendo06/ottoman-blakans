# L'expension ottomane dans les balkans (1354-1683)
**Projet personnel - Data Science - Université de Neuchâtel - 2026**

---

## 1. Question de recherche

Comment l'expension militaire ottomane dans les Balkans a-t-elle progressé géographiquement et temporellement, et quelles différences observe-t-on d'un sultan à l'autre ?

Cette question s'inscrit dans le domaine de l'histoire mediévale et moderne. Elle vise à aller plus loin qu'une narration événementielle pour adopter une perspective quantitative : mesurer des tendances - l'intensité militaire par règne, les guerres traversant plusieurs sultants - plûtot que de décrire les batailles une par une. Le but est de voir si les données confirment une expansion linéaire ou révèlent des phases d'accélération et de rupture liées aux individus.

La période retenue, 1354 - 1683, correspond aux premières incursions ottomanes en Europe jusqu'au siège de Vienne, moment généralement considéré comme le début du recul ottoman dans les Balkans.

---

## 2. Nature et choix des données

### Source

Les données ont été extraites de **Wikidata**, la base de connaissance libre et collaborative du projet Wikimedia (licence CC0). Wikidata structure ses données sous forme de triplets RDF interrogables via le langage SPARQL. L'extraction a été effectuer sur le site web https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service à l'aide d'une requête SPARQL puis a été extraite sous forme CSV.

### Corpus brute

Le corpus brut contient **260 entrée**, chacune correspondant é une bataille. Le filtre géographique appliqué dans la requête SPARQL vise la péninsule balkanique (latitude 35-48°N, longitude 13-30°E).
L'attribution de chaque bataille à un sultan à été réalisée automatiquement en comparant la date de la bataille aux dates de règne définies dans l'extracteur.

### Colonnes du jeu de donées

Chaque entrée contient les champs suivant : nom de la bataille ("battleLabel"), date ("date"), précision de la date ("date_precision"), lieu ("locationLabel"), coordonnées géographiques ("lat", "lon"), sultant régnant ("sultan"), identification Wikidata du sultan ("sultan_wikidata"), conflit ou gueurre associé ("part_ofLabel"), et le lien vers l'entité Wikidata ("wikidata_url").

### Représentativité

Wikidata est une base collaborative dont la couverture n'est pas uniforme : les batailles bien documentées y sont surreprésentées, tandis que certains conflits mineurs sont absents. Le corpus reflète d'avantage l'état de la documentation historique que l'activité militaire réelle. Ce biais doit être pris en compte dans l'interprétation.

---

## 3. Traitement des données

Le nettoyage a été réalisé en python avec le script 'clean_ottoman_battles.py', sans bibliothèques externes - uniquement les modules standards 'csv', 'collections' et 'pathlib'. Le pipeline comporte six étapes successives.

**Etape 1 - Résolution des labels non résolus.** Wikidata retourne parfois un identifiant brut (QID) sans libellé anglais. Un dictionnaire de correction manuelles ('LABEL_FIXES') remplace ces QID par leurs noms correctes.

**Etape  2 - Filtre périmètre.** Le filtre géographique SPARQL capture parfois des batailles sans lien ottoman (guerre véniciennes, conflits argonais). Une liste noire ('OUT_OF_SCOPE_WARS') les excluts si aucun mot-clé ottoman n'apparait dans leurs champs.

**Etape 3 - Déduplication.** Une bataille peut apparaître plusieurs fois si associée à plusieurs lieux ou conflits. Les lignes sont groupées par '(wikidata_url, date)' : le lieu le plus spécifique est conservé et les conflits parents sont fusionnés.

**Etape 4 - Résolution des conflits de dates.** Lorsqu'une bataille possède une date approximative ('YYYY-01-01') et une date précise, seule la précise est conservée. Plusieurs dates précises distinctes indiquent des événements différents - toutes sont conservées.

**Etape 5 - Ajout de 'date_precision'.** Une colonne explicite ('year' / 'month' / 'day') est ajoutée : 89 bataille au jour (45%), 87 à l'année (44%), 22 au mois (11%).

**Etape 6 - Harmonisation des noms de guerres.** Un dictionnaire ('WAR_HARMONISATION') normalise les variantes de libellés vers une forme canonique unique, évitant les doublons dans le réseau.

A l'issue de ces six étapes, le corpus pas de **260 à 198 entrées valides**, soit une réduction de 62 ligne (24 %).

---

## 4. Analyse et visualisations

### Analyse A - Distribution temporelle des batailles par sultant

La première analyse qauntifie l'intensité militaire de chaque règne. Deux visualisation ont été produites avec MAtplotlib : un barplot du nombre de batailles par sultant dans l'ordre chronologique, et une courbe cumulative des batailles dans le temps avec les zones de règne colorées en arrière-plan.

Le barplot révèle des différences marquées : Mehmed II domine avec 34 batailles (17% du corpus), suivi de Mehmed IV (25) et Soliman Ier (22). La courbe cumulative confirme ces tendances : la pente s'accentue sous Mehmed II (1451-1481), révèlant le pic de l'expansion balkanique. L'interrègne (1402-1413) apparaît comme un plateau visible, marquant une rupture dans la progression.

### Analyse B - Réseau sultant <-> conflits

La seconde analyse construit un graphe bipartite reliant chaque sultant aux conflits (0part_ofLabel') dans lequels il a participé. Réalisée avec NetworkX et Matplotlib, elle porte sur 168 des 198 entrées disposant d'un conflit associé, formant un réseau de 69 noeuds et 78 arêtes. La taille des noeuds est proportionnelle au nombre de batailles ; l'épaisseur des arêtes reflète le nombre de batailles partagées.

Le réseau met en évidence les conflits transrégnaux : les *Ottoman Wars in Europe* constituent le noeud le plus connecté, reliant de nombreux sultants sur toute la période. Certains conflits sont en revanche limités à un seul règne. L'analyse révèle ainsi que l'expension ottomane est un enchevêtrement de conflits durables traversant plusieurs règnes, ce qui nuance l'idée d'une expension portée uniquement par des individus.

Les deux analyses sont reproductibles à partir des scripts du dossier technique et documentées sur le [site du projet](https://momobendo06.github.io/ottoman-blakans/)

---

#Données : Wikidata (CC0) - Outils : python 3.13, Matplotlib, NetworkX - Date de collecte avril 2026*
