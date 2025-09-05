# Discord Monitor v2.3 - Redémarrage Automatique du Service

## 🔄 **Amélioration majeure**

### Redémarrage automatique après mise à jour
Le système de mise à jour **redémarre maintenant automatiquement le service** pour s'assurer que tous les changements backend sont pris en compte.

## ⚡ **Problème résolu**

### Avant v2.3
- ❌ Mise à jour Git uniquement
- ❌ Changements backend non pris en compte
- ❌ Nécessité de redémarrage manuel
- ❌ Interface pas synchronisée avec le backend

### Après v2.3
- ✅ Mise à jour Git + redémarrage automatique
- ✅ Tous les changements appliqués immédiatement
- ✅ Processus entièrement automatisé
- ✅ Reconnexion automatique de l'interface

## 🔧 **Fonctionnement**

### Séquence de mise à jour complète
1. **Sauvegarde** de la configuration actuelle
2. **Arrêt** du bot Discord si actif
3. **Mise à jour Git** (fetch, reset, clean)
4. **Restauration** de la configuration
5. **Redémarrage** du bot Discord si nécessaire
6. **Redémarrage** du service Flask/Python
7. **Reconnexion** automatique de l'interface

### Méthodes de redémarrage
Le système essaie plusieurs méthodes dans l'ordre :
```bash
# 1. systemd (recommandé)
systemctl restart discord-monitor

# 2. init.d (système classique)
service discord-monitor restart

# 3. supervisor (gestionnaire de processus)
supervisorctl restart discord-monitor

# 4. Fallback (arrêt forcé du processus)
pkill -f main.py
```

## 🎯 **Configuration**

### Variable de contrôle
```env
# Dans le fichier .env
AUTO_RESTART_SERVICE=True  # Active le redémarrage automatique
AUTO_RESTART_SERVICE=False # Désactive le redémarrage automatique
```

### Comportement selon la configuration
- **True** : Redémarrage automatique du service
- **False** : Mise à jour Git uniquement (comme avant)

## 🌐 **Expérience utilisateur**

### Interface pendant la mise à jour
1. **Confirmation** : "Êtes-vous sûr de vouloir mettre à jour l'application ? Cela redémarrera le service."
2. **Feedback** : "Mise à jour en cours..."
3. **Progression** : "Redémarrage du service en cours..."
4. **Reconnexion** : "Tentative de reconnexion 1/10..."
5. **Succès** : "Reconnexion réussie ! Rechargement de la page..."

### Reconnexion intelligente
- **Tentatives** : 10 maximum
- **Délai croissant** : 2s, 3s, 4s... jusqu'à 10s max
- **Timeout** : 5 secondes par tentative
- **Fallback** : Bouton de rechargement manuel si échec

## 🛡️ **Robustesse**

### Gestion des erreurs
- **Service non trouvé** : Fallback vers arrêt de processus
- **Permissions insuffisantes** : Tentative avec différentes méthodes
- **Timeout** : Arrêt forcé si nécessaire
- **Reconnexion échouée** : Interface de secours

### Sécurité
- **Délai de 2 secondes** avant redémarrage (réponse HTTP envoyée)
- **Thread séparé** pour éviter les blocages
- **Sauvegarde config** avant toute opération
- **Restauration automatique** en cas de problème

## 📱 **Interface améliorée**

### Messages informatifs
```javascript
// Progression détaillée
"Démarrage de la mise à jour..."
"Mise à jour effectuée avec succès"
"Redémarrage du service en cours..."
"Tentative de reconnexion 3/10..."
"Reconnexion réussie ! Rechargement de la page..."
```

### États visuels
- **Loading overlay** : "Redémarrage du service..."
- **Logs en temps réel** : Progression visible
- **Bouton de secours** : Si reconnexion échoue
- **Feedback immédiat** : Chaque étape documentée

## 🔄 **API améliorée**

### Réponse de mise à jour
```json
{
  "message": "Mise à jour effectuée avec succès - Service en cours de redémarrage",
  "results": [...],
  "config_restored": true,
  "bot_restarted": true,
  "service_restart": true
}
```

### Nouveau champ
- **service_restart** : Indique si le service va redémarrer
- Permet à l'interface de s'adapter au comportement

## 🚀 **Déploiement**

### Environnements supportés
- **systemd** : Ubuntu 16+, CentOS 7+, Debian 8+
- **init.d** : Systèmes classiques
- **supervisor** : Gestionnaires de processus
- **Processus direct** : Python lancé manuellement

### Configuration recommandée
```bash
# Créer un service systemd
sudo nano /etc/systemd/system/discord-monitor.service

[Unit]
Description=Discord Monitor Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/discord-monitor
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

# Activer le service
sudo systemctl enable discord-monitor
sudo systemctl start discord-monitor
```

## 🧪 **Tests**

### Scénarios de test
- [ ] Mise à jour avec redémarrage systemd
- [ ] Mise à jour avec redémarrage init.d
- [ ] Mise à jour avec supervisor
- [ ] Fallback vers arrêt de processus
- [ ] Reconnexion automatique réussie
- [ ] Reconnexion échouée → bouton manuel
- [ ] Configuration AUTO_RESTART_SERVICE=False
- [ ] Sauvegarde/restauration de config

### Validation
- [ ] Service redémarre correctement
- [ ] Configuration préservée
- [ ] Bot Discord fonctionne après redémarrage
- [ ] Interface se reconnecte automatiquement
- [ ] Logs informatifs affichés

## ⚠️ **Considérations**

### Permissions requises
- **systemctl** : Droits sudo ou service user
- **service** : Droits sudo
- **supervisorctl** : Accès supervisor
- **pkill** : Droits sur le processus

### Environnements de développement
- **Mode dev** : Peut désactiver AUTO_RESTART_SERVICE
- **Docker** : Nécessite configuration spécifique
- **PM2** : Ajouter commande PM2 dans les méthodes

## 🔄 **Migration**

### Depuis v2.2
- **Automatique** : Variable AUTO_RESTART_SERVICE ajoutée
- **Comportement** : Redémarrage activé par défaut
- **Compatibilité** : Peut être désactivé si problème

### Nouveaux déploiements
- **Service systemd** : Recommandé pour production
- **Configuration .env** : AUTO_RESTART_SERVICE=True
- **Tests** : Vérifier que le redémarrage fonctionne

---

**Version** : 2.3.0  
**Compatibilité** : Discord Monitor v2.2+  
**Changement majeur** : Redémarrage automatique du service  
**Impact** : Mises à jour complètement automatisées

