<div align="center">

<img src="web/static/images/logoS.png" alt="Phoenix Vision AI" width="170">

# PHOENIX VISION AI

### Plateforme intelligente de supervision routière, sécurité vidéo et ANPR

**Phoenix Security Technologies**
*L’innovation au service de la protection.*

</div>

---

## 1. Présentation

**Phoenix Vision AI** est une plateforme de vision par ordinateur et de supervision conçue pour centraliser l’analyse vidéo de la circulation, le suivi des véhicules, la lecture automatisée des plaques d’immatriculation (ANPR), les alertes intelligentes, l’historique, les rapports et l’administration des utilisateurs.

Le projet est porté par **Phoenix Security Technologies** avec l’ambition de construire une solution adaptée aux réalités opérationnelles de la République démocratique du Congo, puis extensible à d’autres marchés africains.

Phoenix Vision AI est actuellement en **phase de développement Enterprise / SDK v0.6.0-dev**. Certaines briques sont fonctionnelles, d’autres sont encore en cours d’intégration ou de validation terrain.

> **Important :** le dépôt ne doit pas présenter comme “terminées” les fonctions qui ne sont pas encore validées sur données réelles.

---

## 2. Objectifs du logiciel

Phoenix Vision AI vise notamment à permettre :

- la supervision de plusieurs caméras depuis un centre de contrôle ;
- la détection et le suivi de véhicules ;
- l’identification d’événements routiers et de comportements suspects ;
- la lecture automatisée de plaques d’immatriculation ;
- la consultation de l’historique des véhicules et événements ;
- la génération de rapports et preuves ;
- la recherche par plaque, caméra, date ou événement ;
- la gestion sécurisée des utilisateurs et des rôles ;
- l’intégration future avec cartes, centres de commandement et infrastructures publiques ou privées.

---

## 3. État actuel du projet

### Interface Enterprise

| Module | État |
|---|---|
| Launcher Enterprise | ✅ Fonctionnel |
| Login sécurisé | ✅ Fonctionnel |
| Demande de compte | ✅ Fonctionnel |
| Validation des comptes par administrateur | ✅ Fonctionnel |
| Mot de passe temporaire + changement obligatoire | ✅ Fonctionnel |
| Sessions HTTPOnly | ✅ Fonctionnel |
| Photos de profil des comptes approuvés | ✅ Fonctionnel |
| Dashboard Enterprise | ✅ Interface fonctionnelle |
| Grille 3×3 caméras | ✅ Interface/API |
| Profil et rôles | ✅ Session serveur |
| Vue véhicule courant | ✅ VehicleManager |
| Statut ANPR | ✅ Connecté au moteur |
| Historique forensic | ✅ Persistant + recherche + impression |
| Console Plaques / LAPI | ✅ Recherche + analyse + statistiques |
| Liste de surveillance locale | ✅ Proposition, validation, audit et correspondances |
| Événements persistants | ✅ SQLite + API + console |
| Carte opérationnelle | ✅ Mode topologique ; GPS réel à configurer |
| Rapports Enterprise | ✅ Génération, recherche, impression, PDF et audit |
| Paramètres Enterprise | ✅ Configuration persistante, RBAC, audit, LAPI, Rapports et installation |
| Utilisateurs Enterprise | ✅ Registre, cycle de vie, RBAC, console, audit, impression A4 et QR interne |
| Système Enterprise | ✅ Santé système, runtime, composants, bases, diagnostics, audit et RBAC |
| Sauvegardes Enterprise | 🔄 À construire |

### Vision IA et ANPR

| Élément | État |
|---|---|
| Vehicle / VehicleManager | ✅ |
| VehicleAdapter | ✅ |
| Tracking / historique véhicule | ✅ Fondation |
| PlateReader canonique | ✅ `detection/plate_reader.py` |
| Tesseract OCR | ✅ Installé et détecté |
| Smoke test ANPR contrôlé | ✅ `2431AB01` — 89,5 % |
| Test image routière réelle | 🔄 En cours |
| Détection locale YOLO réelle | ⚠️ Backend local actuellement simulé |
| Détecteur spécialisé de plaques | ⏳ Futur |
| Consensus ANPR multi-frame | ⏳ Futur |
| PaddleOCR | ⏳ Option future |

### Point technique important

Le backend `ai/backends/yolo_backend.py` utilisé localement est encore une **implémentation Foundation simulée** : il renvoie actuellement des détections fixes pour tester l’architecture. Les résultats de détection locaux ne doivent donc pas être présentés comme une inférence YOLO réelle tant que ce backend n’a pas été remplacé ou connecté à un backend réel.

---

## 4. Architecture générale

```text
PhoenixVisionAI/
│
├── ai/
├── cloud/
├── colab_server/
├── core/
│   ├── application/
│   ├── camera/
│   ├── database/
│   ├── events/
│   ├── evidence/
│   ├── framehub/
│   ├── intelligence/
│   ├── journey/
│   ├── lines/
│   ├── memory/
│   ├── pipeline/
│   ├── reports/
│   ├── search/
│   ├── security/
│   ├── server/
│   ├── storage/
│   ├── streaming/
│   ├── timeline/
│   ├── ui/
│   ├── users/
│   ├── vehicle/
│   ├── watchlist/
│   ├── workspace/
│   └── zones/
│
├── detection/
│   ├── detector.py
│   ├── tracker.py
│   └── plate_reader.py
│
├── web/
│   ├── app.py
│   ├── routes/
│   ├── static/
│   └── templates/
│
├── tests/
├── tools/
├── docs/
├── frames/
├── videos/
├── outputs/
├── run.py
└── requirements.txt
```

### Règle de nettoyage architectural

```text
SEARCH → COMPARE → MIGRATE → TEST → DELETE → RETEST → COMMIT
```

---

## 5. Flux de traitement cible

```text
CAMÉRA / VIDÉO
      │
      ▼
DÉTECTION IA
      │
      ▼
TRACKING
      │
      ▼
VEHICLE ADAPTER
      │
      ▼
VEHICLE MANAGER
      │
      ├───────────────┐
      ▼               ▼
ANPR / OCR        INTELLIGENCE
      │               │
      └───────┬───────┘
              ▼
        ÉVÉNEMENTS / MÉMOIRE
              │
              ▼
          API FASTAPI
              │
              ▼
      DASHBOARD ENTERPRISE
```

---

## 6. ANPR

Le module ANPR V1 repose actuellement sur :

- OpenCV pour le recadrage et le prétraitement ;
- Tesseract OCR pour la lecture ;
- normalisation des chaînes ;
- score de confiance ;
- conservation de la meilleure lecture dans `Vehicle`.

### Validation actuelle

```bash
python tools/anpr_smoke_test.py
```

Résultat validé :

```text
Plaque          : 2431AB01
Texte OCR brut  : 2431AB01
Confiance       : 89.5 %
Statut          : VALIDATED
```

Le test sur `frames/frame_000013.jpg` a atteint Tesseract mais retourne actuellement `OCR_EMPTY`. L’analyse a montré que le backend YOLO local renvoie des coordonnées simulées et fixes. La prochaine étape est donc de connecter un backend de détection réel avant d’évaluer la précision ANPR terrain.

---

## 7. `route.mp4` et `route.avi`

Les deux fichiers ont actuellement :

```text
640×360
25 FPS
750 frames
```

`route.avi` contient déjà des annotations/rectangles issus d’un traitement antérieur. Pour l’ANPR, `route.mp4` reste préférable car il s’agit de la source la plus propre, sans overlays susceptibles de masquer des pixels utiles.

`route.avi` reste utile comme **référence visuelle de détection**.

---

### Paramètres Enterprise — état actuel

La console `/settings` constitue le centre de configuration locale de Phoenix Vision AI.

Fonctions actuellement intégrées :

- persistance des paramètres dans une base Settings locale ;
- révisions et journal d'audit avec contrôle d'intégrité ;
- validation des paramètres et valeurs système protégées ;
- permissions Settings contrôlées côté serveur ;
- configuration du site, de la localisation et du fuseau horaire ;
- français actif comme langue d'interface, anglais préparé mais non activable ;
- consultation des droits effectifs et des règles de sécurité obligatoires ;
- période et sections par défaut réellement appliquées à la console Rapports ;
- affichage de la confiance LAPI configurable ;
- vérification humaine configurable pour les lectures LAPI incertaines ;
- confirmation obligatoire des opérations classées sensibles ;
- informations d'installation et de runtime non sensibles ;
- identité produit et version issues de `core/constants.py` ;
- licence propriétaire affichée depuis la source canonique ;
- navigation `/settings` harmonisée avec les consoles Enterprise.

Les données techniques de confiance LAPI restent conservées même lorsque leur affichage est masqué. Une lecture OCR incertaine ne constitue pas, à elle seule, un véhicule suspect ou recherché.

La distribution centralisée des mises à jour n'est pas encore implémentée dans Phoenix Vision AI. Elle est prévue comme fonction de Phoenix Control Center.

La console a été validée pendant le développement sous Firefox / Lubuntu. Les autres navigateurs majeurs restent à tester avant une validation de compatibilité générale.


### Utilisateurs Enterprise — état actuel

La gestion des utilisateurs dispose désormais d'un registre administratif
Enterprise distinct du stockage des identifiants d'authentification.

Fonctionnalités actuellement opérationnelles :

- registre persistant local `users.db` avec identifiant utilisateur stable ;
- synchronisation avec le workflow historique de demandes et d'approbation ;
- cycle de vie `APPROVED`, `ACTIVE`, `SUSPENDED`, `DISABLED` et `EXPIRED` ;
- contrôle réel de l'accès lors de la connexion et pendant les sessions ;
- révocation des sessions après suspension, désactivation ou changement de rôle ;
- permissions d'administration utilisateurs intégrées au RBAC central ;
- accès complet pour ADMIN et consultation limitée pour SUPERVISOR ;
- protection des informations sensibles selon les permissions ;
- console `/users` avec recherche, filtres, dossiers et états de compte ;
- compteur réel des demandes de comptes encore en attente ;
- modification administrative contrôlée des dossiers ;
- suspension, désactivation et réactivation avec motif obligatoire ;
- changement de rôle contrôlé entre OPERATOR, ANALYST et SUPERVISOR ;
- promotion directe vers ADMIN interdite depuis Phoenix Vision AI ;
- journal d'audit utilisateur à chaîne d'intégrité ;
- fiche utilisateur officielle A4 avec photo, rôle, statut et droits effectifs ;
- QR interne ne contenant que la référence Phoenix `PHX-USER:<user_id>` ;
- aucun hash, sel ou mot de passe n'est enregistré dans le registre administratif.

Le workflow temporaire `/admin/requests` reste utilisé pendant le développement
pour l'approbation initiale et la génération du mot de passe temporaire.
À terme, la gouvernance complète des comptes sera intégrée à Phoenix Admin.


### Système Enterprise — état actuel

La console `/system` fournit une vue locale et opérationnelle de l'état
de Phoenix Vision AI sans modifier directement la configuration du système.

Fonctionnalités actuellement opérationnelles :

- état global calculé à partir de mesures réelles ;
- utilisation CPU, mémoire et stockage via `psutil` ;
- informations de runtime et de processus Phoenix Vision AI ;
- liaison réelle de `PhoenixEngine` et `Stream Service` au registre runtime ;
- supervision des principaux composants locaux du moteur ;
- détection dynamique des bases SQLite présentes dans `data/` ;
- contrôle de disponibilité des bases sans modification de leur contenu ;
- diagnostic général non destructif ;
- vérification SQLite à la demande avec `PRAGMA quick_check` en lecture seule ;
- journal local des diagnostics avec chaîne d'intégrité SHA-256 ;
- permissions `system.view`, `system.diagnostics` et `system.database_check` ;
- ADMIN autorisé à consulter et exécuter les diagnostics ;
- SUPERVISOR limité à la consultation de l'état système ;
- ANALYST et OPERATOR sans accès à la console Système ;
- validation stricte des noms de bases transmis à l'API ;
- contrôle d'origine des opérations POST sensibles ;
- console terminal allégée en fonctionnement normal.

Le nombre de bases affiché par la console n'est pas figé : Phoenix Vision AI
détecte dynamiquement les bases SQLite locales disponibles. Lors de la
validation de cette phase, l'installation de développement comportait sept
bases accessibles.

Le cookie de session utilise actuellement `HttpOnly` et `SameSite=Strict`.
Le mode `Secure` reste désactivé pendant le développement local en HTTP et
devra être activé lors d'un déploiement de production sous HTTPS.

La console Système a été validée pendant le développement sous Firefox /
Lubuntu.


## 8. Dashboard Enterprise

Chaque bouton doit progressivement ouvrir une fonction réelle.

| Élément | Fonction cible |
|---|---|
| Tableau de bord | Vue générale temps réel |
| Caméras | État, recherche, vue individuelle, plein écran |
| Événements | Franchissements, véhicules, événements système |
| Alertes IA | Suspect, recherché, comportement anormal |
| Historique | Recherche par date, véhicule, caméra, événement |
| Carte | Caméras, zones et événements géolocalisés |
| ANPR / Plaques | Dernières lectures, recherche et historique |
| Rapports | PDF / CSV / JSON et statistiques |
| Paramètres | Configuration générale |
| Utilisateurs | Comptes, rôles, approbation, suspension |
| Système | CPU, RAM, stockage, moteurs et services |
| Sauvegardes | Sauvegarde et restauration |
| Notifications | Centre de notifications |
| Profil | Identité, photo et sécurité du compte |

### Rapports Enterprise — état actuel

Phoenix Vision AI possède maintenant un système de rapports persistant :

- génération de rapports sur une période réelle ;
- archivage durable avec référence unique `PHX-RPT-...` ;
- recherche ultérieure par numéro de rapport, auteur, statut ou période ;
- snapshot figé des données au moment de la génération ;
- vérification d’intégrité SHA-256 ;
- journal d’audit traçable ;
- document officiel A4 avec identité Phoenix ;
- impression selon les permissions du compte ;
- export PDF côté serveur avec ReportLab ;
- empreinte SHA-256 du fichier PDF généré.

Les données utilisées proviennent des sources persistantes disponibles :
historique véhicule, LAPI, événements, alertes et liste de surveillance.

Le navigateur Firefox sous Lubuntu est actuellement validé pour cette
fonction. Chrome/Chromium, Edge et Safari devront être validés sur les
plateformes cibles avant une diffusion de production.

---

## 9. Sécurité

Phoenix Vision AI applique déjà plusieurs principes :

- cookie de session `HttpOnly` ;
- `SameSite=Strict` ;
- rôles utilisateur ;
- validation des comptes par administrateur ;
- PBKDF2-HMAC-SHA256 pour les comptes approuvés ;
- changement obligatoire du mot de passe temporaire ;
- contrôle d’accès aux pages administratives.

### À renforcer avant production

- HTTPS obligatoire ;
- expiration et rotation des sessions ;
- stockage de session persistant ;
- généralisation de la journalisation d’audit à tous les modules ;
- politique de rétention ;
- chiffrement des sauvegardes ;
- secrets hors du code ;
- protection CSRF ;
- revue de sécurité et tests d’intrusion.

---

## 10. Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Tesseract

```bash
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-eng
```

### Lancement

```bash
python run.py
```

Interface :

```text
http://127.0.0.1:8000
```

---

## 11. Tests utiles

```bash
python -m compileall -q core detection web tools
python tools/anpr_smoke_test.py
python tools/anpr_real_frame_test.py
```

Si `pytest` est installé :

```bash
python -m pytest tests -q
```

---

## 12. Roadmap

### V1 — Foundation / Enterprise Prototype
Moteur vidéo, détection/tracking, Vehicle Intelligence, Dashboard Enterprise, comptes/rôles, ANPR V1, événements, historique, rapports et administration.

### V2 — Smart Traffic & Security
Détecteur de plaques spécialisé, ANPR multi-frame, alertes IA avancées,
multi-site, cartographie géographique, recherche avancée, API d’intégration,
Centre de notifications et d’actions Phoenix, supervision système et haute
disponibilité.

### V3 — National / African Platform
Centre de commandement multi-ville, corrélation inter-caméras, Edge + Cloud
et déploiements nationaux/régionaux.

La plateforme devra également exploiter les données réellement collectées par
les caméras Phoenix afin de produire des analyses statistiques routières :
densité par zone, heures de pointe, embouteillages récurrents, tendances,
comparaisons territoriales et indicateurs utiles à la planification de la
mobilité. Ces fonctions restent dans la roadmap et ne sont pas présentées
comme déjà opérationnelles.

---

## 13. Propriété

**Phoenix Vision AI** est un projet de **Phoenix Security Technologies**.

**Porteur du projet : Ritchi Biongo**
Conception, vision produit, pilotage stratégique et développement du projet Phoenix Vision AI.

Les composants tiers conservent leurs licences respectives.

---

## 14. Statut de production

Phoenix Vision AI est actuellement un **logiciel en développement**. Il ne doit pas être présenté comme un système de sécurité publique, d’identification ou d’ANPR certifié tant que les validations terrain, sécurité, charge, résilience et conformité ne sont pas terminées.

---

<div align="center">

**PHOENIX SECURITY TECHNOLOGIES**

*L’innovation au service de la protection.*

© 2026 Phoenix Security Technologies. Tous droits réservés.

</div>
