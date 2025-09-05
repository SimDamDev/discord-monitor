# Discord Monitor

Une application web moderne pour surveiller les messages d'un canal Discord en temps réel.

## 🚀 Fonctionnalités

- **Surveillance en temps réel** : Recevez instantanément les nouveaux messages d'un canal Discord spécifique
- **Interface web moderne** : Interface utilisateur intuitive et responsive
- **Configuration simple** : Configuration via interface web ou fichier de configuration
- **Logs détaillés** : Suivi complet des activités et erreurs
- **Installation automatique** : Script d'installation pour VPS en une commande
- **Service système** : Fonctionne comme un service système avec démarrage automatique

## 📋 Prérequis

### Pour votre bot Discord
1. Créez une application Discord sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez un bot et récupérez son token
3. Activez les intents nécessaires :
   - `MESSAGE CONTENT INTENT`
   - `SERVER MEMBERS INTENT` (optionnel)
4. Invitez le bot sur votre serveur avec les permissions :
   - `Read Messages`
   - `Read Message History`

### Pour votre serveur VPS
- **OS** : Ubuntu 18.04+, Debian 9+, CentOS 7+, ou Fedora 30+
- **RAM** : 512 MB minimum (1 GB recommandé)
- **Python** : 3.7+ (installé automatiquement)
- **Accès root** : Nécessaire pour l'installation

## 🔧 Installation sur VPS

### Méthode 1 : Installation automatique (Recommandée)

1. **Téléchargez et décompressez l'application** :
```bash
wget https://github.com/votre-repo/discord-monitor/releases/latest/download/discord-monitor.zip
unzip discord-monitor.zip
cd discord-monitor
```

2. **Exécutez le script d'installation** :
```bash
sudo chmod +x install.sh
sudo ./install.sh
```

3. **Configurez votre bot Discord** :
```bash
sudo discord-monitor config
```

Ajoutez vos informations :
```env
DISCORD_TOKEN=votre_token_de_bot_discord
DISCORD_GUILD_ID=id_de_votre_serveur
DISCORD_CHANNEL_ID=id_du_canal_a_surveiller
FLASK_SECRET_KEY=une_cle_secrete_aleatoire
FLASK_DEBUG=False
```

4. **Démarrez le service** :
```bash
sudo discord-monitor start
```

5. **Accédez à l'interface web** :
Ouvrez votre navigateur et allez à `http://votre-ip-serveur:5000`

### Méthode 2 : Installation manuelle

Si vous préférez installer manuellement :

```bash
# 1. Cloner ou télécharger les fichiers
git clone https://github.com/votre-repo/discord-monitor.git
cd discord-monitor

# 2. Installer Python et les dépendances
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 3. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env

# 5. Lancer l'application
python src/main.py
```

## 🎮 Configuration Discord

### 1. Créer un bot Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur "New Application"
3. Donnez un nom à votre application
4. Allez dans l'onglet "Bot"
5. Cliquez sur "Add Bot"
6. Copiez le token du bot (gardez-le secret !)

### 2. Configurer les intents

Dans l'onglet "Bot" :
- Activez "MESSAGE CONTENT INTENT"
- Activez "SERVER MEMBERS INTENT" (optionnel)

### 3. Inviter le bot sur votre serveur

1. Allez dans l'onglet "OAuth2" > "URL Generator"
2. Sélectionnez "bot" dans les scopes
3. Sélectionnez les permissions :
   - Read Messages
   - Read Message History
4. Copiez l'URL générée et ouvrez-la dans votre navigateur
5. Sélectionnez votre serveur et autorisez le bot

### 4. Récupérer les IDs

Pour récupérer les IDs Discord, activez le mode développeur :
1. Discord > Paramètres utilisateur > Avancé > Mode développeur
2. Clic droit sur votre serveur → "Copier l'ID" (Guild ID)
3. Clic droit sur le canal à surveiller → "Copier l'ID" (Channel ID)

## 🛠️ Gestion du service

Une fois installé, utilisez ces commandes pour gérer l'application :

```bash
# Démarrer le service
sudo discord-monitor start

# Arrêter le service
sudo discord-monitor stop

# Redémarrer le service
sudo discord-monitor restart

# Voir le statut
sudo discord-monitor status

# Voir les logs en temps réel
sudo discord-monitor logs

# Éditer la configuration
sudo discord-monitor config

# Mettre à jour l'application
sudo discord-monitor update
```

## 🌐 Utilisation de l'interface web

1. **Accès** : Ouvrez `http://votre-ip-serveur:5000` dans votre navigateur

2. **Configuration** :
   - Entrez votre token de bot Discord
   - Entrez l'ID de votre serveur Discord
   - Entrez l'ID du canal à surveiller
   - Cliquez sur "Sauvegarder"

3. **Démarrage** :
   - Cliquez sur "Démarrer" pour commencer la surveillance
   - Les messages apparaîtront en temps réel dans la section "Messages"

4. **Surveillance** :
   - Consultez le statut du bot dans la section "Statut du Bot"
   - Suivez les logs dans la section "Logs récents"

## 🔒 Sécurité

### Recommandations importantes :

1. **Token Discord** : Ne partagez jamais votre token de bot
2. **Pare-feu** : Limitez l'accès au port 5000 aux IPs autorisées
3. **HTTPS** : Utilisez un reverse proxy (nginx) avec SSL en production
4. **Mots de passe** : Changez la clé secrète Flask par défaut

### Configuration avec nginx (optionnel) :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐛 Dépannage

### Le service ne démarre pas
```bash
# Vérifier les logs
sudo discord-monitor logs

# Vérifier la configuration
sudo discord-monitor config

# Redémarrer le service
sudo discord-monitor restart
```

### Le bot ne se connecte pas à Discord
- Vérifiez que le token est correct
- Vérifiez que le bot est invité sur le serveur
- Vérifiez que les intents sont activés

### L'interface web n'est pas accessible
- Vérifiez que le service est démarré : `sudo discord-monitor status`
- Vérifiez que le port 5000 est ouvert dans le pare-feu
- Vérifiez les logs : `sudo discord-monitor logs`

### Aucun message n'apparaît
- Vérifiez que l'ID du canal est correct
- Vérifiez que le bot a les permissions de lecture sur le canal
- Envoyez un message de test dans le canal surveillé

## 📝 Logs

Les logs sont accessibles via :
```bash
# Logs en temps réel
sudo discord-monitor logs

# Logs système
sudo journalctl -u discord-monitor

# Logs avec filtre par date
sudo journalctl -u discord-monitor --since "2024-01-01"
```

## 🔄 Mise à jour

Pour mettre à jour l'application :
```bash
sudo discord-monitor update
```

Ou manuellement :
```bash
# Télécharger la nouvelle version
wget https://github.com/votre-repo/discord-monitor/releases/latest/download/discord-monitor.zip
unzip discord-monitor.zip -d discord-monitor-new

# Sauvegarder la configuration
sudo cp /opt/discord-monitor/.env /tmp/discord-monitor.env.backup

# Arrêter le service
sudo discord-monitor stop

# Remplacer les fichiers
sudo cp -r discord-monitor-new/* /opt/discord-monitor/
sudo cp /tmp/discord-monitor.env.backup /opt/discord-monitor/.env

# Mettre à jour les dépendances
cd /opt/discord-monitor
sudo -u discord-monitor ./venv/bin/pip install -r requirements.txt

# Redémarrer le service
sudo discord-monitor start
```

## 📞 Support

Si vous rencontrez des problèmes :

1. Consultez les logs : `sudo discord-monitor logs`
2. Vérifiez la configuration : `sudo discord-monitor config`
3. Redémarrez le service : `sudo discord-monitor restart`
4. Consultez la documentation Discord : [Discord Developer Portal](https://discord.com/developers/docs)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

**Discord Monitor** - Surveillez vos canaux Discord en toute simplicité ! 🚀

