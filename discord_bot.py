import discord
import asyncio
import threading
import os
from datetime import datetime
from typing import Optional, Callable

class DiscordMonitor:
    def __init__(self):
        self.client = None
        self.token = None
        self.guild_id = None
        self.channel_id = None
        self.message_callback = None
        self.status_callback = None
        self.is_running = False
        self.bot_thread = None
        
    def setup(self, token: str, guild_id: int, channel_id: int, 
              message_callback: Callable = None, status_callback: Callable = None):
        """Configure le bot Discord avec les paramètres nécessaires"""
        self.token = token
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_callback = message_callback
        self.status_callback = status_callback
        
        # Configuration des intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        self.client = discord.Client(intents=intents)
        self._setup_events()
    
    def _setup_events(self):
        """Configure les événements Discord"""
        
        @self.client.event
        async def on_ready():
            print(f'Bot connecté en tant que {self.client.user}')
            
            # Vérifier que le serveur et le canal existent
            guild = self.client.get_guild(self.guild_id)
            if guild is None:
                error_msg = f"Serveur Discord avec l'ID {self.guild_id} non trouvé"
                print(error_msg)
                if self.status_callback:
                    self.status_callback("error", error_msg)
                return
            
            channel = guild.get_channel(self.channel_id)
            if channel is None:
                error_msg = f"Canal Discord avec l'ID {self.channel_id} non trouvé"
                print(error_msg)
                if self.status_callback:
                    self.status_callback("error", error_msg)
                return
            
            success_msg = f"Bot connecté et surveille le canal #{channel.name} sur {guild.name}"
            print(success_msg)
            if self.status_callback:
                self.status_callback("connected", success_msg)
        
        @self.client.event
        async def on_message(message):
            # Ignorer les messages du bot lui-même
            if message.author == self.client.user:
                return
            
            # Vérifier si le message provient du canal surveillé
            if message.channel.id == self.channel_id:
                message_data = {
                    'id': message.id,
                    'content': message.content,
                    'author': {
                        'name': message.author.display_name,
                        'username': message.author.name,
                        'avatar_url': str(message.author.avatar.url) if message.author.avatar else None
                    },
                    'channel': {
                        'name': message.channel.name,
                        'id': message.channel.id
                    },
                    'guild': {
                        'name': message.guild.name,
                        'id': message.guild.id
                    },
                    'timestamp': message.created_at.isoformat(),
                    'attachments': [
                        {
                            'filename': att.filename,
                            'url': att.url,
                            'size': att.size
                        } for att in message.attachments
                    ]
                }
                
                print(f"Nouveau message de {message.author.display_name}: {message.content}")
                
                # Appeler le callback si défini
                if self.message_callback:
                    self.message_callback(message_data)
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            error_msg = f"Erreur Discord: {event}"
            print(error_msg)
            if self.status_callback:
                self.status_callback("error", error_msg)
    
    def start(self):
        """Démarre le bot Discord dans un thread séparé"""
        if self.is_running:
            return False, "Le bot est déjà en cours d'exécution"
        
        if not all([self.token, self.guild_id, self.channel_id]):
            return False, "Configuration incomplète"
        
        def run_bot():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.client.start(self.token))
            except Exception as e:
                error_msg = f"Erreur lors du démarrage du bot: {str(e)}"
                print(error_msg)
                if self.status_callback:
                    self.status_callback("error", error_msg)
                self.is_running = False
        
        self.bot_thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_thread.start()
        self.is_running = True
        
        return True, "Bot Discord démarré"
    
    def stop(self):
        """Arrête le bot Discord"""
        if not self.is_running:
            return False, "Le bot n'est pas en cours d'exécution"
        
        if self.client and not self.client.is_closed():
            asyncio.run_coroutine_threadsafe(self.client.close(), self.client.loop)
        
        self.is_running = False
        return True, "Bot Discord arrêté"
    
    def get_status(self):
        """Retourne le statut actuel du bot"""
        if not self.is_running:
            return "disconnected"
        elif self.client and self.client.is_ready():
            return "connected"
        else:
            return "connecting"


    def fetch_message_history(self, limit=None, after=None):
        """Récupère l'historique des messages du canal"""
        if not self.client or not self.is_running:
            raise Exception("Bot Discord non connecté")
        
        async def _fetch_messages():
            try:
                guild = self.client.get_guild(self.guild_id)
                if not guild:
                    raise Exception(f"Serveur {self.guild_id} non trouvé")
                
                channel = guild.get_channel(self.channel_id)
                if not channel:
                    raise Exception(f"Canal {self.channel_id} non trouvé")
                
                messages = []
                async for message in channel.history(limit=limit, after=after):
                    message_data = {
                        'id': str(message.id),
                        'content': message.content,
                        'author': {
                            'id': str(message.author.id),
                            'name': message.author.display_name,
                            'username': message.author.name,
                            'avatar': str(message.author.avatar.url) if message.author.avatar else None
                        },
                        'timestamp': message.created_at.isoformat(),
                        'edited_timestamp': message.edited_at.isoformat() if message.edited_at else None,
                        'attachments': [
                            {
                                'id': str(att.id),
                                'filename': att.filename,
                                'url': att.url,
                                'size': att.size
                            } for att in message.attachments
                        ],
                        'embeds': len(message.embeds),
                        'reactions': [
                            {
                                'emoji': str(reaction.emoji),
                                'count': reaction.count
                            } for reaction in message.reactions
                        ]
                    }
                    messages.append(message_data)
                    
                    # Envoyer le message via callback si configuré
                    if self.message_callback:
                        self.message_callback(message_data)
                
                print(f"📥 Récupéré {len(messages)} messages de l'historique")
                return messages
                
            except Exception as e:
                print(f"❌ Erreur lors de la récupération: {e}")
                raise e
        
        # Exécuter dans la boucle d'événements du bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_fetch_messages())
        finally:
            loop.close()
    
    def get_channel_name(self):
        """Récupère le nom du canal Discord"""
        if not self.client or not self.is_running:
            raise Exception("Bot Discord non connecté")
        
        guild = self.client.get_guild(self.guild_id)
        if not guild:
            raise Exception(f"Serveur {self.guild_id} non trouvé")
        
        channel = guild.get_channel(self.channel_id)
        if not channel:
            raise Exception(f"Canal {self.channel_id} non trouvé")
        
        return channel.name
    
    def create_messages_backup(self):
        """Crée une sauvegarde de tous les messages avant suppression"""
        import json
        from datetime import datetime
        
        try:
            # Récupérer tous les messages
            messages = self.fetch_message_history()
            
            # Créer le fichier de sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            channel_name = self.get_channel_name()
            backup_filename = f"backup_messages_{channel_name}_{timestamp}.json"
            backup_path = os.path.join(os.path.dirname(__file__), 'backups', backup_filename)
            
            # Créer le dossier backups s'il n'existe pas
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Sauvegarder les données
            backup_data = {
                'metadata': {
                    'channel_id': str(self.channel_id),
                    'channel_name': channel_name,
                    'guild_id': str(self.guild_id),
                    'backup_timestamp': datetime.now().isoformat(),
                    'message_count': len(messages)
                },
                'messages': messages
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Sauvegarde créée: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            raise e
    
    def delete_all_messages(self):
        """Supprime tous les messages du canal (ACTION CRITIQUE)"""
        if not self.client or not self.is_running:
            raise Exception("Bot Discord non connecté")
        
        async def _delete_messages():
            try:
                guild = self.client.get_guild(self.guild_id)
                if not guild:
                    raise Exception(f"Serveur {self.guild_id} non trouvé")
                
                channel = guild.get_channel(self.channel_id)
                if not channel:
                    raise Exception(f"Canal {self.channel_id} non trouvé")
                
                # Vérifier les permissions
                permissions = channel.permissions_for(guild.me)
                if not permissions.manage_messages:
                    raise Exception("Le bot n'a pas la permission de supprimer les messages")
                
                deleted_count = 0
                
                # Supprimer les messages par batch (Discord limite à 100 messages de moins de 14 jours)
                while True:
                    messages = []
                    async for message in channel.history(limit=100):
                        messages.append(message)
                    
                    if not messages:
                        break
                    
                    # Séparer les messages récents (< 14 jours) des anciens
                    from datetime import datetime, timedelta
                    cutoff = datetime.utcnow() - timedelta(days=14)
                    
                    recent_messages = [msg for msg in messages if msg.created_at > cutoff]
                    old_messages = [msg for msg in messages if msg.created_at <= cutoff]
                    
                    # Supprimer les messages récents en batch
                    if recent_messages:
                        try:
                            await channel.delete_messages(recent_messages)
                            deleted_count += len(recent_messages)
                            print(f"🗑️ Supprimé {len(recent_messages)} messages récents")
                        except Exception as e:
                            print(f"⚠️ Erreur suppression batch: {e}")
                            # Fallback: supprimer un par un
                            for message in recent_messages:
                                try:
                                    await message.delete()
                                    deleted_count += 1
                                except:
                                    pass
                    
                    # Supprimer les anciens messages un par un
                    for message in old_messages:
                        try:
                            await message.delete()
                            deleted_count += 1
                            # Délai pour éviter le rate limiting
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            print(f"⚠️ Impossible de supprimer le message {message.id}: {e}")
                    
                    print(f"🗑️ Progression: {deleted_count} messages supprimés")
                    
                    # Délai entre les batches
                    if messages:
                        await asyncio.sleep(1)
                
                print(f"✅ Suppression terminée: {deleted_count} messages supprimés")
                return deleted_count
                
            except Exception as e:
                print(f"❌ Erreur lors de la suppression: {e}")
                raise e
        
        # Exécuter dans la boucle d'événements du bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_delete_messages())
        finally:
            loop.close()
    
    def get_messages_stats(self):
        """Récupère les statistiques des messages du canal"""
        if not self.client or not self.is_running:
            raise Exception("Bot Discord non connecté")
        
        async def _get_stats():
            try:
                guild = self.client.get_guild(self.guild_id)
                if not guild:
                    raise Exception(f"Serveur {self.guild_id} non trouvé")
                
                channel = guild.get_channel(self.channel_id)
                if not channel:
                    raise Exception(f"Canal {self.channel_id} non trouvé")
                
                # Compter les messages par période
                from datetime import datetime, timedelta
                now = datetime.utcnow()
                
                stats = {
                    'channel_name': channel.name,
                    'total_messages': 0,
                    'last_24h': 0,
                    'last_7d': 0,
                    'last_30d': 0,
                    'authors': {},
                    'last_message': None
                }
                
                cutoff_24h = now - timedelta(hours=24)
                cutoff_7d = now - timedelta(days=7)
                cutoff_30d = now - timedelta(days=30)
                
                async for message in channel.history(limit=1000):  # Limiter pour éviter timeout
                    stats['total_messages'] += 1
                    
                    # Compter par période
                    if message.created_at > cutoff_24h:
                        stats['last_24h'] += 1
                    if message.created_at > cutoff_7d:
                        stats['last_7d'] += 1
                    if message.created_at > cutoff_30d:
                        stats['last_30d'] += 1
                    
                    # Compter par auteur
                    author_name = message.author.display_name
                    if author_name not in stats['authors']:
                        stats['authors'][author_name] = 0
                    stats['authors'][author_name] += 1
                    
                    # Premier message = le plus récent
                    if stats['last_message'] is None:
                        stats['last_message'] = {
                            'content': message.content[:100] + '...' if len(message.content) > 100 else message.content,
                            'author': author_name,
                            'timestamp': message.created_at.isoformat()
                        }
                
                return stats
                
            except Exception as e:
                print(f"❌ Erreur lors de la récupération des stats: {e}")
                raise e
        
        # Exécuter dans la boucle d'événements du bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_get_stats())
        finally:
            loop.close()

