from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

discord_bp = Blueprint('discord', __name__)

# Instance globale du monitor Discord (sera initialisée dans main.py)
discord_monitor = None
socketio_instance = None

def set_discord_monitor(monitor):
    """Définit l'instance du monitor Discord"""
    global discord_monitor
    discord_monitor = monitor

def set_socketio(socketio):
    """Définit l'instance SocketIO"""
    global socketio_instance
    socketio_instance = socketio

@discord_bp.route('/config', methods=['GET'])
def get_config():
    """Récupère la configuration actuelle"""
    token = os.getenv('DISCORD_TOKEN')
    guild_id = os.getenv('DISCORD_GUILD_ID')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')
    
    # Vérifier si la configuration est valide (pas les valeurs par défaut)
    is_configured = (token and token != 'your_discord_bot_token_here' and
                    guild_id and guild_id != 'your_guild_id_here' and
                    channel_id and channel_id != 'your_channel_id_here')
    
    config = {
        'token_configured': is_configured,
        'guild_id': guild_id if is_configured else None,
        'channel_id': channel_id if is_configured else None,
        'status': discord_monitor.get_status() if discord_monitor else 'not_configured',
        'config_source': 'env_file' if is_configured else 'not_configured'
    }
    return jsonify(config)

@discord_bp.route('/config', methods=['POST'])
def update_config():
    """Met à jour la configuration Discord et la sauvegarde dans le fichier .env"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    required_fields = ['token', 'guild_id', 'channel_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Le champ {field} est requis'}), 400
    
    try:
        guild_id = int(data['guild_id'])
        channel_id = int(data['channel_id'])
    except ValueError:
        return jsonify({'error': 'guild_id et channel_id doivent être des nombres'}), 400
    
    # Sauvegarder dans le fichier .env
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        # Lire le fichier .env existant
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # Mettre à jour les variables
        updated_vars = {
            'DISCORD_TOKEN': data['token'],
            'DISCORD_GUILD_ID': str(guild_id),
            'DISCORD_CHANNEL_ID': str(channel_id)
        }
        
        # Mettre à jour les lignes existantes ou ajouter de nouvelles
        updated_lines = []
        found_vars = set()
        
        for line in env_lines:
            line_stripped = line.strip()
            if '=' in line_stripped and not line_stripped.startswith('#'):
                var_name = line_stripped.split('=')[0].strip()
                if var_name in updated_vars:
                    updated_lines.append(f"{var_name}={updated_vars[var_name]}\n")
                    found_vars.add(var_name)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Ajouter les variables manquantes
        for var_name, var_value in updated_vars.items():
            if var_name not in found_vars:
                updated_lines.append(f"{var_name}={var_value}\n")
        
        # Écrire le fichier .env mis à jour
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        # Recharger les variables d'environnement
        load_dotenv(override=True)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la sauvegarde: {str(e)}'}), 500
    
    # Arrêter le bot s'il est en cours d'exécution
    if discord_monitor and discord_monitor.is_running:
        discord_monitor.stop()
    
    # Configurer le bot avec les nouveaux paramètres
    if discord_monitor:
        discord_monitor.setup(
            token=data['token'],
            guild_id=guild_id,
            channel_id=channel_id,
            message_callback=handle_new_message,
            status_callback=handle_status_change
        )
        
        print(f"🔧 Bot configuré et sauvegardé dans .env - Guild: {guild_id}, Channel: {channel_id}")
        print(f"🔧 Token configuré: {data['token'][:10]}...")
    
    return jsonify({'message': 'Configuration sauvegardée dans le fichier .env avec succès'})

@discord_bp.route('/start', methods=['POST'])
def start_bot():
    """Démarre le bot Discord"""
    if not discord_monitor:
        return jsonify({'error': 'Monitor Discord non initialisé'}), 500
    
    success, message = discord_monitor.start()
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400

@discord_bp.route('/stop', methods=['POST'])
def stop_bot():
    """Arrête le bot Discord"""
    if not discord_monitor:
        return jsonify({'error': 'Monitor Discord non initialisé'}), 500
    
    success, message = discord_monitor.stop()
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400

@discord_bp.route('/status', methods=['GET'])
def get_status():
    """Récupère le statut du bot"""
    if not discord_monitor:
        return jsonify({'status': 'not_configured'})
    
    return jsonify({'status': discord_monitor.get_status()})

def handle_new_message(message_data):
    """Callback appelé lors de la réception d'un nouveau message Discord"""
    print(f"📨 Nouveau message reçu: {message_data['content']} de {message_data['author']['name']}")
    
    if socketio_instance:
        try:
            # Émettre le message vers tous les clients connectés
            socketio_instance.emit('new_message', message_data, namespace='/')
            print("✅ Message envoyé via WebSocket")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi WebSocket: {e}")
    else:
        print("❌ SocketIO non initialisé")

def handle_status_change(status, message):
    """Callback appelé lors d'un changement de statut du bot"""
    print(f"🔄 Changement de statut: {status} - {message}")
    
    if socketio_instance:
        try:
            # Émettre le changement de statut vers tous les clients connectés
            socketio_instance.emit('status_change', {
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, namespace='/')
            print("✅ Statut envoyé via WebSocket")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du statut: {e}")
    else:
        print("❌ SocketIO non initialisé pour le statut")

