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



@discord_bp.route('/update', methods=['POST'])
def update_application():
    """Met à jour l'application depuis Git"""
    import subprocess
    import sys
    
    try:
        # Vérifier si les mises à jour sont activées
        auto_update = os.getenv('AUTO_UPDATE_ENABLED', 'True').lower() == 'true'
        if not auto_update:
            return jsonify({'error': 'Les mises à jour automatiques sont désactivées'}), 403
        
        # Arrêter le bot s'il est en cours d'exécution
        bot_was_running = False
        if discord_monitor and discord_monitor.is_running:
            bot_was_running = True
            discord_monitor.stop()
            
        # Sauvegarder la configuration actuelle
        current_config = {
            'token': os.getenv('DISCORD_TOKEN'),
            'guild_id': os.getenv('DISCORD_GUILD_ID'),
            'channel_id': os.getenv('DISCORD_CHANNEL_ID')
        }
        
        # Obtenir la branche de mise à jour
        update_branch = os.getenv('UPDATE_BRANCH', 'master')
        
        # Exécuter les commandes Git
        commands = [
            ['git', 'fetch', 'origin'],
            ['git', 'reset', '--hard', f'origin/{update_branch}'],
            ['git', 'clean', '-fd']
        ]
        
        results = []
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=os.path.dirname(os.path.dirname(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                results.append({
                    'command': ' '.join(cmd),
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                })
                
                if result.returncode != 0:
                    return jsonify({
                        'error': f'Erreur lors de l\'exécution de {" ".join(cmd)}',
                        'details': result.stderr,
                        'results': results
                    }), 500
                    
            except subprocess.TimeoutExpired:
                return jsonify({
                    'error': f'Timeout lors de l\'exécution de {" ".join(cmd)}',
                    'results': results
                }), 500
            except Exception as e:
                return jsonify({
                    'error': f'Erreur lors de l\'exécution de {" ".join(cmd)}: {str(e)}',
                    'results': results
                }), 500
        
        # Recharger les variables d'environnement
        load_dotenv(override=True)
        
        # Restaurer la configuration si elle a été perdue
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_path):
            # Vérifier si la config est toujours là
            current_token = os.getenv('DISCORD_TOKEN')
            if not current_token or current_token == 'your_discord_bot_token_here':
                # Restaurer la configuration
                if current_config['token'] and current_config['token'] != 'your_discord_bot_token_here':
                    with open(env_path, 'r', encoding='utf-8') as f:
                        env_lines = f.readlines()
                    
                    updated_lines = []
                    found_vars = set()
                    
                    for line in env_lines:
                        line_stripped = line.strip()
                        if '=' in line_stripped and not line_stripped.startswith('#'):
                            var_name = line_stripped.split('=')[0].strip()
                            if var_name == 'DISCORD_TOKEN':
                                updated_lines.append(f"DISCORD_TOKEN={current_config['token']}\n")
                                found_vars.add('DISCORD_TOKEN')
                            elif var_name == 'DISCORD_GUILD_ID':
                                updated_lines.append(f"DISCORD_GUILD_ID={current_config['guild_id']}\n")
                                found_vars.add('DISCORD_GUILD_ID')
                            elif var_name == 'DISCORD_CHANNEL_ID':
                                updated_lines.append(f"DISCORD_CHANNEL_ID={current_config['channel_id']}\n")
                                found_vars.add('DISCORD_CHANNEL_ID')
                            else:
                                updated_lines.append(line)
                        else:
                            updated_lines.append(line)
                    
                    # Ajouter les variables manquantes
                    if 'DISCORD_TOKEN' not in found_vars and current_config['token']:
                        updated_lines.append(f"DISCORD_TOKEN={current_config['token']}\n")
                    if 'DISCORD_GUILD_ID' not in found_vars and current_config['guild_id']:
                        updated_lines.append(f"DISCORD_GUILD_ID={current_config['guild_id']}\n")
                    if 'DISCORD_CHANNEL_ID' not in found_vars and current_config['channel_id']:
                        updated_lines.append(f"DISCORD_CHANNEL_ID={current_config['channel_id']}\n")
                    
                    with open(env_path, 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
                    
                    load_dotenv(override=True)
        
        # Reconfigurer le bot si nécessaire
        if discord_monitor and current_config['token'] and current_config['token'] != 'your_discord_bot_token_here':
            discord_monitor.setup(
                token=current_config['token'],
                guild_id=int(current_config['guild_id']),
                channel_id=int(current_config['channel_id']),
                message_callback=handle_new_message,
                status_callback=handle_status_change
            )
            
            # Redémarrer le bot s'il était en cours d'exécution
            if bot_was_running:
                discord_monitor.start()
        
        # Notifier via WebSocket
        if socketio_instance:
            socketio_instance.emit('status_change', {
                'status': 'updated',
                'message': 'Application mise à jour avec succès',
                'timestamp': datetime.now().isoformat()
            }, namespace='/')
        
        return jsonify({
            'message': 'Mise à jour effectuée avec succès',
            'results': results,
            'config_restored': current_config['token'] != 'your_discord_bot_token_here',
            'bot_restarted': bot_was_running
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la mise à jour: {str(e)}',
            'type': type(e).__name__
        }), 500

@discord_bp.route('/update/status', methods=['GET'])
def get_update_status():
    """Récupère le statut des mises à jour"""
    import subprocess
    
    try:
        # Vérifier si on est dans un repo Git
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                'git_available': False,
                'error': 'Pas un repository Git'
            })
        
        # Obtenir la branche actuelle
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        current_branch = result.stdout.strip() if result.returncode == 0 else 'unknown'
        
        # Obtenir le dernier commit
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%s|%an|%ad', '--date=iso'],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        commit_info = {}
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split('|')
            if len(parts) >= 4:
                commit_info = {
                    'hash': parts[0][:8],
                    'message': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                }
        
        # Vérifier s'il y a des mises à jour disponibles
        subprocess.run(['git', 'fetch', 'origin'], 
                      cwd=os.path.dirname(os.path.dirname(__file__)),
                      capture_output=True)
        
        update_branch = os.getenv('UPDATE_BRANCH', 'master')
        result = subprocess.run(
            ['git', 'rev-list', '--count', f'HEAD..origin/{update_branch}'],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        updates_available = 0
        if result.returncode == 0 and result.stdout.strip().isdigit():
            updates_available = int(result.stdout.strip())
        
        return jsonify({
            'git_available': True,
            'auto_update_enabled': os.getenv('AUTO_UPDATE_ENABLED', 'True').lower() == 'true',
            'current_branch': current_branch,
            'update_branch': update_branch,
            'current_commit': commit_info,
            'updates_available': updates_available,
            'can_update': updates_available > 0
        })
        
    except Exception as e:
        return jsonify({
            'git_available': False,
            'error': str(e)
        })

