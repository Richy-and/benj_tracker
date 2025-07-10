# Déploiement sur Render.com

## Configuration du Projet

Ce projet est maintenant configuré pour être déployé sur Render.com avec les fichiers suivants :

- `requirements.txt` - Dépendances Python
- `Procfile` - Command de démarrage pour Render
- `runtime.txt` - Version Python spécifiée
- `render.yaml` - Configuration infrastructure as code (optionnel)

## Étapes de Déploiement

### 1. Préparer le Repository
1. Commitez tous les fichiers dans votre repository Git
2. Poussez vers GitHub, GitLab ou Bitbucket

### 2. Créer le Service Web sur Render
1. Connectez-vous à [render.com](https://render.com)
2. Cliquez sur "New +" et sélectionnez "Web Service"
3. Connectez votre repository Git
4. Configurez les paramètres :
   - **Name**: `qr-attendance-system`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Python Version**: `3.11.0`

### 3. Créer la Base de Données PostgreSQL
1. Dans le dashboard Render, cliquez sur "New +" et sélectionnez "PostgreSQL"
2. Configurez :
   - **Name**: `qr-attendance-db`
   - **Database**: `qr_attendance`
   - **User**: `qr_user`
   - **Region**: Choisissez la même région que votre web service

### 4. Configurer les Variables d'Environnement
Dans les paramètres de votre Web Service, ajoutez :

```
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your-secret-key-here
```

**Important**: Render fournira automatiquement l'URL de la base de données. Copiez-la depuis les détails de votre base PostgreSQL.

### 5. Déployer
1. Cliquez sur "Create Web Service"
2. Render construira et déploiera automatiquement votre application
3. L'URL de votre application sera disponible dans le dashboard

## Variables d'Environnement Requises

- `DATABASE_URL`: URL de connexion PostgreSQL (fournie par Render)
- `SESSION_SECRET`: Clé secrète pour les sessions Flask (générez une chaîne aléatoire sécurisée)

## Fonctionnalités du Système

- **Gestion des Ouvriers**: Ajouter, voir, supprimer des ouvriers
- **Génération QR**: Codes QR uniques pour chaque ouvrier
- **Suivi de Présence**: Marquage automatique via scan QR
- **Rapports**: Journal de présence quotidien
- **Interface Mobile**: Compatible avec smartphones et tablettes

## Sécurité en Production

1. **Secret Key**: Utilisez une clé secrète forte et unique
2. **HTTPS**: Render active automatiquement HTTPS
3. **Base de Données**: Connexions chiffrées via SSL
4. **Variables d'Environnement**: Stockées de manière sécurisée

## Support et Maintenance

- **Logs**: Consultables dans le dashboard Render
- **Monitoring**: Surveillance automatique de l'uptime
- **Backups**: Sauvegardes automatiques de la base de données
- **Scaling**: Mise à l'échelle automatique selon la charge