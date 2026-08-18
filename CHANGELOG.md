# CHANGELOG — Phoenix Vision AI

Toutes les modifications significatives du projet Phoenix Vision AI sont documentées ici.

Le projet est encore en développement. Les entrées **Unreleased** ne constituent pas une version de production.

---

## [Unreleased] — SDK v0.5.0 Enterprise

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
