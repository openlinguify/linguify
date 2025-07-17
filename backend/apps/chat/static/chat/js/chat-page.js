/**
 * JavaScript pour la page de chat dédiée
 * Interface complète de messagerie style Discord/Slack
 * Version: 2025-07-13.4 - Fixed message display and participant names
 */

// Initialiser les tooltips et améliorations UX
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Ajouter des effets visuels pour les boutons d'appel
    document.querySelectorAll('.btn-conv-action[title*="appel"]').forEach(button => {
        // Effet de survol amélioré
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.15)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Effet de clic
        button.addEventListener('click', function() {
            // Animation de clic
            this.style.transform = 'scale(0.9)';
            setTimeout(() => {
                this.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 100);
            }, 100);
        });
    });
    
    // Animation d'apparition des boutons quand une conversation est sélectionnée
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.target.id === 'chat-header' && mutation.type === 'attributes') {
                const chatHeader = document.getElementById('chat-header');
                const callButtons = chatHeader.querySelectorAll('.btn-conv-action[title*="appel"]');
                
                if (chatHeader.style.display !== 'none') {
                    // Animation d'apparition des boutons
                    callButtons.forEach((button, index) => {
                        button.style.opacity = '0';
                        button.style.transform = 'scale(0.5) translateY(20px)';
                        
                        setTimeout(() => {
                            button.style.transition = 'all 0.4s ease-out';
                            button.style.opacity = '1';
                            button.style.transform = 'scale(1) translateY(0)';
                        }, index * 100 + 200);
                    });
                }
            }
        });
    });
    
    const chatHeader = document.getElementById('chat-header');
    if (chatHeader) {
        observer.observe(chatHeader, { attributes: true, attributeFilter: ['style'] });
    }
});

class ChatPage {
    constructor() {
        this.currentConversation = null;
        this.conversations = new Map();
        this.websockets = {
            chat: null,
            status: null,
            notifications: null
        };
        
        this.init();
    }

    init() {
        console.log('[ChatPage] Initialisation... (WebSockets disabled)');
        
        if (!window.currentUserId) {
            console.error('[ChatPage] currentUserId manquant');
            return;
        }
        
        this.setupEventListeners();
        this.loadConversations();
        // WebSockets désactivés temporairement pour éviter les erreurs
        // this.connectWebSockets();
        
        console.log('[ChatPage] Initialisé avec succès');
    }

    setupEventListeners() {
        // Nouvelle conversation
        const newConvBtn = document.getElementById('new-conversation-btn');
        if (newConvBtn) {
            newConvBtn.addEventListener('click', () => this.showNewConversationModal());
        }

        // Recherche conversations
        const searchInput = document.getElementById('search-conversations');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchConversations(e.target.value));
        }

        // Envoi de message
        const sendBtn = document.getElementById('send-message');
        const messageInput = document.getElementById('message-input');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }

        // Toggle sidebar mobile
        const mobileToggle = document.getElementById('mobile-chat-toggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => this.toggleMobileSidebar());
        }

        // Recherche utilisateurs dans modal
        const userSearch = document.getElementById('user-search');
        if (userSearch) {
            userSearch.addEventListener('input', (e) => this.searchUsers(e.target.value));
        }

        // Boutons d'appel
        this.setupCallButtons();
    }

    setupCallButtons() {
        // Bouton appel audio
        const audioCallBtn = document.getElementById('audio-call-btn');
        if (audioCallBtn) {
            audioCallBtn.addEventListener('click', () => this.initiateCall('audio'));
        }

        // Bouton appel vidéo
        const videoCallBtn = document.getElementById('video-call-btn');
        if (videoCallBtn) {
            videoCallBtn.addEventListener('click', () => this.initiateCall('video'));
        }
    }

    async loadConversations() {
        try {
            console.log('[ChatPage] Chargement des conversations...');
            
            const response = await fetch('/chat/api/conversations/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayConversations(data.conversations);
                console.log(`[ChatPage] ${data.conversations.length} conversations chargées`);
            } else {
                console.error('[ChatPage] Erreur chargement conversations:', data.message);
                this.showError('Erreur lors du chargement des conversations');
            }
        } catch (error) {
            console.error('[ChatPage] Erreur:', error);
            this.showError('Impossible de charger les conversations');
        }
    }

    displayConversations(conversations) {
        const container = document.getElementById('conversations-list');
        if (!container) return;

        // Sauvegarder les conversations dans le Map pour référence
        this.conversations.clear();
        conversations.forEach(conv => {
            this.conversations.set(conv.id, conv);
        });

        if (conversations.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="bi bi-chat-dots" style="font-size: 3rem;"></i>
                    <p class="mt-2">Aucune conversation</p>
                    <small>Créez votre première conversation</small>
                </div>
            `;
            return;
        }

        container.innerHTML = conversations.map(conv => {
            const participant = conv.participant;
            const lastMessage = conv.last_message;
            
            return `
                <div class="conversation-item d-flex align-items-center" 
                     data-conversation-id="${conv.id}"
                     onclick="chatPage.openConversation(${conv.id})">
                    <div class="conversation-avatar position-relative">
                        ${participant ? participant.username.charAt(0).toUpperCase() : '?'}
                        ${participant && participant.is_online ? '<div class="online-indicator"></div>' : ''}
                    </div>
                    <div class="conversation-info">
                        <div class="conversation-name">
                            ${participant ? participant.username : 'Conversation'}
                        </div>
                        <div class="conversation-preview">
                            ${lastMessage ? lastMessage.content.substring(0, 50) + '...' : 'Aucun message'}
                        </div>
                    </div>
                    <div class="conversation-meta">
                        ${lastMessage ? this.formatTime(lastMessage.timestamp) : ''}
                        ${conv.unread_count > 0 ? `<div class="badge bg-primary rounded-pill">${conv.unread_count}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    async openConversation(conversationId) {
        try {
            console.log(`[ChatPage] Ouverture conversation ${conversationId}`);
            
            // Marquer comme active
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector(`[data-conversation-id="${conversationId}"]`)?.classList.add('active');
            
            this.currentConversation = conversationId;
            
            // Trouver les infos de la conversation dans la liste
            const conversationData = this.conversations.get(conversationId);
            
            // Charger les messages
            const response = await fetch(`/chat/api/conversations/${conversationId}/messages/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showConversationArea();
                this.updateConversationHeader(conversationData);
                this.displayMessages(data.messages);
                // WebSocket désactivé temporairement
                // this.connectToChatWebSocket(conversationId);
                
                // Masquer sidebar sur mobile
                if (window.innerWidth < 768) {
                    this.hideMobileSidebar();
                }
            } else {
                console.error('[ChatPage] Erreur chargement messages:', data.message);
                this.showError('Erreur lors du chargement des messages');
            }
        } catch (error) {
            console.error('[ChatPage] Erreur ouverture conversation:', error);
            this.showError('Impossible d\'ouvrir la conversation');
        }
    }

    showConversationArea() {
        document.getElementById('no-conversation').style.display = 'none';
        document.getElementById('conversation-area').style.display = 'flex';
        document.getElementById('chat-header').style.display = 'block';
    }

    hideConversationArea() {
        document.getElementById('no-conversation').style.display = 'flex';
        document.getElementById('conversation-area').style.display = 'none';
        document.getElementById('chat-header').style.display = 'none';
    }

    updateConversationHeader(conversation) {
        if (!conversation || !conversation.participant) return;
        
        const participantName = document.getElementById('current-participant-name');
        const participantStatus = document.getElementById('current-participant-status');
        const participantAvatar = document.getElementById('current-participant-avatar');
        
        if (participantName) {
            participantName.textContent = conversation.participant.username;
        }
        
        if (participantAvatar) {
            participantAvatar.textContent = conversation.participant.username.charAt(0).toUpperCase();
        }
        
        if (participantStatus) {
            participantStatus.textContent = conversation.participant.is_online ? 'En ligne' : 'Hors ligne';
            participantStatus.style.color = conversation.participant.is_online ? '#28a745' : '#6c757d';
        }
    }

    displayMessages(messages) {
        const container = document.getElementById('messages-area');
        if (!container) return;

        console.log('[ChatPage] Displaying messages:', messages);

        container.innerHTML = messages.map(msg => {
            console.log('[ChatPage] Message:', msg.content, 'is_own_message:', msg.is_own_message);
            const isOwn = msg.is_own_message === true;
            const messageClass = isOwn ? 'own' : 'other';
            console.log('[ChatPage] Message class:', messageClass);
            
            return `
                <div class="message ${messageClass}">
                    <div class="message-bubble">
                        <div class="message-content">${this.escapeHtml(msg.content)}</div>
                        <div class="message-time">${this.formatTime(msg.timestamp)}</div>
                    </div>
                </div>
            `;
        }).join('');

        // Scroll vers le bas avec un petit délai pour s'assurer que le DOM est mis à jour
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 10);
    }

    async sendMessage() {
        const input = document.getElementById('message-input');
        if (!input || !this.currentConversation) return;

        const message = input.value.trim();
        if (!message) return;

        // Vider l'input immédiatement
        input.value = '';

        try {
            // Envoyer le message via l'API REST pour le sauvegarder en base
            const response = await fetch('/chat/api/messages/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    conversation_id: this.currentConversation,
                    message: message
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Ajouter le message à l'interface
                this.addMessageToUI(message, true);
                
                // Recharger les conversations pour mettre à jour la liste
                this.loadConversations();
            } else {
                console.error('[ChatPage] Error sending message:', data.message);
                // Restaurer le message dans l'input en cas d'erreur
                input.value = message;
                alert('Erreur lors de l\'envoi du message');
            }
        } catch (error) {
            console.error('[ChatPage] Failed to send message:', error);
            // Restaurer le message dans l'input en cas d'erreur
            input.value = message;
            alert('Erreur lors de l\'envoi du message');
        }
    }

    addMessageToUI(message, isOwn = false) {
        const container = document.getElementById('messages-area');
        if (!container) return;

        const messageDiv = document.createElement('div');
        const messageClass = isOwn ? 'own' : 'other';
        messageDiv.className = `message ${messageClass}`;
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <div class="message-content">${this.escapeHtml(message)}</div>
                <div class="message-time">${this.formatTime(new Date().toISOString())}</div>
            </div>
        `;

        container.appendChild(messageDiv);
        // Scroll vers le bas avec un petit délai
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 10);
    }

    connectWebSockets() {
        // WebSockets temporairement désactivés pour éviter les erreurs
        console.log('[ChatPage] WebSockets disabled temporarily');
        return;
        
        // this.connectStatusWebSocket();
        // this.connectNotificationsWebSocket();
    }

    connectStatusWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/status/`;
        
        this.websockets.status = new WebSocket(wsUrl);
        
        this.websockets.status.onopen = () => {
            console.log('[ChatPage] Status WebSocket connecté');
        };
        
        this.websockets.status.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleStatusUpdate(data);
        };
        
        this.websockets.status.onclose = () => {
            console.log('[ChatPage] Status WebSocket déconnecté');
            // Reconnexion automatique désactivée temporairement
            // setTimeout(() => this.connectStatusWebSocket(), 5000);
        };
    }

    connectNotificationsWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/notifications/`;
        
        this.websockets.notifications = new WebSocket(wsUrl);
        
        this.websockets.notifications.onopen = () => {
            console.log('[ChatPage] Notifications WebSocket connecté');
        };
        
        this.websockets.notifications.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleNotification(data);
        };
        
        this.websockets.notifications.onclose = () => {
            console.log('[ChatPage] Notifications WebSocket déconnecté');
            // Reconnexion automatique désactivée temporairement
            // setTimeout(() => this.connectNotificationsWebSocket(), 5000);
        };
    }

    connectToChatWebSocket(conversationId) {
        // WebSocket désactivé temporairement
        console.log('[ChatPage] Chat WebSocket disabled temporarily');
        return;
        
        // if (this.websockets.chat) {
        //     this.websockets.chat.close();
        // }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/chat/${conversationId}/`;
        
        this.websockets.chat = new WebSocket(wsUrl);
        
        this.websockets.chat.onopen = () => {
            console.log(`[ChatPage] Chat WebSocket connecté à la conversation ${conversationId}`);
        };
        
        this.websockets.chat.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleChatMessage(data);
        };
        
        this.websockets.chat.onclose = () => {
            console.log('[ChatPage] Chat WebSocket déconnecté');
        };
    }

    handleChatMessage(data) {
        if (data.type === 'message' && data.conversation_id == this.currentConversation) {
            this.addMessageToUI(data.message, false);
        }
    }

    handleStatusUpdate(data) {
        if (data.type === 'user_status') {
            // Mettre à jour les indicateurs en ligne
            this.updateOnlineStatus(data.user_id, data.is_online);
        }
    }

    handleNotification(data) {
        if (data.type === 'new_message') {
            this.loadConversations(); // Recharger pour mettre à jour
        }
    }

    showNewConversationModal() {
        const modal = new bootstrap.Modal(document.getElementById('newConversationModal'));
        modal.show();
    }

    async searchUsers(query) {
        if (query.length < 2) {
            document.getElementById('user-search-results').innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/chat/api/users/search/?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayUserSearchResults(data.users);
            }
        } catch (error) {
            console.error('[ChatPage] Erreur recherche utilisateurs:', error);
        }
    }

    displayUserSearchResults(users) {
        const container = document.getElementById('user-search-results');
        if (!container) return;

        if (users.length === 0) {
            container.innerHTML = '<p class="text-muted">Aucun utilisateur trouvé</p>';
            return;
        }

        container.innerHTML = users.map(user => `
            <div class="d-flex align-items-center p-2 border-bottom user-result" 
                 style="cursor: pointer;" 
                 onclick="chatPage.startConversation(${user.id})">
                <div class="conversation-avatar me-3">
                    ${user.username.charAt(0).toUpperCase()}
                </div>
                <div>
                    <div class="fw-bold">${user.username}</div>
                    <small class="text-muted">${user.is_online ? 'En ligne' : 'Hors ligne'}</small>
                </div>
            </div>
        `).join('');
    }

    async startConversation(userId) {
        try {
            const response = await fetch('/chat/api/conversations/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify({ user_id: userId })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Fermer le modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('newConversationModal'));
                modal.hide();
                
                // Recharger les conversations et ouvrir la nouvelle
                await this.loadConversations();
                await this.openConversation(data.conversation_id);
            } else {
                this.showError('Erreur: ' + data.message);
            }
        } catch (error) {
            console.error('[ChatPage] Erreur création conversation:', error);
            this.showError('Impossible de créer la conversation');
        }
    }

    searchConversations(query) {
        const items = document.querySelectorAll('.conversation-item');
        items.forEach(item => {
            const name = item.querySelector('.conversation-name').textContent.toLowerCase();
            const visible = name.includes(query.toLowerCase());
            item.style.display = visible ? 'flex' : 'none';
        });
    }

    toggleMobileSidebar() {
        const sidebar = document.getElementById('chat-sidebar');
        sidebar.classList.toggle('show');
    }

    hideMobileSidebar() {
        const sidebar = document.getElementById('chat-sidebar');
        sidebar.classList.remove('show');
    }

    updateOnlineStatus(userId, isOnline) {
        // Mettre à jour les indicateurs en ligne dans la liste
        // Implementation selon le design
    }

    showError(message) {
        console.error('[ChatPage]', message);
        // Vous pouvez ajouter une notification toast ici
    }

    // Fonctions utilitaires
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Maintenant';
        if (diff < 3600000) return Math.floor(diff / 60000) + 'm';
        if (diff < 86400000) return Math.floor(diff / 3600000) + 'h';
        return date.toLocaleDateString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ===== FONCTIONNALITÉS D'APPEL =====
    
    async initiateCall(callType) {
        if (!this.currentConversation) {
            alert('Veuillez sélectionner une conversation');
            return;
        }
        
        // Vérifier s'il y a déjà un appel en cours
        const existingModal = document.getElementById('call-modal');
        if (existingModal) {
            alert('Un appel est déjà en cours');
            return;
        }

        try {
            // Obtenir l'autre participant de la conversation
            const conversation = this.conversations.get(this.currentConversation);
            const otherUser = conversation.participant;
            
            if (!otherUser) {
                alert('Impossible de trouver le destinataire');
                return;
            }

            console.log(`[ChatPage] Initiating ${callType} call to user ${otherUser.id}`);

            // Créer l'appel via l'API
            const response = await fetch('/chat/api/calls/initiate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    conversation_id: this.currentConversation,
                    receiver_id: otherUser.id,
                    call_type: callType
                })
            });

            const callData = await response.json();

            if (callData.success) {
                console.log('[ChatPage] Call initiated:', callData);
                this.startCall(callData, callType, otherUser);
            } else {
                alert('Erreur lors de l\'initiation de l\'appel: ' + callData.error);
            }
        } catch (error) {
            console.error('[ChatPage] Error initiating call:', error);
            alert('Erreur lors de l\'initiation de l\'appel');
        }
    }

    async startCall(callData, callType, otherUser) {
        // Créer l'interface d'appel
        this.createCallInterface(callData, callType, otherUser);
        
        // Initialiser WebRTC
        await this.initializeWebRTC(callData.room_id, callType === 'video');
        
        // Connecter au WebSocket d'appel
        this.connectCallWebSocket(callData.room_id);
    }

    createCallInterface(callData, callType, otherUser) {
        // Supprimer toute modal d'appel existante
        const existingModal = document.getElementById('call-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Créer une modal d'appel
        const callModal = document.createElement('div');
        callModal.id = 'call-modal';
        callModal.className = 'call-modal';
        callModal.innerHTML = `
            <div class="call-container">
                <div class="call-header">
                    <h3>${callType === 'video' ? '📹' : '📞'} Appel ${callType}</h3>
                    <div class="call-status" id="call-status">Connexion...</div>
                </div>
                
                <div class="call-participants">
                    <div class="participant-card">
                        <div class="participant-avatar">
                            <div class="avatar-placeholder">${otherUser.username.charAt(0).toUpperCase()}</div>
                        </div>
                        <div class="participant-name">${otherUser.username}</div>
                    </div>
                </div>
                
                <div class="call-videos" style="display: ${callType === 'video' ? 'block' : 'none'};">
                    <video id="localVideo" autoplay muted playsinline class="local-video"></video>
                    <video id="remoteVideo" autoplay playsinline class="remote-video"></video>
                </div>
                
                <div class="call-controls">
                    <button id="toggleAudio" class="call-btn call-btn-audio" title="Micro">
                        🎤
                    </button>
                    ${callType === 'video' ? `
                    <button id="toggleVideo" class="call-btn call-btn-video" title="Caméra">
                        📹
                    </button>
                    ` : ''}
                    <button id="endCall" class="call-btn call-btn-end" title="Raccrocher">
                        📞
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(callModal);
        
        // Event listeners pour les contrôles
        this.setupCallControls(callData.call_id);
    }

    setupCallControls(callId) {
        const toggleAudioBtn = document.getElementById('toggleAudio');
        const toggleVideoBtn = document.getElementById('toggleVideo');
        const endCallBtn = document.getElementById('endCall');
        
        if (toggleAudioBtn) {
            toggleAudioBtn.addEventListener('click', () => this.toggleAudio());
        }
        
        if (toggleVideoBtn) {
            toggleVideoBtn.addEventListener('click', () => this.toggleVideo());
        }
        
        if (endCallBtn) {
            endCallBtn.addEventListener('click', () => this.endCall(callId));
        }
    }

    async initializeWebRTC(roomId, videoEnabled) {
        try {
            // Configuration WebRTC
            this.peerConnection = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' },
                    { urls: 'stun:stun1.l.google.com:19302' }
                ]
            });

            // Obtenir les médias locaux
            const constraints = {
                audio: true,
                video: videoEnabled ? { width: 1280, height: 720 } : false
            };

            this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Afficher la vidéo locale
            const localVideo = document.getElementById('localVideo');
            if (localVideo && videoEnabled) {
                localVideo.srcObject = this.localStream;
            }

            // Ajouter les tracks à la connexion
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });

            // Gérer le stream distant
            this.peerConnection.ontrack = (event) => {
                const remoteVideo = document.getElementById('remoteVideo');
                if (remoteVideo) {
                    remoteVideo.srcObject = event.streams[0];
                }
            };

            // Gérer les candidats ICE
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate && this.callWebSocket) {
                    this.callWebSocket.send(JSON.stringify({
                        type: 'ice-candidate',
                        candidate: event.candidate
                    }));
                }
            };

            console.log('[ChatPage] WebRTC initialized successfully');
        } catch (error) {
            console.error('[ChatPage] Error initializing WebRTC:', error);
            alert('Erreur d\'accès aux médias. Vérifiez vos permissions.');
        }
    }

    connectCallWebSocket(roomId) {
        const wsUrl = `ws://${window.location.host}/ws/call/${roomId}/`;
        this.callWebSocket = new WebSocket(wsUrl);

        this.callWebSocket.onopen = () => {
            console.log('[ChatPage] Call WebSocket connected');
            this.updateCallStatus('Connecté');
        };

        this.callWebSocket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            await this.handleCallMessage(data);
        };

        this.callWebSocket.onclose = () => {
            console.log('[ChatPage] Call WebSocket disconnected');
            this.updateCallStatus('Déconnecté');
            
            // Fermer l'appel après 5 secondes si pas de reconnexion
            setTimeout(() => {
                const callModal = document.getElementById('call-modal');
                if (callModal && this.callWebSocket && this.callWebSocket.readyState !== WebSocket.OPEN) {
                    console.log('[ChatPage] Auto-ending call due to persistent disconnection');
                    this.handleCallEnded();
                }
            }, 5000);
        };
    }

    async handleCallMessage(data) {
        switch (data.type) {
            case 'offer':
                await this.handleOffer(data);
                break;
            case 'answer':
                await this.handleAnswer(data);
                break;
            case 'ice-candidate':
                await this.handleIceCandidate(data);
                break;
            case 'user-joined':
                this.handleUserJoined(data);
                break;
            case 'call-ended':
                this.handleCallEnded();
                break;
        }
    }

    async handleOffer(data) {
        if (!this.peerConnection) return;
        
        await this.peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);
        
        this.callWebSocket.send(JSON.stringify({
            type: 'answer',
            answer: answer
        }));
    }

    async handleAnswer(data) {
        if (!this.peerConnection) return;
        await this.peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
    }

    async handleIceCandidate(data) {
        if (!this.peerConnection || !data.candidate) return;
        await this.peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
    }

    handleUserJoined(data) {
        console.log('[ChatPage] User joined call:', data.username);
        this.updateCallStatus('En cours...');
        
        // Créer une offre si c'est nous qui avons initié l'appel
        if (this.peerConnection) {
            this.createOffer();
        }
    }

    async createOffer() {
        if (!this.peerConnection) return;
        
        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);
        
        this.callWebSocket.send(JSON.stringify({
            type: 'offer',
            offer: offer
        }));
    }

    toggleAudio() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                const btn = document.getElementById('toggleAudio');
                btn.textContent = audioTrack.enabled ? '🎤' : '🔇';
                btn.classList.toggle('muted', !audioTrack.enabled);
                
                // Notifier via WebSocket
                if (this.callWebSocket) {
                    this.callWebSocket.send(JSON.stringify({
                        type: 'mute-audio',
                        is_muted: !audioTrack.enabled
                    }));
                }
            }
        }
    }

    toggleVideo() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                const btn = document.getElementById('toggleVideo');
                btn.textContent = videoTrack.enabled ? '📹' : '📵';
                btn.classList.toggle('muted', !videoTrack.enabled);
                
                // Notifier via WebSocket
                if (this.callWebSocket) {
                    this.callWebSocket.send(JSON.stringify({
                        type: 'mute-video',
                        is_muted: !videoTrack.enabled
                    }));
                }
            }
        }
    }

    async endCall(callId) {
        try {
            // Notifier le serveur
            await fetch(`/chat/api/calls/${callId}/end/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin'
            });

            this.handleCallEnded();
        } catch (error) {
            console.error('[ChatPage] Error ending call:', error);
            this.handleCallEnded(); // Terminer quand même localement
        }
    }

    handleCallEnded() {
        // Arrêter les streams
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }

        // Fermer la connexion WebRTC
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }

        // Fermer le WebSocket d'appel
        if (this.callWebSocket) {
            this.callWebSocket.close();
            this.callWebSocket = null;
        }

        // Supprimer l'interface d'appel
        const callModal = document.getElementById('call-modal');
        if (callModal) {
            callModal.remove();
        }

        console.log('[ChatPage] Call ended successfully');
    }

    updateCallStatus(status) {
        const statusElement = document.getElementById('call-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    // ===== FIN FONCTIONNALITÉS D'APPEL =====
}

// Initialiser la page de chat
document.addEventListener('DOMContentLoaded', function() {
    window.chatPage = new ChatPage();
});