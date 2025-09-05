import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv

from src.models.user import db
from src.routes.user import user_bp
from src.routes.discord import discord_bp, set_discord_monitor
from src.discord_bot import DiscordMonitor

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Activer CORS pour permettre les requêtes cross-origin
CORS(app)

# Initialiser SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurer SocketIO dans les routes Discord
from src.routes.discord import set_socketio
set_socketio(socketio)

# Enregistrer les blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(discord_bp, url_prefix='/api/discord')

# Initialiser le monitor Discord
discord_monitor = DiscordMonitor()
set_discord_monitor(discord_monitor)

# Configuration automatique si les variables d'environnement sont présentes
def load_discord_config():
    """Charge la configuration Discord depuis les variables d'environnement"""
    token = os.getenv('DISCORD_TOKEN')
    guild_id = os.getenv('DISCORD_GUILD_ID')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')
    
    # Vérifier si toutes les variables sont configurées et ne sont pas des valeurs par défaut
    if (token and token != 'your_discord_bot_token_here' and
        guild_id and guild_id != 'your_guild_id_here' and
        channel_id and channel_id != 'your_channel_id_here'):
        try:
            from src.routes.discord import handle_new_message, handle_status_change
            discord_monitor.setup(
                token=token,
                guild_id=int(guild_id),
                channel_id=int(channel_id),
                message_callback=handle_new_message,
                status_callback=handle_status_change
            )
            print("✅ Configuration Discord chargée depuis le fichier .env")
            print(f"Guild ID: {guild_id}")
            print(f"Channel ID: {channel_id}")
            return True
        except ValueError as e:
            print(f"❌ Erreur dans la configuration Discord: {e}")
            return False
    else:
        print("⚠️  Configuration Discord non trouvée dans le fichier .env")
        print("   Veuillez configurer DISCORD_TOKEN, DISCORD_GUILD_ID et DISCORD_CHANNEL_ID")
        return False

# Charger la configuration Discord au démarrage
load_discord_config()

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Événements SocketIO
@socketio.on('connect')
def handle_connect():
    print('Client connecté')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client déconnecté')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
