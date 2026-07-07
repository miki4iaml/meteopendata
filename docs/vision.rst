.. _vision:

Vision et objectifs du projet
==============================

.. contents:: Sommaire
   :local:
   :depth: 2


Pourquoi ce package existe
---------------------------

Les données météorologiques numériques opendata sont aujourd'hui accessibles
gratuitement depuis plusieurs sources de référence mondiale (ECMWF, Météo-France,
NOAA, Copernicus...). Leur exploitation dans un contexte scientifique, physique
ou technique se heurte cependant à des obstacles récurrents :

- les formats de distribution (GRIB2, NetCDF, API JSON...) sont hétérogènes
  et requièrent des bibliothèques spécialisées souvent difficiles à installer
- la disponibilité des runs varie, les serveurs sont parfois indisponibles,
  les noms de paramètres diffèrent selon les sources
- les conventions de métadonnées (coordonnées, unités, noms de variables)
  ne sont pas uniformes entre modèles
- reproduire une chaîne de collecte fiable demande un effort non trivial que
  chaque utilisateur refait de son côté

**meteopendata2netcdf** est né du besoin de disposer d'une couche de collecte
robuste, testée et partageable, qui élimine ces frictions et livre une donnée
prête à l'exploitation sous un format unique et portable : le **NetCDF conforme
aux conventions CF**.


Philosophie générale
---------------------

Le package repose sur quatre principes :

**Collect — Check — Convert — Control**
   Le cycle de traitement de chaque source est toujours le même :

   1. **Collect** — télécharger les données depuis la source opendata, en gérant
      la disponibilité des runs et les erreurs réseau
   2. **Check** — vérifier l'intégrité et la cohérence de ce qui a été reçu
      (champs attendus présents, dimensions correctes, valeurs dans les plages
      physiquement raisonnables)
   3. **Convert** — transformer la donnée brute (GRIB2, JSON...) en
      ``xr.Dataset`` normalisé avec coordonnées CF
   4. **Control** — écrire le NetCDF final avec encodage conforme aux
      conventions CF (attributs ``units``, ``long_name``, ``standard_name``,
      système de référence spatial)

**Ne pas réinventer ce qui existe**
   Plusieurs bibliothèques robustes couvrent déjà certains aspects de la
   collecte météo. En particulier :

   - `ecmwf-opendata <https://github.com/ecmwf/ecmwf-opendata>`_ gère le
     mécanisme HTTP Byte-Range vers les serveurs ECMWF open data — nous
     l'utilisons comme client de téléchargement plutôt que de le réécrire
   - `meteofetch <https://github.com/CyrilJl/meteofetch>`_ couvre les modèles
     Météo-France (AROME, ARPEGE, MFWAM) et les modèles ECMWF (IFS, AIFS) de
     manière plus exhaustive — nous ne dupliquons pas son périmètre

   Quand une bibliothèque existante couvre bien un cas d'usage, on l'encapsule
   ou on redirige vers elle. On n'ajoute de la valeur que là où il en manque :
   normalisation CF, gestion des erreurs, testabilité, documentation.

**La cible est toujours le NetCDF-CF**
   Quelle que soit la source (ECMWF, Copernicus, NOAA à terme...) et quel que
   soit le format d'entrée (GRIB2, NetCDF non normalisé, API JSON...), le
   résultat d'une collecte est toujours un fichier NetCDF dont les métadonnées
   respectent les `conventions CF <https://cfconventions.org/>`_. Ce choix
   garantit l'interopérabilité avec les outils de traitement scientifique
   (xarray, CDO, NCO, Ferret, QGIS...).

**Fiabilité avant exhaustivité**
   Mieux vaut couvrir peu de sources avec des tests complets, une gestion
   d'erreur explicite et une documentation à jour, que de couvrir beaucoup de
   sources de manière fragile. La version 1.0 sera publiée quand le périmètre
   ECMWF sera jugé solide et complet, pas avant.


Périmètre couvert par version
------------------------------

Version 0.x (bêta — en cours)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Source : **ECMWF open data** uniquement, via ``ecmwf-opendata``
- Modèle : **IFS HRES oper** (runs 00Z et 12Z, résolution 0.25°)
- Paramètres de surface : température 2 m, point de rosée 2 m, vent 10 m
- Échéances : 0 à 72 h par pas de 6 h
- Format de sortie : GRIB2 (intermédiaire) + ``xr.Dataset`` en mémoire + NetCDF
- L'API publique peut évoluer entre versions mineures

Objectifs pour la version 1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les points suivants constituent la cible pour la première version stable.
Ils seront traités progressivement dans les versions 0.x :

- **Couverture ECMWF étendue** : paramètres sur plusieurs niveaux de pression,
  niveaux modèles, variables d'accumulation (précipitations, rayonnement)
- **Support du modèle AIFS** (modèle data-driven ECMWF, stream ``oper``)
- **Support des prévisions d'ensemble ECMWF (ENFO)** avec gestion de la
  dimension ``number`` (50 membres)
- **Vérification de cohérence physique** automatique après conversion
  (bornes de température, vents, humidité relative dans [0, 100] %)
- **Mise en cache locale** des fichiers GRIB2 pour éviter les téléchargements
  redondants entre appels successifs
- **Documentation complète** de toutes les sources avec exemples reproductibles
- **Couverture de tests >= 90 %** sur l'ensemble du code

Versions 1.x (au-delà)
~~~~~~~~~~~~~~~~~~~~~~~~

- Intégration d'autres sources opendata (Copernicus CDS, NOAA GFS open data,
  Météo-France si non couvert par meteofetch)
- Interface de requête unifiée indépendante de la source
- Exports vers d'autres formats (Zarr, Parquet pour les séries temporelles)


Relation avec meteofetch
-------------------------

`meteofetch <https://github.com/CyrilJl/meteofetch>`_ et
**meteopendata2netcdf** sont **complémentaires** et partagent une origine
commune. Le tableau suivant clarifie quand utiliser l'un ou l'autre :

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Besoin
     - Outil recommandé
     - Raison
   * - Données AROME, ARPEGE ou MFWAM (Météo-France)
     - meteofetch
     - Couverture native, non dupliquée ici
   * - Run IFS ou AIFS complet (toutes variables)
     - meteofetch
     - Téléchargement GRIB complet plus efficace
   * - Quelques paramètres IFS sur 0-72 h avec export NetCDF-CF
     - meteopendata2netcdf
     - Byte-Range + normalisation CF automatique
   * - Prévisions d'ensemble ECMWF (ENFO)
     - meteopendata2netcdf (v1.0)
     - Objectif de la roadmap

Les deux projets peuvent être utilisés conjointement dans une même chaîne de
traitement sans conflit.


Public cible
-------------

Ce package s'adresse principalement à :

- des **physiciens, ingénieurs et scientifiques** qui ont besoin de forcer des
  modèles (hydrauliques, thermiques, structurels, agricoles...) avec des données
  météo de réanalyse ou de prévision
- des **développeurs** qui construisent des pipelines de traitement de données
  climatiques ou météorologiques et cherchent une couche de collecte fiable et
  testée
- des **contributeurs** qui souhaitent ajouter le support d'une nouvelle source
  opendata en bénéficiant de l'infrastructure de test et de publication existante
