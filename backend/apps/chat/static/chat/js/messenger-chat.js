/**
 * Facebook Messenger Style Chat Integration pour Linguify
 * Chat fonctionnel avec connexion au backend community
 * Version: 2024-07-13.4 - Fixed message display and participant names
 */

class MessengerChat {
    constructor() {
        this.isMinimized = false;
        this.isInitialized = false;
        this.currentConversation = null;
        this.conversations = new Map();
        this.unreadCounts = new Map();
        this.websockets = {
            chat: null,
            status: null,
            notifications: null
        };
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        console.log('[MessengerChat] Initializing chat...');
        
        // Vérifier les variables globales
        if (!window.currentUserId) {
            console.error('[MessengerChat] currentUserId not found');
            return;
        }
        
        // Charger les conversations existantes
        this.loadConversations();
        
        // Événements pour le widget existant
        this.setupEventListeners();
        
        // WebSockets désactivés temporairement pour éviter les erreurs
        // this.connectWebSockets();
        
        this.isInitialized = true;
        console.log('[MessengerChat] Chat initialized successfully');
    }

    setupEventListeners() {
        // Bouton minimiser
        const minimizeBtn = document.getElementById('messenger-minimize');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', () => this.toggleMinimize());
        }

        // Bouton fermer
        const closeBtn = document.getElementById('messenger-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        // Bouton retour conversation
        const backBtn = document.getElementById('conversation-back');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showConversationsList());
        }

        // Nouvelle conversation
        const newConvBtn = document.getElementById('new-conversation-btn');
        if (newConvBtn) {
            newConvBtn.addEventListener('click', () => this.showNewConversationDialog());
        }

        // Recherche conversations
        const searchInput = document.getElementById('search-conversations');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchConversations(e.target.value));
        }

        // Envoi de message
        const sendBtn = document.getElementById('send-message');
        const messageInput = document.getElementById('message-input');
        
        console.log('[MessengerChat] Éléments trouvés:', { sendBtn, messageInput });
        
        if (sendBtn && messageInput) {
            console.log('[MessengerChat] Attaching event listeners to message input');
            sendBtn.addEventListener('click', () => {
                console.log('[MessengerChat] Send button clicked');
                this.sendMessage();
            });
            messageInput.addEventListener('keypress', (e) => {
                console.log('[MessengerChat] Key pressed:', e.key);
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
            messageInput.addEventListener('focus', () => {
                console.log('[MessengerChat] Input focused');
            });
            messageInput.addEventListener('click', () => {
                console.log('[MessengerChat] Input clicked');
            });
        } else {
            console.error('[MessengerChat] Send button or message input not found');
        }

        // Boutons d'appel
        this.setupCallButtons();
        
        // Bouton voir le profil
        this.setupViewProfileButton();
    }

    setupCallButtons() {
        // Bouton appel audio
        const audioCallBtn = document.getElementById('messenger-audio-call-btn');
        if (audioCallBtn) {
            audioCallBtn.addEventListener('click', () => this.initiateCall('audio'));
            console.log('[MessengerChat] Audio call button listener attached');
        } else {
            console.warn('[MessengerChat] Audio call button not found');
        }

        // Bouton appel vidéo
        const videoCallBtn = document.getElementById('messenger-video-call-btn');
        if (videoCallBtn) {
            videoCallBtn.addEventListener('click', () => this.initiateCall('video'));
            console.log('[MessengerChat] Video call button listener attached');
        } else {
            console.warn('[MessengerChat] Video call button not found');
        }
    }

    setupViewProfileButton() {
        const viewProfileBtn = document.getElementById('view-profile-btn');
        if (viewProfileBtn) {
            viewProfileBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.viewUserProfile();
            });
            console.log('[MessengerChat] View profile button listener attached');
        } else {
            console.warn('[MessengerChat] View profile button not found');
        }
    }

    viewUserProfile() {
        if (!this.currentConversation) {
            console.warn('[MessengerChat] No current conversation to view profile');
            alert('Aucune conversation active pour voir le profil');
            return;
        }

        // Récupérer les données de la conversation actuelle
        const conversation = this.conversations.get(this.currentConversation);
        if (!conversation || !conversation.participant) {
            console.warn('[MessengerChat] No participant data found');
            alert('Impossible de trouver les données du participant');
            return;
        }

        const username = conversation.participant.username;
        
        console.log(`[MessengerChat] Viewing profile for user ${username}`);
        
        // Rediriger vers la page de profil (format court recommandé)
        // Normaliser le username en minuscules pour l'URL
        const normalizedUsername = username.toLowerCase();
        window.open(`/u/${normalizedUsername}/`, '_blank');
    }

    async loadConversations() {
        try {
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
                this.updateUnreadBadge(data.conversations);
            } else {
                console.error('[MessengerChat] Error loading conversations:', data.message);
            }
        } catch (error) {
            console.error('[MessengerChat] Failed to load conversations:', error);
        }
    }

    displayConversations(conversations) {
        const container = document.getElementById('conversations-container');
        if (!container) return;

        // Sauvegarder les conversations dans le Map pour référence
        this.conversations.clear();
        conversations.forEach(conv => {
            this.conversations.set(conv.id, conv);
        });

        if (conversations.length === 0) {
            container.innerHTML = `
                <div class="empty-state text-center p-3">
                    <i class="bi bi-chat-dots text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2">Aucune conversation</p>
                    <small class="text-muted">Démarrez une nouvelle conversation</small>
                </div>
            `;
            return;
        }

        container.innerHTML = conversations.map(conv => `
            <div class="conversation-item" data-conversation-id="${conv.id}" onclick="messengerChat.openConversation(${conv.id})">
                <div class="conversation-avatar">
                    <div class="avatar-circle">
                        ${conv.participant ? conv.participant.username.charAt(0).toUpperCase() : '?'}
                    </div>
                    ${conv.participant && conv.participant.is_online ? '<div class="online-indicator"></div>' : ''}
                </div>
                <div class="conversation-info">
                    <div class="conversation-name">
                        ${conv.participant ? conv.participant.username : 'Conversation'}
                    </div>
                    <div class="conversation-preview">
                        ${conv.last_message ? conv.last_message.content.substring(0, 50) + '...' : 'Pas de messages'}
                    </div>
                </div>
                <div class="conversation-meta">
                    ${conv.last_message ? this.formatTime(conv.last_message.timestamp) : ''}
                    ${conv.unread_count > 0 ? `<span class="unread-badge">${conv.unread_count}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    async openConversation(conversationId) {
        try {
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
                this.showConversationView();
                this.updateConversationHeader(conversationData);
                this.displayMessages(data.messages);
                // WebSocket désactivé temporairement
                // this.connectToChatWebSocket(conversationId);
            } else {
                console.error('[MessengerChat] Error loading messages:', data.message);
            }
        } catch (error) {
            console.error('[MessengerChat] Failed to load messages:', error);
        }
    }

    updateConversationHeader(conversation) {
        if (!conversation || !conversation.participant) return;
        
        const participantName = document.getElementById('participant-name');
        const participantAvatar = document.getElementById('participant-avatar');
        const participantStatus = document.getElementById('participant-status');
        const statusIndicator = document.getElementById('status-indicator');
        
        if (participantName) {
            participantName.textContent = conversation.participant.username;
        }
        
        if (participantAvatar) {
            // Nouveau design avec avatar-letter
            const avatarLetter = participantAvatar.querySelector('.avatar-letter');
            if (avatarLetter) {
                avatarLetter.textContent = conversation.participant.username.charAt(0).toUpperCase();
            }
        }
        
        if (participantStatus) {
            const statusText = participantStatus.querySelector('.status-text-modern');
            const lastSeen = participantStatus.querySelector('.last-seen');
            
            if (statusText) {
                statusText.textContent = conversation.participant.is_online ? 'En ligne' : 'Hors ligne';
            }
            
            if (lastSeen) {
                lastSeen.textContent = conversation.participant.is_online ? '• Actif maintenant' : '• Vu récemment';
            }
        }
        
        // Mettre à jour l'indicateur de statut
        if (statusIndicator) {
            statusIndicator.className = conversation.participant.is_online ? 'status-indicator online' : 'status-indicator';
        }
    }

    displayMessages(messages) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        console.log('[MessengerChat] Displaying messages:', messages);

        container.innerHTML = messages.map(msg => {
            console.log('[MessengerChat] Message:', msg.content, 'is_own_message:', msg.is_own_message);
            return `
                <div class="message ${msg.is_own_message ? 'own' : 'other'}">
                    <div class="message-bubble">
                        <div class="message-content">${this.escapeHtml(msg.content)}</div>
                        <div class="message-time">${this.formatTime(msg.timestamp)}</div>
                    </div>
                </div>
            `;
        }).join('');

        // Scroll vers le bas
        container.scrollTop = container.scrollHeight;
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
                console.error('[MessengerChat] Error sending message:', data.message);
                // Restaurer le message dans l'input en cas d'erreur
                input.value = message;
                alert('Erreur lors de l\'envoi du message');
            }
        } catch (error) {
            console.error('[MessengerChat] Failed to send message:', error);
            // Restaurer le message dans l'input en cas d'erreur
            input.value = message;
            alert('Erreur lors de l\'envoi du message');
        }
    }

    addMessageToUI(message, isOwnMessage = false) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isOwnMessage ? 'own' : 'other'}`;
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <div class="message-content">${this.escapeHtml(message)}</div>
                <div class="message-time">${this.formatTime(new Date().toISOString())}</div>
            </div>
        `;

        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }

    connectWebSockets() {
        // WebSockets temporairement désactivés pour éviter les erreurs
        console.log('[MessengerChat] WebSockets disabled temporarily');
        return;
        
        // WebSocket pour le statut utilisateur
        // this.connectStatusWebSocket();
        
        // WebSocket pour les notifications
        // this.connectNotificationsWebSocket();
    }

    connectStatusWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/status/`;
        
        this.websockets.status = new WebSocket(wsUrl);
        
        this.websockets.status.onopen = () => {
            console.log('[MessengerChat] Status WebSocket connected');
        };
        
        this.websockets.status.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleStatusUpdate(data);
        };
        
        this.websockets.status.onclose = () => {
            console.log('[MessengerChat] Status WebSocket disconnected');
            // Reconnexion automatique désactivée temporairement
            // setTimeout(() => this.connectStatusWebSocket(), 5000);
        };
    }

    connectNotificationsWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/notifications/`;
        
        this.websockets.notifications = new WebSocket(wsUrl);
        
        this.websockets.notifications.onopen = () => {
            console.log('[MessengerChat] Notifications WebSocket connected');
        };
        
        this.websockets.notifications.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleNotification(data);
        };
        
        this.websockets.notifications.onclose = () => {
            console.log('[MessengerChat] Notifications WebSocket disconnected');
            // Reconnexion automatique désactivée temporairement
            // setTimeout(() => this.connectNotificationsWebSocket(), 5000);
        };
    }

    connectToChatWebSocket(conversationId) {
        // Fermer la connexion précédente si elle existe
        if (this.websockets.chat) {
            this.websockets.chat.close();
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/community/chat/${conversationId}/`;
        
        this.websockets.chat = new WebSocket(wsUrl);
        
        this.websockets.chat.onopen = () => {
            console.log(`[MessengerChat] Chat WebSocket connected to conversation ${conversationId}`);
        };
        
        this.websockets.chat.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleChatMessage(data);
        };
        
        this.websockets.chat.onclose = () => {
            console.log('[MessengerChat] Chat WebSocket disconnected');
        };
    }

    handleChatMessage(data) {
        if (data.type === 'message' && data.conversation_id == this.currentConversation) {
            // Ajouter le message reçu à l'interface
            this.addMessageToUI(data.message, false);
        }
    }

    handleStatusUpdate(data) {
        // Mettre à jour les statuts en ligne dans la liste des conversations
        if (data.type === 'user_status') {
            const userId = data.user_id;
            const isOnline = data.is_online;
            
            // Mettre à jour l'indicateur en ligne
            const indicators = document.querySelectorAll(`[data-user-id="${userId}"] .online-indicator`);
            indicators.forEach(indicator => {
                indicator.style.display = isOnline ? 'block' : 'none';
            });
        }
    }

    handleNotification(data) {
        // Gérer les notifications de nouveau message
        if (data.type === 'new_message') {
            this.loadConversations(); // Recharger pour mettre à jour les badges
        }
    }

    async showNewConversationDialog() {
        const query = prompt('Nom d\'utilisateur à rechercher:');
        if (!query) return;

        try {
            const response = await fetch(`/chat/api/users/search/?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                },
                credentials: 'same-origin'
            });

            const data = await response.json();
            
            if (data.status === 'success' && data.users.length > 0) {
                const user = data.users[0]; // Prendre le premier résultat
                await this.startConversation(user.id);
            } else {
                alert('Utilisateur non trouvé');
            }
        } catch (error) {
            console.error('[MessengerChat] Error searching users:', error);
            alert('Erreur lors de la recherche');
        }
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
                await this.loadConversations(); // Recharger la liste
                await this.openConversation(data.conversation_id);
            } else {
                alert('Erreur: ' + data.message);
            }
        } catch (error) {
            console.error('[MessengerChat] Error starting conversation:', error);
            alert('Erreur lors de la création de la conversation');
        }
    }

    showConversationsList() {
        document.getElementById('conversations-list').style.display = 'block';
        document.getElementById('active-conversation').style.display = 'none';
        this.currentConversation = null;
        
        // WebSocket désactivé temporairement
        // if (this.websockets.chat) {
        //     this.websockets.chat.close();
        //     this.websockets.chat = null;
        // }
    }

    showConversationView() {
        document.getElementById('conversations-list').style.display = 'none';
        document.getElementById('active-conversation').style.display = 'block';
        
        // Forcer la focalisation de l'input après un court délai
        setTimeout(() => {
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.style.pointerEvents = 'auto';
                messageInput.disabled = false;
                console.log('[MessengerChat] Input enabled and ready');
            }
        }, 100);
    }

    updateUnreadBadge(conversations) {
        const totalUnread = conversations.reduce((total, conv) => total + conv.unread_count, 0);
        
        // Badge du widget messenger
        const messengerBadge = document.getElementById('total-unread');
        if (messengerBadge) {
            messengerBadge.textContent = totalUnread;
            messengerBadge.classList.toggle('visible', totalUnread > 0);
        }
        
        // Badge du bouton flottant
        const toggleBadge = document.getElementById('chat-toggle-badge');
        if (toggleBadge) {
            toggleBadge.textContent = totalUnread;
            toggleBadge.classList.toggle('visible', totalUnread > 0);
        }
    }

    show() {
        const chatElement = document.getElementById('messenger-chat');
        if (chatElement) {
            chatElement.style.display = 'block';
            this.isMinimized = false;
            // Recharger les conversations à chaque ouverture
            this.loadConversations();
        }
    }

    hide() {
        const chatElement = document.getElementById('messenger-chat');
        if (chatElement) {
            chatElement.style.display = 'none';
        }
    }

    toggleMinimize() {
        const body = document.getElementById('messenger-body');
        if (body) {
            if (this.isMinimized) {
                body.style.display = 'block';
                this.isMinimized = false;
                // Recharger les conversations quand on dé-minimise
                this.loadConversations();
            } else {
                body.style.display = 'none';
                this.isMinimized = true;
            }
        }
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
            const otherUser = conversation.participants.find(p => p.id != window.currentUserId);
            
            if (!otherUser) {
                alert('Impossible de trouver le destinataire');
                return;
            }

            console.log(`[MessengerChat] Initiating ${callType} call to user ${otherUser.id}`);

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
                console.log('[MessengerChat] Call initiated:', callData);
                this.startCall(callData, callType, otherUser);
            } else {
                alert('Erreur lors de l\'initiation de l\'appel: ' + callData.error);
            }
        } catch (error) {
            console.error('[MessengerChat] Error initiating call:', error);
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
                            ${otherUser.avatar_url ? 
                                `<img src="${otherUser.avatar_url}" alt="${otherUser.username}">` : 
                                `<div class="avatar-placeholder">${otherUser.username.charAt(0).toUpperCase()}</div>`
                            }
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

            console.log('[MessengerChat] WebRTC initialized successfully');
        } catch (error) {
            console.error('[MessengerChat] Error initializing WebRTC:', error);
            alert('Erreur d\'accès aux médias. Vérifiez vos permissions.');
        }
    }

    connectCallWebSocket(roomId) {
        const wsUrl = `ws://${window.location.host}/ws/call/${roomId}/`;
        this.callWebSocket = new WebSocket(wsUrl);

        this.callWebSocket.onopen = () => {
            console.log('[MessengerChat] Call WebSocket connected');
            this.updateCallStatus('Connecté');
        };

        this.callWebSocket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            await this.handleCallMessage(data);
        };

        this.callWebSocket.onclose = () => {
            console.log('[MessengerChat] Call WebSocket disconnected');
            this.updateCallStatus('Déconnecté');
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
        console.log('[MessengerChat] User joined call:', data.username);
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
            console.error('[MessengerChat] Error ending call:', error);
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

        console.log('[MessengerChat] Call ended successfully');
    }

    updateCallStatus(status) {
        const statusElement = document.getElementById('call-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    // ===== FIN FONCTIONNALITÉS D'APPEL =====

    // Fonctions utilitaires
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Moins d'une minute
            return 'Maintenant';
        } else if (diff < 3600000) { // Moins d'une heure
            return Math.floor(diff / 60000) + 'm';
        } else if (diff < 86400000) { // Moins d'un jour
            return Math.floor(diff / 3600000) + 'h';
        } else {
            return date.toLocaleDateString();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    searchConversations(query) {
        const items = document.querySelectorAll('.conversation-item');
        items.forEach(item => {
            const name = item.querySelector('.conversation-name').textContent.toLowerCase();
            const visible = name.includes(query.toLowerCase());
            item.style.display = visible ? 'flex' : 'none';
        });
    }
}

// Initialiser le chat quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    console.log('[MessengerChat] DOM ready, currentUserId:', window.currentUserId);
    
    if (window.currentUserId && !window.messengerChat) {
        console.log('[MessengerChat] Création de l\'objet MessengerChat');
        window.messengerChat = new MessengerChat();
        console.log('[MessengerChat] Objet créé:', window.messengerChat);
    } else if (!window.currentUserId) {
        console.error('[MessengerChat] currentUserId manquant');
    } else if (window.messengerChat) {
        console.log('[MessengerChat] Objet déjà existant');
    }
});