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

