# 🚀 Installation Rapide - Discord Monitor

## Installation en 3 étapes

### 1. Télécharger et décompresser
```bash
# Téléchargez le fichier discord-monitor-package.zip sur votre VPS
unzip discord-monitor-package.zip
cd discord-monitor-app
```

### 2. Installer automatiquement
```bash
sudo chmod +x install.sh
sudo ./install.sh
```

### 3. Configurer et démarrer
```bash
# Configurer le bot Discord
sudo discord-monitor config

# Démarrer le service
sudo discord-monitor start

# Accéder à l'interface web
# http://votre-ip-serveur:5000
```

## Configuration Discord Bot

### Avant l'installation, préparez :

1. **Token du bot Discord** :
   - Allez sur https://discord.com/developers/applications
   - Créez une nouvelle application
   - Onglet "Bot" → "Add Bot" → Copiez le token

2. **ID du serveur Discord** :
   - Mode développeur activé dans Discord
   - Clic droit sur votre serveur → "Copier l'ID"

3. **ID du canal à surveiller** :
   - Clic droit sur le canal → "Copier l'ID"

### Inviter le bot sur votre serveur :

1. Onglet "OAuth2" → "URL Generator"
2. Sélectionnez "bot"
3. Permissions : "Read Messages" + "Read Message History"
4. Ouvrez l'URL générée et invitez le bot

## Commandes utiles

```bash
discord-monitor start     # Démarrer
discord-monitor stop      # Arrêter
discord-monitor restart   # Redémarrer
discord-monitor status    # Statut
discord-monitor logs      # Voir les logs
discord-monitor config    # Configurer
```

## Dépannage rapide

- **Service ne démarre pas** : `sudo discord-monitor logs`
- **Bot ne se connecte pas** : Vérifiez le token et les permissions
- **Interface inaccessible** : Vérifiez le pare-feu (port 5000)

---

**C'est tout ! Votre Discord Monitor est prêt ! 🎉**

