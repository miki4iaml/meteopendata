.. _design:

Architecture et choix de conception
====================================

Ce document retrace l'ensemble des décisions d'architecture, de conception et
d'outillage prises lors du développement de **meteopendata2netcdf**. Il sert à
la fois de guide d'*onboarding* pour les nouveaux contributeurs et de référence
technique pour comprendre pourquoi le code est structuré comme il l'est.

.. contents:: Sommaire
   :local:
   :depth: 2


Contexte et objectif
--------------------

**meteopendata2netcdf** est un package Python qui permet de récupérer les
prévisions de surface du modèle IFS de l'ECMWF (température 2 m, point de
rosée 2 m, vent 10 m) depuis l'API publique `ecmwf-opendata
<https://github.com/ecmwf/ecmwf-opendata>`_, et de les exporter en NetCDF
conforme aux conventions CF.

Le package est né d'une conversation de conception itérative qui a également
produit `meteofetch <https://github.com/CyrilJl/meteofetch>`_, un package plus
généraliste couvrant les modèles Météo-France (AROME, ARPEGE, MFWAM) et les
modèles ECMWF (IFS, AIFS). Les deux packages ciblent les mêmes serveurs ECMWF
mais avec des philosophies différentes — voir :ref:`comparison-meteofetch`.


.. _comparison-meteofetch:

Comparaison avec meteofetch
----------------------------

Contrairement à **meteofetch** qui télécharge les fichiers GRIB2 complets et
les lit localement, **meteopendata2netcdf** s'appuie sur le mécanisme HTTP
**Byte-Range** fourni par ``ecmwf-opendata`` : pour chaque échéance, seuls les
octets correspondant aux paramètres demandés sont transférés depuis le fichier
GRIB2 distant, grâce aux fichiers d'index ``.index`` publiés par l'ECMWF aux
côtés des fichiers GRIB.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Critère
     - meteopendata2netcdf
     - meteofetch
   * - Mécanisme de téléchargement
     - HTTP Byte-Range (index ECMWF)
     - Fichiers GRIB2 complets
   * - Modèles couverts
     - IFS HRES oper
     - IFS, AIFS, AROME, ARPEGE, MFWAM
   * - Format de sortie
     - GRIB2 + ``xr.Dataset`` + NetCDF
     - ``xr.DataArray`` CF uniquement
   * - Sources de données
     - ECMWF, AWS, Azure, Google
     - ECMWF direct uniquement
   * - Dépendances obligatoires
     - ecmwf-opendata, cfgrib, xarray, netCDF4
     - cfgrib, xarray, requests

Le Byte-Range est avantageux quand on ne veut qu'une poignée de paramètres sur
beaucoup d'échéances. Si la majorité des champs d'un fichier est nécessaire,
télécharger le fichier complet (comme meteofetch) est plus efficace.


Paramètres et domaine couvert
-------------------------------

Les quatre paramètres retenus couvrent les besoins météorologiques de surface
les plus courants :

.. list-table::
   :header-rows: 1
   :widths: 15 35 15 15

   * - Nom court
     - Description
     - Unité
     - Hauteur
   * - ``2t``
     - Température à 2 mètres
     - K
     - 2 m
   * - ``2d``
     - Point de rosée à 2 mètres (proxy humidité)
     - K
     - 2 m
   * - ``10u``
     - Composante U du vent à 10 mètres
     - m s⁻¹
     - 10 m
   * - ``10v``
     - Composante V du vent à 10 mètres
     - m s⁻¹
     - 10 m

Le point de rosée (``2d``) a été préféré à l'humidité relative (``r``) car
il est directement disponible en surface sur les serveurs ECMWF open data, et
la conversion Td → RH est triviale si besoin. Les échéances vont de 0 à 72 h
par pas de 6 h, ce qui correspond aux runs ``00Z`` et ``12Z`` du stream
``oper`` (HRES). Les runs ``06Z`` et ``18Z`` (stream ``scda``) ne couvrent que
jusqu'à 90 h mais avec une disponibilité et une résolution temporelle
différentes — ils ne sont pas couverts dans cette version.


Architecture du package
------------------------

Structure des fichiers source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le package adopte le layout ``src/`` (PEP 517), qui isole le code installable
du reste du dépôt et évite les imports accidentels du répertoire courant lors
des tests::

    src/meteopendata2netcdf/
    ├── __init__.py       API publique + __version__ via importlib.metadata
    ├── _constants.py     Constantes ECMWF (params, steps, model strings)
    ├── _exceptions.py    DownloadError, DatasetBuildError
    ├── _grib.py          Lecture et fusion multi-groupes des fichiers GRIB2
    ├── _downloader.py    IFSSurfaceDownloader + DownloadResult
    ├── _cli.py           Point d'entrée CLI (argparse)
    └── py.typed          Marqueur PEP 561 (package annoté)

Les modules préfixés par ``_`` sont internes et ne font pas partie de l'API
publique. Seuls les symboles listés dans ``__all__`` dans ``__init__.py``
sont garantis stables entre versions mineures.

Séparation des responsabilités
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chaque module a une responsabilité unique et clairement délimitée :

- **``_constants.py``** — source de vérité unique pour toutes les valeurs
  ECMWF. Tout ce qui est "magique" (noms de paramètres, heures de run valides,
  résolution) vit ici. Cela permet de modifier la configuration sans toucher
  à la logique.

- **``_exceptions.py``** — hiérarchie d'exceptions propre. ``DownloadError``
  et ``DatasetBuildError`` héritent de ``RuntimeError`` (pas de ``Exception``)
  pour signaler qu'elles représentent des échecs d'exécution non récupérables
  dans le flux normal, tout en restant attrapables par un ``except Exception``.

- **``_grib.py``** — isolation du problème spécifique de la lecture GRIB2
  multi-groupes (voir :ref:`grib-multigroup`). Cette séparation permet de
  tester la logique de fusion indépendamment du téléchargement.

- **``_downloader.py``** — orchestre le cycle complet : détection du run,
  construction des URLs, téléchargement, lecture. Contient ``DownloadResult``,
  un dataclass qui encapsule tous les résultats et expose ``to_netcdf()``
  comme méthode de convenance.

- **``_cli.py``** — couche mince au-dessus de ``_downloader.py``. Contient
  uniquement la logique argparse et la gestion des codes de retour. Aucune
  logique métier ne vit ici.


.. _grib-multigroup:

Le problème des groupes GRIB multiples
----------------------------------------

C'est le principal défi technique du package, découvert lors des premiers
tests d'intégration.

Les quatre paramètres demandés se répartissent sur **deux hauteurs** dans les
fichiers GRIB2 IFS :

- ``heightAboveGround = 2 m`` → ``t2m``, ``d2m``
- ``heightAboveGround = 10 m`` → ``u10``, ``v10``

``cfgrib`` groupe les messages GRIB par valeur de coordonnée scalaire. Quand
``xr.open_dataset()`` (backend cfgrib) tente de fusionner les deux groupes,
il rencontre un conflit sur la coordonnée ``heightAboveGround`` (deux valeurs
différentes pour la même coordonnée scalaire) et lève une
``DatasetBuildError``, abandonnant silencieusement les variables du groupe
en conflit (``t2m`` et ``d2m``).

**Solution retenue** : utiliser ``cfgrib.open_datasets()`` (pluriel), qui
retourne une liste de Datasets cohérents — un par groupe de hauteur. La
fonction ``load_surface_dataset()`` dans ``_grib.py`` :

1. Appelle ``cfgrib.open_datasets()``
2. Trie chaque groupe par ``valid_time`` croissant
3. Stocke la hauteur d'origine dans ``ds[var].attrs["height_m"]`` pour la
   traçabilité
4. Supprime la coordonnée scalaire ``heightAboveGround`` de chaque groupe
5. Fusionne tous les groupes avec ``xr.merge(compat="override")``

Cette approche est robuste à l'ajout de futurs paramètres à des hauteurs
différentes (ex. ``100u``, ``100v`` à 100 m).


Coordonnées temporelles : ``np.datetime64`` obligatoire
--------------------------------------------------------

``xr.Dataset.to_netcdf()`` ne sait pas sérialiser des objets ``datetime``
Python timezone-aware (``datetime(..., tzinfo=timezone.utc)``) — il lève
``ValueError: unable to infer dtype on variable 'valid_time'``.

**Règle** : toute coordonnée temporelle dans le code de production et dans les
tests doit utiliser ``np.datetime64`` (dtype ``"datetime64[ns]"``), qui est le
format natif attendu par le backend NetCDF4. Cette contrainte s'applique aussi
aux fixtures de test — c'est pourquoi ``_make_fake_dataset()`` utilise
``np.array([...], dtype="datetime64[ns]")``.


Choix du build system
----------------------

Le build system est **setuptools** avec ``setuptools.build_meta`` comme
backend PEP 517. Ce choix a été motivé par :

- **Universalité** : ``setuptools.build_meta`` est disponible depuis
  setuptools 40 et fonctionne dans tous les environnements (y compris les
  notebooks hébergés qui verrouillent leurs versions de dépendances).
- **Absence de setuptools-scm** : la version est déclarée statiquement dans
  ``pyproject.toml``. La gestion dynamique de version via git tags aurait
  introduit une dépendance supplémentaire sans bénéfice à ce stade.

.. note::

   ``setuptools.backends.legacy:build``, backend alternatif présent dans
   setuptools >= 69, a été testé et rejeté car il n'est pas disponible dans
   les environnements qui verrouillent setuptools à une version antérieure.
   **Ne pas réintroduire ce backend.**


Chaîne d'outillage qualité
----------------------------

Linting et formatage : ruff
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ruff** remplace flake8 + isort + pyupgrade + plusieurs plugins en un seul
outil, avec une vitesse d'exécution sans comparaison (Rust). Les règles
activées sont :

.. list-table::
   :header-rows: 1
   :widths: 10 20 70

   * - Code
     - Origine
     - Rôle
   * - ``E``, ``W``
     - pycodestyle
     - Style PEP 8 de base
   * - ``F``
     - pyflakes
     - Imports inutilisés, variables non définies
   * - ``I``
     - isort
     - Ordre et groupement des imports
   * - ``UP``
     - pyupgrade
     - Syntaxe Python moderne (``X | Y`` au lieu de ``Optional[X]``, etc.)
   * - ``B``
     - flake8-bugbear
     - Bugs subtils et mauvaises pratiques
   * - ``C4``
     - flake8-comprehensions
     - Compréhensions inutilement verbeuses
   * - ``ANN``
     - flake8-annotations
     - Annotations de type manquantes sur les fonctions publiques
   * - ``N``
     - pep8-naming
     - Conventions de nommage PEP 8
   * - ``RUF``
     - ruff-specific
     - Règles propres à ruff (dont RUF001 : caractères Unicode ambigus)

**Exceptions configurées** :

- ``ANN401`` (``**kwargs: Any``) : ignoré globalement car légitime pour les
  méthodes wrapper de bibliothèques tierces (``to_netcdf``).
- ``ANN``, ``S101`` : ignorés dans ``tests/**`` — les fonctions de test
  n'ont pas besoin d'annotations de retour et peuvent utiliser ``assert``.

.. warning::

   La règle **RUF001** détecte les caractères Unicode visuellement similaires
   aux opérateurs ASCII. En particulier, le tiret demi-cadratin ``–``
   (U+2013, EN DASH) est interdit dans les chaînes de code car il est
   indiscernable du trait d'union ``-`` (U+002D) mais n'est pas reconnu
   comme opérateur. Utiliser systématiquement le trait d'union ASCII.

Vérification de types : mypy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mypy est configuré en mode ``strict``, ce qui impose notamment :

- Annotations sur toutes les fonctions et méthodes publiques
- Interdiction de ``Any`` implicite (``disallow_implicit_optional``)
- ``warn_return_any`` : interdit de retourner ``Any`` sans annotation explicite

Les packages tiers sans stubs (``cfgrib``, ``ecmwf-opendata``) sont exemptés
via ``[[tool.mypy.overrides]]`` ciblés — plus précis qu'un
``ignore_missing_imports = true`` global qui masquerait les erreurs sur les
autres imports.

Tests : pytest + pytest-cov
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

La stratégie de test repose sur l'**isolation totale du réseau** : aucun test
ne télécharge de données réelles. Les dépendances externes sont toutes
mockées :

- ``ecmwf.opendata.Client`` → ``unittest.mock.MagicMock``
- ``cfgrib.open_datasets`` → ``unittest.mock.patch`` retournant des
  ``xr.Dataset`` synthétiques construits en mémoire avec NumPy

Les tests qui nécessitent une connexion réseau réelle (intégration end-to-end)
sont marqués ``@pytest.mark.network`` et exclus par défaut (``-m "not
network"``). Ils peuvent être lancés ponctuellement avec
``pytest -m network``.

La couverture minimale est fixée à **80 %** (``fail_under = 80`` dans
``[tool.coverage.report]``). Le module ``_cli.py`` est exclu de la mesure de
couverture car son point d'entrée ``if __name__ == "__main__"`` n'est pas
testable en isolation sans subprocess.


CI/CD : GitHub Actions
-----------------------

Le pipeline CI est constitué de deux workflows distincts.

Workflow ``ci.yml``
~~~~~~~~~~~~~~~~~~~~

Déclenché sur chaque push sur ``main`` et chaque pull request vers ``main``.
Structure en trois jobs séquentiels :

1. **lint** (Ubuntu, Python 3.12) — ``ruff check`` + ``ruff format --check``
   + ``mypy``. Job le plus rapide, bloque les deux suivants en cas d'échec.

2. **test** — matrice 3 OS × 2 versions Python (6 combinaisons) :

   .. list-table::
      :header-rows: 1

      * - OS
        - Python 3.12
        - Python 3.13
      * - ubuntu-latest
        - ✓
        - ✓
      * - windows-latest
        - ✓
        - ✓
      * - macos-latest
        - ✓
        - ✓

   ``libeccodes-dev`` est installé via ``apt-get`` sur Linux et ``brew`` sur
   macOS. Sur Windows, eccodes est inclus dans la wheel cfgrib — aucune action
   nécessaire.

3. **build** — ``python -m build`` + ``twine check --strict``. Valide que la
   distribution est conforme aux attentes de PyPI avant tout upload.

Workflow ``publish.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~

Déclenché par trois événements :

- ``push: tags: ["v*.*.*"]`` — workflow en ligne de commande
- ``release: types: [published]`` — création de release depuis l'IHM GitHub
- ``workflow_dispatch`` — déclenchement manuel depuis l'onglet Actions

Le workflow utilise le **Trusted Publishing OIDC** de PyPI : aucun token API
n'est stocké dans les secrets GitHub. PyPI émet un token de courte durée via
OIDC lors de l'exécution du workflow, éliminant le risque de fuite de
credentials. Un environnement GitHub ``pypi`` est configuré avec une règle
de protection sur les tags ``v*.*.*``.

.. note::

   **Piège rencontré** : la création d'une release via l'IHM GitHub ne
   déclenche pas l'événement ``push: tags`` mais l'événement
   ``release: published``. Si seul ``push: tags`` est configuré dans
   ``publish.yml``, le workflow ne se déclenche pas. Les deux déclencheurs
   doivent être présents, ainsi que ``workflow_dispatch`` pour les
   re-déclenchements manuels.


Documentation : Sphinx + Read the Docs
----------------------------------------

La documentation est générée par **Sphinx** avec le thème ``sphinx-rtd-theme``
et hébergée sur **Read the Docs**. Extensions activées :

- ``sphinx.ext.autodoc`` — génère la documentation API depuis les docstrings
- ``sphinx.ext.napoleon`` — support des docstrings style Google (utilisé dans
  tout le code)
- ``sphinx.ext.viewcode`` — liens ``[source]`` dans la documentation API
- ``sphinx.ext.intersphinx`` — liens croisés vers Python, xarray, NumPy
- ``sphinx_autodoc_typehints`` — affichage des types dans les signatures
- ``myst_parser`` — support Markdown pour les fichiers ``.md`` (README, etc.)

Le fichier ``.readthedocs.yaml`` configure le build sur Ubuntu 24.04 avec
Python 3.12 et installe le package avec les extras ``[docs]``.


Convention de versionnage
--------------------------

Le projet suit **PEP 440** et **Semantic Versioning** adapté :

- ``0.x.yb0`` — versions beta (développement actif, API susceptible de changer)
- ``0.x.y`` — versions stables (rétrocompatibilité garantie dans le minor)
- ``1.0.0`` — première version stable avec API figée

La version est déclarée statiquement dans ``pyproject.toml`` (champ
``version``). Elle doit être incrémentée manuellement avant chaque tag de
release. **PyPI refuse catégoriquement le re-upload d'une version existante**
— vérifier que la version est bien incrémentée avant de pousser un tag.


Décisions en suspens et pistes d'évolution
-------------------------------------------

Les points suivants ont été identifiés mais non implémentés dans la version
actuelle :

**Vérification d'intégrité MD5**
   ``ecmwf-opendata`` ne publie pas de checksums MD5/SHA256 pour ses fichiers.
   Une vérification de la taille du fichier après téléchargement pourrait
   constituer un garde-fou minimal.

**Support de l'ensemble (ENFO)**
   Le stream ``enfo`` (ensemble de prévisions, 50 membres) est disponible via
   ``ecmwf-opendata`` mais nécessite une gestion spécifique des dimensions
   (ajout d'une dimension ``number``). Non couvert dans cette version.

**Support d'AIFS**
   Le modèle data-driven AIFS de l'ECMWF est accessible via le même mécanisme.
   Son intégration nécessite un stream différent (``oper`` également, mais avec
   ``model="aifs"``).

**Mise en cache locale**
   Actuellement, deux appels successifs avec les mêmes paramètres téléchargent
   deux fois les mêmes données. Un mécanisme de cache basé sur le nom du
   fichier GRIB2 (qui encode la date et l'heure du run) permettrait d'éviter
   les téléchargements redondants.

**Conversion de coordonnées**
   Le package retourne les températures en Kelvin (format natif ECMWF). Une
   option de conversion automatique K → °C pourrait améliorer l'ergonomie
   pour les utilisateurs non-météorologues.


.. seealso::

   Le guide complet du contributeur (branches, CI, publication, ajout d'une
   source) est documenté dans :ref:`contributing`.
