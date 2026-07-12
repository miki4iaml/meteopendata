.. _contributing:

Guide du contributeur
======================

Ce guide explique pas à pas comment contribuer à **meteopendata2netcdf**,
de la création d'une branche de travail jusqu'à la publication d'une nouvelle
version sur PyPI, en passant par la CI, les tests et la documentation.

Il s'adresse à toute personne souhaitant corriger un bug, ajouter une
fonctionnalité ou intégrer une nouvelle source de données.

.. contents:: Sommaire
   :local:
   :depth: 2


Prérequis
---------

Avant de commencer, assurez-vous d'avoir :

- **Python >= 3.12** installé (vérifiez avec ``python --version``)
- **git** installé
- **eccodes** installé sur votre système (requis par ``cfgrib``) :

  .. code-block:: bash

      # Linux (Debian/Ubuntu)
      sudo apt-get install libeccodes-dev

      # macOS
      brew install eccodes

      # Windows : inclus dans la wheel cfgrib, aucune action supplémentaire

- Un compte **GitHub** avec accès en écriture au dépôt
  (ou un fork si vous n'êtes pas encore collaborateur)

Clonage et installation
------------------------

.. code-block:: bash

    # Cloner le dépôt
    git clone https://github.com/miki4iaml/meteopendata.git
    cd meteopendata

    # Installer le package en mode éditable avec tous les extras
    pip install -e ".[dev,docs]"

    # Vérifier que l'installation est fonctionnelle
    python -c "import meteopendata2netcdf; print(meteopendata2netcdf.__version__)"

    # Vérifier que la suite de tests passe
    pytest -m "not network"


Stratégie de branches
----------------------

Le projet utilise un modèle de branches structuré pour s'intégrer proprement
avec PyPI et Read the Docs.

Vue d'ensemble
~~~~~~~~~~~~~~

.. code-block:: text

    main          ← branche de référence (toujours stable, toujours publiable)
    │
    ├── develop   ← intégration des features avant merge sur main
    │   ├── feature/nom-de-la-feature
    │   ├── fix/description-du-bug
    │   └── docs/description-de-la-doc
    │
    └── (tags)    ← v0.2b0, v0.3b0, ..., v1.0.0, v1.1.0, ...

Description de chaque branche
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**``main``**
   La branche de production. Tout ce qui est sur ``main`` est publié sur PyPI
   et correspond à la version ``latest`` sur Read the Docs. On n'y pousse
   jamais directement (hors corrections critiques). Chaque merge sur ``main``
   provient d'une pull request validée avec CI verte.

**``develop``**
   La branche d'intégration. Les features et corrections sont mergées ici
   en premier. Quand ``develop`` est stable et que l'on veut préparer une
   release, on merge ``develop`` sur ``main``.

**``feature/*``**, **``fix/*``**, **``docs/*``**
   Branches de travail éphémères, créées depuis ``develop``, supprimées
   après merge. Exemples :

   - ``feature/aifs-support`` — ajout du support du modèle AIFS
   - ``fix/grib-multigroup-windows`` — correction d'un bug Windows
   - ``docs/ecmwf-source-page`` — rédaction d'une page de documentation

Intégration avec Read the Docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Read the Docs construit automatiquement plusieurs versions de la documentation :

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Version RTD
     - Branche/tag correspondant
     - Quand la configurer
   * - ``latest``
     - ``main``
     - Automatique (défaut RTD)
   * - ``stable``
     - Dernier tag ``vX.Y.Z`` sans suffixe ``b``
     - Automatique dès la v1.0.0
   * - ``v0.2b0``, ``v0.3b0``...
     - Tags correspondants
     - Activer dans RTD → Versions → Activer
   * - ``v1``, ``v2``...
     - Branches ``v1``, ``v2`` (créées manuellement)
     - À partir de la v1.0.0

Pour activer une version de doc sur RTD : aller dans l'interface Read the Docs
→ **Versions** → cocher la version souhaitée → **Save**.

.. tip::

   Pendant la phase bêta (0.x), seules ``latest`` (= ``main``) et les tags
   de release sont utiles. Les branches ``v1``, ``v2``... n'ont de sens qu'à
   partir de la version 1.0.


Cycle de vie d'une contribution
---------------------------------

Étape 1 — Créer sa branche de travail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Toujours partir depuis ``develop`` à jour :

.. code-block:: bash

    # Se placer sur develop et la mettre à jour
    git checkout develop
    git pull origin develop

    # Créer et basculer sur la nouvelle branche
    # Convention de nommage : type/description-courte-en-kebab-case
    git checkout -b feature/aifs-support
    # ou
    git checkout -b fix/grib-multigroup-windows
    # ou
    git checkout -b docs/ecmwf-ensemble-page

Étape 2 — Développer
~~~~~~~~~~~~~~~~~~~~~~

Travaillez normalement. Quelques règles :

- **Un commit = une unité logique cohérente.** Préférez plusieurs petits
  commits à un seul commit géant.
- **Messages de commit en anglais**, au format
  ``type: description courte`` (50 caractères max sur la première ligne) :

  .. code-block:: bash

      git commit -m "feat: add AIFS model support"
      git commit -m "fix: handle missing heightAboveGround coord in cfgrib"
      git commit -m "docs: add ENFO parameters table in ecmwf.rst"
      git commit -m "test: add unit tests for AIFS downloader"
      git commit -m "chore: bump version to 0.3b0"
      git commit -m "refactor: extract _validate_steps() from _downloader.py"

  Types reconnus : ``feat``, ``fix``, ``docs``, ``test``, ``chore``,
  ``refactor``, ``perf``, ``ci``.

- **Ne pas committer** : fichiers ``.grib2``, ``.nc``, ``.idx``,
  ``htmlcov/``, ``dist/``, ``*.egg-info/`` (tous listés dans ``.gitignore``).

Étape 3 — Vérifier localement avant de pousser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avant chaque push, lancer la chaîne qualité complète. Un push avec des
erreurs de lint ou des tests cassés fait échouer la CI et bloque la PR.

.. code-block:: bash

    # 1. Lint : détection d'erreurs et vérification du formatage
    ruff check src tests
    ruff format src tests

    # 2. Vérification des types
    mypy src/meteopendata2netcdf

    # 3. Tests (hors réseau — pas de téléchargement ECMWF)
    pytest -m "not network" --tb=short

    # 4. Tests avec rapport de couverture
    pytest -m "not network" --cov=meteopendata2netcdf --cov-report=term-missing

    # La couverture doit rester >= 80 % (fail_under = 80 dans pyproject.toml)

.. tip::

   Pour corriger automatiquement les erreurs de lint et de formatage :

   .. code-block:: bash

       ruff check --fix src tests
       ruff format src tests

Étape 4 — Pousser la branche
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Premier push (crée la branche sur GitHub)
    git push -u origin feature/aifs-support

    # Pushs suivants
    git push

Étape 5 — Ouvrir une Pull Request vers ``develop``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sur GitHub :

1. Aller sur la page du dépôt
2. GitHub affiche une bannière **"Compare & pull request"** pour votre branche
   — cliquer dessus (ou aller dans **Pull requests → New pull request**)
3. Vérifier que la cible est bien **``develop``** (et non ``main``)
4. Remplir le titre et la description :

   - **Titre** : même format que les commits (``feat: ...``, ``fix: ...``)
   - **Description** : expliquer *pourquoi* le changement, pas seulement *quoi*
   - Mentionner l'issue résolue si applicable (``Closes #42``)

5. Cliquer **Create pull request**

La CI se déclenche automatiquement sur la PR (workflow ``ci.yml``) :

- ✅ Lint (ruff check + ruff format)
- ✅ mypy strict
- ✅ Tests sur 6 combinaisons OS × Python (Linux, Windows, macOS × 3.12, 3.13)
- ✅ Build wheel + sdist + twine check

**La PR ne peut pas être mergée tant que la CI n'est pas entièrement verte.**

Étape 6 — Review et merge dans ``develop``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Après validation :

.. code-block:: bash

    # Sur GitHub : cliquer "Squash and merge" ou "Merge pull request"
    # (Squash and merge recommandé pour garder develop propre)

    # Supprimer la branche de travail après merge (bouton GitHub ou en ligne)
    git push origin --delete feature/aifs-support

    # Mettre à jour develop localement
    git checkout develop
    git pull origin develop


Préparer et publier une release
---------------------------------

Une release est déclenchée quand ``develop`` contient un ensemble de
changements cohérents et stables que l'on veut publier sur PyPI.

Étape 1 — Mettre à jour la version et le changelog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sur une branche dédiée depuis ``develop`` :

.. code-block:: bash

    git checkout develop
    git pull origin develop
    git checkout -b chore/release-0.3b0

Modifier **``pyproject.toml``** :

.. code-block:: toml

    [project]
    version = "0.3b0"

Mettre à jour **``CHANGELOG.md``** en déplaçant la section ``[Unreleased]``
vers la nouvelle version :

.. code-block:: markdown

    ## [0.3b0] — 2026-07-15

    ### Added
    - Support du modèle AIFS (stream oper, résolution 0.25°)

    ### Fixed
    - Correction de la gestion des groupes GRIB sur Windows

    ## [Unreleased]
    *(rien pour l'instant)*

Committer :

.. code-block:: bash

    git add pyproject.toml CHANGELOG.md
    git commit -m "chore: bump version to 0.3b0"
    git push -u origin chore/release-0.3b0

Ouvrir une PR ``chore/release-0.3b0`` → ``develop``, la merger après CI verte.

Étape 2 — Merger ``develop`` dans ``main``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git checkout main
    git pull origin main
    git merge --no-ff develop -m "release: merge develop into main for v0.3b0"
    git push origin main

La CI se relance sur ``main``. Attendre qu'elle soit verte avant de continuer.

Étape 3 — Créer le tag Git
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Créer un tag annoté (recommandé : contient un message et une date)
    git tag -a v0.3b0 -m "Release v0.3b0"

    # Pousser le tag
    git push origin v0.3b0

Étape 4 — Créer la release GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sur GitHub (méthode IHM — recommandée) :

1. **Releases → Draft a new release**
2. **Choose a tag** → sélectionner ``v0.3b0``
3. **Target** → ``main``
4. **Release title** → ``v0.3b0``
5. **Description** → coller le contenu du CHANGELOG pour cette version
6. Cocher **"Set as a pre-release"** si version bêta (suffixe ``b``)
7. Cliquer **Publish release**

.. warning::

   La création d'une release via l'IHM GitHub déclenche l'événement
   ``release: published``, **pas** l'événement ``push: tags``. Le workflow
   ``publish.yml`` est configuré pour répondre aux deux. Si vous avez créé
   le tag en ligne de commande **avant** la release GitHub, le workflow aura
   déjà été déclenché par ``push: tags``.

   Pour éviter une double exécution, l'ordre recommandé est :

   1. Pousser le tag (``git push origin v0.3b0``) → déclenche ``publish.yml``
   2. Créer la release GitHub manuellement **sans** repousser le tag

Étape 5 — Vérifier la publication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dans l'onglet **Actions → Publish to PyPI** :

.. code-block:: text

    Publish to PyPI
    ├── Build           ← construction wheel + sdist
    └── build-and-publish
        ├── Checkout
        ├── Build
        └── Publish to PyPI (Trusted Publishing OIDC)
                         ↑ échange un token de courte durée avec PyPI
                           sans aucun secret stocké dans GitHub

Après succès, vérifier sur PyPI :
``https://pypi.org/project/meteopendata2netcdf/0.3b0/``

Étape 6 — Activer la version sur Read the Docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Read the Docs détecte automatiquement le nouveau tag. Pour rendre la
documentation de cette version accessible :

1. Aller sur ``https://readthedocs.org/projects/meteopendata2netcdf/versions/``
2. Trouver ``v0.3b0`` dans la liste
3. Cliquer **Edit** → cocher **Active** → **Save**

La documentation sera disponible sur :
``https://meteopendata2netcdf.readthedocs.io/en/v0.3b0/``


Gestion des versions majeures (à partir de v1.0)
--------------------------------------------------

À partir de la version 1.0, une branche de maintenance ``v1`` sera créée
pour permettre des correctifs sur la v1 tout en développant la v2 sur
``develop``.

Création de la branche ``v1`` au moment du tag v1.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Après avoir mergé develop → main et créé le tag v1.0.0
    git checkout main
    git checkout -b v1
    git push origin v1

Cette branche ``v1`` :

- reçoit les correctifs critiques (backports depuis ``develop``)
- est configurée dans Read the Docs comme version active permanente
- est protégée en écriture directe sur GitHub (PRs obligatoires)

Modèle de branches avec plusieurs versions majeures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    main      ← v2.x en développement actif
    │
    ├── develop    ← intégration features v2.x
    ├── v1         ← maintenance v1.x (correctifs uniquement)
    │
    ├── (tags) v1.0.0, v1.1.0, v1.2.3 ...
    └── (tags) v2.0.0b0, v2.0.0 ...

Intégration Read the Docs multi-versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - URL RTD
     - Source
     - Usage
   * - ``/en/latest/``
     - branche ``main``
     - Développement en cours (peut être instable)
   * - ``/en/stable/``
     - Dernier tag sans ``b``
     - Référence recommandée pour les utilisateurs
   * - ``/en/v1/``
     - branche ``v1``
     - Documentation maintenance v1
   * - ``/en/v1.2.3/``
     - tag ``v1.2.3``
     - Version exacte archivée

Pour configurer RTD correctement :

1. **Settings → Default branch** → ``main``
2. **Versions → v1** → Active = oui, Privacy = Public
3. **Advanced Settings → Default version** → ``stable``
   (pointe sur le dernier tag non-bêta)


Déclenchement manuel de la CI
--------------------------------

Si la CI ne s'est pas déclenchée automatiquement (par exemple après un
changement de configuration GitHub Actions), vous pouvez la déclencher
manuellement :

.. code-block:: text

    GitHub → Actions → [nom du workflow] → Run workflow → Sélectionner la branche → Run

Pour ``publish.yml`` spécifiquement (re-publier une version déjà taguée) :

.. code-block:: text

    GitHub → Actions → Publish to PyPI → Run workflow → main → Run

.. warning::

   PyPI refuse catégoriquement le re-upload d'une version existante.
   Si le workflow de publication échoue après que la wheel a déjà été
   uploadée, il faut obligatoirement incrémenter la version avant de
   retenter.


Règles de contribution (résumé)
---------------------------------

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - 1.
     - **Toujours partir depuis ``develop``**, jamais depuis ``main``.
   * - 2.
     - **Un PR = une fonctionnalité ou un correctif.** Ne pas mélanger
       refactorisations et ajouts de fonctionnalités.
   * - 3.
     - **La CI doit être entièrement verte** avant de demander un merge.
   * - 4.
     - **Tout nouveau code public doit être couvert par des tests.**
       La couverture ne doit pas descendre sous 80 %.
   * - 5.
     - **Zéro dépendance réseau dans les tests.** Toute interaction avec
       ``ecmwf-opendata`` ou ``cfgrib`` doit être mockée.
   * - 6.
     - **Les docstrings suivent le style Google** (Args, Returns, Raises).
   * - 7.
     - **Mettre à jour ``CHANGELOG.md``** dans la section ``[Unreleased]``
       pour chaque changement notable.
   * - 8.
     - **Ne pas modifier la version dans ``pyproject.toml``** dans un PR de
       fonctionnalité. La version est incrémentée uniquement dans un PR de
       release dédié (``chore/release-X.Y.Z``).
   * - 9.
     - **Ne jamais forcer un push sur ``main``** (``git push --force``).
   * - 10.
     - **Signaler les problèmes** via les
       `Issues GitHub <https://github.com/miki4iaml/meteopendata/issues>`_
       avant d'ouvrir un PR pour discuter de l'approche.


Ajouter le support d'une nouvelle source de données
-----------------------------------------------------

L'ajout d'une nouvelle source (par exemple NOAA GFS) suit un modèle
reproductible :

1. **Créer la branche** ``feature/noaa-gfs-support`` depuis ``develop``

2. **Ajouter un module** ``src/meteopendata2netcdf/sources/noaa.py`` avec :

   - Une classe ``NOAAGFSDownloader`` suivant la même interface que
     ``IFSSurfaceDownloader`` (méthodes ``download()`` et
     ``get_latest_run_time()``)
   - Un dataclass ``DownloadResult`` ou réutiliser celui existant
   - Des constantes dans ``_constants.py`` ou dans un module dédié

3. **Écrire les tests** dans ``tests/test_noaa.py`` en mockant tous les
   appels réseau (même approche que ``test_downloader.py``)

4. **Documenter la source** dans ``docs/source/sources/noaa.rst`` en
   suivant le modèle de ``docs/source/sources/ecmwf.rst``

5. **Mettre à jour** ``docs/source/sources/index.rst``, ``__init__.py``
   (``__all__``), ``CHANGELOG.md`` et ``docs/source/vision.rst``
   (périmètre couvert)

6. **Ouvrir un PR** vers ``develop`` avec la CI verte

Avant d'intégrer une nouvelle source, vérifier qu'elle n'est pas déjà
couverte par ``meteofetch`` ou une autre bibliothèque établie — voir la
philosophie du projet dans :ref:`vision`.
