# CHANGELOG — Phoenix Vision AI

Toutes les modifications significatives du projet Phoenix Vision AI sont documentées ici.

Le projet est encore en développement. Les entrées **Unreleased** ne constituent pas une version de production.

---

## [Unreleased] — SDK v0.6.0 Enterprise

### Interface Enterprise
- Launcher Enterprise.
- Login sécurisé.
- Formulaire professionnel de demande de compte.
- Phoenix Admin pour validation des demandes.
- Attribution d’identifiants Phoenix.
- Upload et affichage des photos de profil.
- Rôles `ADMIN`, `SUPERVISOR`, `OPERATOR`, `ANALYST`.
- Changement obligatoire du mot de passe temporaire.
- Dashboard Enterprise : topbar, sidebar, grille 3×3, événements, véhicule, localisation, statut système et plein écran.
- Session utilisateur réelle via `/api/session/me`.
- Utilisation de `logoS.png` pour le symbole Phoenix.

### Sécurité
- Cookie de session `HttpOnly`.
- `SameSite=Strict`.
- Contrôle serveur des sessions.
- Protection des routes administratives.
- PBKDF2-HMAC-SHA256 pour les comptes approuvés.
- Nouvelle session après changement de mot de passe.

### Vehicle Intelligence
- `Vehicle`.
- `VehicleManager`.
- `VehicleAdapter`.
- vitesse relative, direction, zone, menace, historique et franchissements.
- suppression d’un bloc dupliqué dans `VehicleManager.update()`.

### ANPR
- `detection/plate_reader.py` devient l’implémentation canonique.
- suppression de l’ancien `core/plate_reader.py` vide après audit.
- OpenCV + Tesseract.
- normalisation, confiance et statuts ANPR.
- enrichissement de `Vehicle` avec `plate_raw`, `plate_confidence`, `plate_status`, `plate_last_seen`.
- raccordement ANPR au moteur et à l’API.
- état ANPR affiché dans le Dashboard.
- Tesseract 5.3.4 validé.
- smoke test : `2431AB01`, 89.5 %, `VALIDATED`.
- test routier réel en cours.

### Problème technique identifié
- `ai/backends/yolo_backend.py` est encore une simulation Foundation.
- ses détections sont fixes et ne proviennent pas d’une vraie inférence YOLO.
- le test réel ANPR ne pourra être évalué correctement qu’après connexion d’un backend de détection réel.

### Caméras / Streaming
- CameraManager, FrameHub, Pipeline, StreamService.
- grille Enterprise légère afin d’éviter neuf flux MJPEG simultanés sur la machine de développement.

### Web / API
- API grille caméras.
- API résumé Dashboard.
- API session.
- API véhicule courant.
- routes Launcher, Login, Enterprise, Admin, changement de mot de passe et demande de compte.

### Historique / Forensic
- Persistance SQLite de l’historique véhicule.
- Conservation des trajectoires, zones et caméras observées.
- Recherche forensic par véhicule et plaque.
- Impression sécurisée des fiches historiques.
- Contrôle RBAC pour consultation, preuves et impression.
- Exclusion des sources de démonstration locales de l’historique officiel.

### Carte opérationnelle
- Console Carte Enterprise.
- Représentation topologique des caméras et zones.
- Métadonnées de localisation préparées pour GPS réel.
- L’interface distingue explicitement le mode topologique d’une future cartographie géographique.

### Plaques / LAPI
- Console Enterprise dédiée aux plaques d’immatriculation.
- Persistance des lectures ANPR/LAPI dans l’historique.
- Recherche par plaque et analyse forensic.
- Statistiques de confiance et statuts de validation.
- Liste de surveillance locale persistante.
- Workflow proposition → validation → activation.
- Permissions Watchlist selon rôle.
- Journal d’audit des actions Watchlist.
- Détection des correspondances actives sans permettre à l’IA de modifier le statut administratif d’un véhicule.
- Les données locales de surveillance ne sont pas propagées automatiquement aux autres clients.

### Persistance Événements / Alertes
- Ajout de `data/events.db`.
- Ajout de `data/alerts.db`.
- Les événements et alertes survivent désormais aux redémarrages.
- Acquittement persistant des alertes.
- APIs temporelles communes pour historique, événements, alertes et Watchlist.

### Paramètres Enterprise
- Nouvelle console Paramètres Enterprise accessible via `/settings`.
- Base Settings persistante locale avec révisions et journal d’audit à chaîne d’intégrité.
- Paramètres organisés par catégories : Général, Interface, Exploitation, LAPI / ANPR, Rapports et Installation.
- Validation centralisée des valeurs et protection des paramètres système en lecture seule.
- Contrôle d’accès Settings par rôles et permissions côté serveur.
- Matrice des autorisations et règles de sécurité obligatoires consultables depuis la console.
- Configuration du site, pays, ville et fuseau horaire.
- Infrastructure i18n préparée : français actif et anglais préparé mais non activable.
- Paramètres Rapports réellement raccordés à la période et aux sections par défaut.
- Affichage de la confiance LAPI configurable sans suppression des données internes.
- Politique de vérification humaine des lectures LAPI incertaines.
- Politique centralisée des actions sensibles avec confirmation avant impression, export PDF et validation locale de surveillance.
- Informations produit, version, édition, éditeur et licence reliées à la source canonique `core/constants.py`.
- Informations techniques d'installation locale exposées sans données sensibles.
- Gestion future des mises à jour explicitement réservée à Phoenix Control Center ; aucun faux mécanisme distant n'est simulé.
- Navigation Paramètres harmonisée sur les consoles Enterprise.
- Firefox / Lubuntu validé pour la console Paramètres et les interactions testées de cette phase.

### Rapports Enterprise
- Ajout d’un registre persistant `reports.db`.
- Références uniques de type `PHX-RPT-YYYYMMDD-XXXXXXXX`.
- Snapshots figés des données utilisées pour chaque rapport.
- Intégrité SHA-256 des snapshots.
- Journal d’audit chaîné et vérifiable.
- Recherche de rapports par référence, auteur, statut et période.
- Permissions `reports.view`, `reports.generate`, `reports.print` et `reports.export_pdf`.
- Console Rapports Enterprise avec génération et recherche historique.
- Rapport officiel imprimable A4 avec identité et logo Phoenix.
- Traçabilité `PRINT_VIEWED` et `PRINT_REQUESTED`.
- Export PDF côté serveur avec ReportLab.
- Optimisation du logo PDF avec Pillow.
- Empreinte SHA-256 du PDF généré.
- Traçabilité `PDF_EXPORT_REQUESTED` et `PDF_GENERATED`.
- Les bases d’exploitation restent exclues du dépôt Git.

### Compatibilité Web
- Firefox / Lubuntu validé pour la console Rapports, l’impression et le téléchargement PDF.
- Architecture Web basée sur standards HTML/CSS/JavaScript et API HTTP.
- Chrome/Chromium, Edge et Safari restent à valider sur les plateformes cibles avant production.

### Gouvernance
Adoption de :

```text
SEARCH → COMPARE → MIGRATE → TEST → DELETE → RETEST → COMMIT
```

---

## [0.4.0] — Foundation
- PhoenixEngine.
- health check.
- lecteur/écriture vidéo.
- détecteur, tracker, compteur, annotateur, reporter et exporter.
- traitement de `videos/route.mp4`.
- génération de `outputs/output.mp4` et `outputs/report.json`.

---

## [0.1.0] — Initial Project Structure
- structure initiale du dépôt ;
- environnement Python ;
- webcam et vidéo de test ;
- premiers modules detection/tracking/plate reader ;
- README, requirements et `.gitignore`.

---

© 2026 Phoenix Security Technologies — Tous droits réservés.
