# Configuration Discord Monitor

## Configuration via fichier .env

Le Discord Monitor utilise maintenant un fichier `.env` pour stocker la configuration de manière sécurisée.

### Fichier .env

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
# Configuration Discord
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_CHANNEL_ID=your_channel_id_here

# Configuration Flask
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True

# Configuration de la base de données
DATABASE_URL=sqlite:///database/app.db
```

### Obtenir les informations Discord

#### 1. Token du Bot Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez une nouvelle application ou sélectionnez une existante
3. Allez dans l'onglet "Bot"
4. Cliquez sur "Reset Token" et copiez le token
5. Remplacez `your_discord_bot_token_here` par ce token

#### 2. ID du Serveur (Guild ID)

1. Activez le mode développeur dans Discord (Paramètres > Avancé > Mode développeur)
2. Clic droit sur votre serveur Discord
3. Sélectionnez "Copier l'ID"
4. Remplacez `your_guild_id_here` par cet ID

#### 3. ID du Canal (Channel ID)

1. Clic droit sur le canal que vous voulez surveiller
2. Sélectionnez "Copier l'ID"
3. Remplacez `your_channel_id_here` par cet ID

### Configuration automatique

Une fois le fichier `.env` configuré correctement :

1. Le bot se configure automatiquement au démarrage de l'application
2. La configuration est chargée depuis le fichier `.env`
3. L'interface web affiche le statut du bot sans montrer la configuration

### Interface web

- **Configuration masquée par défaut** : L'interface se concentre sur le monitoring
- **Bouton "Configuration"** : Permet d'afficher temporairement la configuration si nécessaire
- **Sauvegarde automatique** : Les modifications via l'interface web sont sauvegardées dans le fichier `.env`

### Sécurité

- Le fichier `.env` contient des informations sensibles
- Ne jamais commiter le fichier `.env` dans le contrôle de version
- Utilisez le fichier `.env.example` comme modèle
- Gardez votre token Discord secret

### Dépannage

Si le bot ne se connecte pas :

1. Vérifiez que le fichier `.env` existe et contient les bonnes valeurs
2. Vérifiez que le token Discord est valide
3. Vérifiez que les IDs de serveur et canal sont corrects
4. Vérifiez que le bot a les permissions nécessaires sur le serveur
5. Consultez les logs dans l'interface web pour plus d'informations
