# Notes d'Architecture - Application Web Discord

## Technologies identifiées

### Backend
- **Flask** : Framework web Python pour l'API et l'interface
- **discord.py** : Bibliothèque Python pour l'intégration Discord
- **WebSockets/SocketIO** : Pour la communication temps réel avec le frontend

### Frontend
- **HTML/CSS/JavaScript** : Interface utilisateur
- **WebSockets** : Pour recevoir les messages en temps réel

## Fonctionnalités principales

### Bot Discord
- Connexion au serveur Discord spécifique
- Surveillance d'un canal spécifique via l'événement `on_message`
- Filtrage des messages par canal ID
- Transmission des nouveaux messages vers l'application web

### Application Web
- Interface pour configurer le bot (token, server ID, channel ID)
- Affichage en temps réel des nouveaux messages
- Logs et statut de connexion
- Configuration persistante

## Architecture proposée

```
Discord Server → Bot Discord (discord.py) → Flask App → WebSocket → Frontend
```

### Composants
1. **Bot Discord** : Module séparé qui se connecte à Discord
2. **Flask API** : Endpoints pour configuration et données
3. **WebSocket Server** : Communication temps réel
4. **Frontend** : Interface utilisateur responsive
5. **Configuration** : Fichier JSON pour stocker les paramètres

## Événements Discord clés
- `on_ready()` : Confirmation de connexion
- `on_message(message)` : Nouveau message reçu
  - Filtrage par `message.channel.id`
  - Vérification que l'auteur n'est pas le bot

## Installation VPS
- Script d'installation automatique
- Service systemd pour démarrage automatique
- Configuration via variables d'environnement
- Package ZIP avec tous les fichiers nécessaires

