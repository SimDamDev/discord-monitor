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
    config = {
        'token_configured': bool(os.getenv('DISCORD_TOKEN')),
        'guild_id': os.getenv('DISCORD_GUILD_ID'),
        'channel_id': os.getenv('DISCORD_CHANNEL_ID'),
        'status': discord_monitor.get_status() if discord_monitor else 'not_configured'
    }
    return jsonify(config)

@discord_bp.route('/config', methods=['POST'])
def update_config():
    """Met à jour la configuration Discord"""
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
        
        print(f"🔧 Bot configuré - Guild: {guild_id}, Channel: {channel_id}")
        print(f"🔧 Token configuré: {data['token'][:10]}...")
        print(f"🔧 Callbacks configurés: message={handle_new_message}, status={handle_status_change}")
    
    return jsonify({'message': 'Configuration mise à jour avec succès'})

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

