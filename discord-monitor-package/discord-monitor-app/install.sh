#!/bin/bash

# Discord Monitor - Script d'installation automatique pour VPS
# Ce script installe et configure l'application Discord Monitor

set -e

echo "=========================================="
echo "  Discord Monitor - Installation VPS"
echo "=========================================="

# Variables
APP_NAME="discord-monitor"
APP_DIR="/opt/$APP_NAME"
SERVICE_NAME="discord-monitor"
USER="discord-monitor"

# Vérifier les privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root (sudo)"
    exit 1
fi

echo "🔍 Vérification du système..."

# Détecter la distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ Impossible de détecter la distribution Linux"
    exit 1
fi

echo "✅ Système détecté: $OS $VER"

# Installer les dépendances système
echo "📦 Installation des dépendances système..."

if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git curl unzip
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum update -y
    yum install -y python3 python3-pip git curl unzip
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf update -y
    dnf install -y python3 python3-pip git curl unzip
else
    echo "❌ Gestionnaire de paquets non supporté"
    exit 1
fi

# Créer l'utilisateur système
echo "👤 Création de l'utilisateur système..."
if ! id "$USER" &>/dev/null; then
    useradd --system --shell /bin/false --home-dir $APP_DIR --create-home $USER
    echo "✅ Utilisateur $USER créé"
else
    echo "✅ Utilisateur $USER existe déjà"
fi

# Créer le répertoire d'application
echo "📁 Création du répertoire d'application..."
mkdir -p $APP_DIR
chown $USER:$USER $APP_DIR

# Copier les fichiers de l'application
echo "📋 Copie des fichiers de l'application..."
if [ -d "./src" ]; then
    cp -r ./src $APP_DIR/
    cp -r ./requirements.txt $APP_DIR/
    cp ./.env.example $APP_DIR/.env
    chown -R $USER:$USER $APP_DIR
    echo "✅ Fichiers copiés"
else
    echo "❌ Répertoire source non trouvé. Assurez-vous d'exécuter le script depuis le répertoire de l'application."
    exit 1
fi

# Créer l'environnement virtuel Python
echo "🐍 Configuration de l'environnement Python..."
cd $APP_DIR
sudo -u $USER python3 -m venv venv
sudo -u $USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Créer le service systemd
echo "⚙️ Configuration du service systemd..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Discord Monitor - Surveillance de canal Discord
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python src/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Recharger systemd et activer le service
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Configurer le pare-feu (si ufw est installé)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuration du pare-feu..."
    ufw allow 5000/tcp
    echo "✅ Port 5000 ouvert dans le pare-feu"
fi

# Créer un script de gestion
cat > /usr/local/bin/discord-monitor << 'EOF'
#!/bin/bash

SERVICE_NAME="discord-monitor"
APP_DIR="/opt/discord-monitor"

case "$1" in
    start)
        echo "🚀 Démarrage de Discord Monitor..."
        systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "⏹️ Arrêt de Discord Monitor..."
        systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "🔄 Redémarrage de Discord Monitor..."
        systemctl restart $SERVICE_NAME
        ;;
    status)
        systemctl status $SERVICE_NAME
        ;;
    logs)
        journalctl -u $SERVICE_NAME -f
        ;;
    config)
        echo "📝 Édition de la configuration..."
        nano $APP_DIR/.env
        echo "⚠️ Redémarrez le service pour appliquer les changements: discord-monitor restart"
        ;;
    update)
        echo "🔄 Mise à jour de Discord Monitor..."
        cd $APP_DIR
        sudo -u discord-monitor $APP_DIR/venv/bin/pip install --upgrade -r requirements.txt
        systemctl restart $SERVICE_NAME
        echo "✅ Mise à jour terminée"
        ;;
    *)
        echo "Usage: discord-monitor {start|stop|restart|status|logs|config|update}"
        echo ""
        echo "Commandes disponibles:"
        echo "  start    - Démarrer le service"
        echo "  stop     - Arrêter le service"
        echo "  restart  - Redémarrer le service"
        echo "  status   - Afficher le statut du service"
        echo "  logs     - Afficher les logs en temps réel"
        echo "  config   - Éditer la configuration"
        echo "  update   - Mettre à jour l'application"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/discord-monitor

echo ""
echo "🎉 Installation terminée avec succès!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Configurez votre bot Discord:"
echo "   discord-monitor config"
echo ""
echo "2. Démarrez le service:"
echo "   discord-monitor start"
echo ""
echo "3. Vérifiez le statut:"
echo "   discord-monitor status"
echo ""
echo "4. Accédez à l'interface web:"
echo "   http://votre-ip-serveur:5000"
echo ""
echo "📖 Commandes utiles:"
echo "   discord-monitor start    - Démarrer"
echo "   discord-monitor stop     - Arrêter"
echo "   discord-monitor restart  - Redémarrer"
echo "   discord-monitor logs     - Voir les logs"
echo "   discord-monitor config   - Configurer"
echo ""
echo "⚠️ N'oubliez pas de configurer votre bot Discord dans le fichier .env"
echo "   ou via l'interface web avant de démarrer le service."

