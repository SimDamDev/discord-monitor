# Discord Monitor

Une application web moderne pour surveiller les messages d'un canal Discord en temps réel.

## 🚀 Fonctionnalités

- **Surveillance en temps réel** : Recevez instantanément les nouveaux messages d'un canal Discord spécifique
- **Interface web moderne** : Interface utilisateur intuitive et responsive avec configuration masquée
- **Configuration .env** : Configuration sécurisée via fichier .env avec chargement automatique
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

## 🔧 Installation rapide

```bash
# Cloner le projet
git clone https://github.com/SimDamDev/discord-monitor.git
cd discord-monitor

# Installation automatique
sudo chmod +x install.sh
sudo ./install.sh

# Configuration
sudo discord-monitor config

# Démarrage
sudo discord-monitor start
```

## 📖 Documentation

- [Installation détaillée](docs/installation.md)
- [Configuration .env](docs/configuration.md)
- [Architecture du projet](docs/architecture.md)
- [Changelog](docs/changelog.md)

## 🌐 Utilisation

### Configuration via fichier .env (Recommandé)

1. **Créer le fichier .env** : Copiez `.env.example` vers `.env` et configurez vos paramètres
2. **Accès** : Ouvrez `http://votre-ip-serveur:5000` dans votre navigateur
3. **Démarrage automatique** : Le bot se configure et démarre automatiquement
4. **Surveillance** : Les messages apparaîtront en temps réel

### Configuration via interface web

1. **Accès** : Ouvrez `http://votre-ip-serveur:5000` dans votre navigateur
2. **Configuration** : Cliquez sur "Configuration" pour afficher les champs
3. **Sauvegarde** : Entrez vos paramètres et sauvegardez (sauvegarde automatique dans .env)
4. **Démarrage** : Cliquez sur "Démarrer" pour commencer la surveillance
5. **Surveillance** : Les messages apparaîtront en temps réel

## 🛠️ Gestion du service

```bash
# Démarrer le service
sudo discord-monitor start

# Arrêter le service
sudo discord-monitor stop

# Redémarrer le service
sudo discord-monitor restart

# Voir le statut
sudo discord-monitor status

# Voir les logs
sudo discord-monitor logs
```

## 🔒 Sécurité

- Ne partagez jamais votre token de bot Discord
- Limitez l'accès au port 5000 aux IPs autorisées
- Utilisez un reverse proxy (nginx) avec SSL en production
- Changez la clé secrète Flask par défaut

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

**Discord Monitor** - Surveillez vos canaux Discord en toute simplicité ! 🚀
