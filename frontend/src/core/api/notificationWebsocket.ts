// src/core/api/notificationWebsocket.ts
import { NotificationDto } from '@/core/types/notification.types';

/**
 * WebSocket service for real-time notifications
 */
class NotificationWebsocketService {
  private static instance: NotificationWebsocketService;
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private listeners: Array<(notification: NotificationDto) => void> = [];
  private connectionListeners: Array<(connected: boolean) => void> = [];
  
  /**
   * Get the singleton instance
   */
  public static getInstance(): NotificationWebsocketService {
    if (!NotificationWebsocketService.instance) {
      NotificationWebsocketService.instance = new NotificationWebsocketService();
    }
    return NotificationWebsocketService.instance;
  }
  
  /**
   * Initialize and connect WebSocket
   * @param authToken Authentication token
   */
  public connect(authToken: string): void {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      console.warn('Attempted to connect WebSocket during server-side rendering');
      return;
    }
    
    // Validate auth token
    if (!authToken || typeof authToken !== 'string') {
      console.error('Invalid authentication token for WebSocket connection');
      this.notifyConnectionListeners(false);
      return;
    }
    
    // If already connected, close the previous connection
    if (this.socket) {
      this.close();
    }
    
    try {
      // Create WebSocket URL based on current environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      
      // Use environment variable if available, otherwise use current host
      const apiHost = process.env.NEXT_PUBLIC_API_HOST;
      const host = apiHost || window.location.host;
      
      // Build WebSocket URL with token
      const wsUrl = `${protocol}//${host}/ws/notifications/?token=${encodeURIComponent(authToken)}`;
      
      // Create WebSocket connection
      this.socket = new WebSocket(wsUrl);
      
      // Set up event handlers with proper error handling
      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
      
      console.log('Notification WebSocket connecting...');
    } catch (error) {
      console.error('Error connecting to notification WebSocket:', error);
      this.notifyConnectionListeners(false);
      
      // Schedule a reconnect attempt
      this.scheduleReconnect(authToken);
    }
  }
  
  /**
   * Close the WebSocket connection
   */
  public close(): void {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      if (this.socket) {
        // Check if the socket is open or connecting before closing
        if (this.socket.readyState === WebSocket.OPEN || 
            this.socket.readyState === WebSocket.CONNECTING) {
          // Remove event handlers to prevent reconnect on expected close
          this.socket.onclose = null;
          this.socket.onerror = null;
          
          // Send close message if connection is open
          if (this.socket.readyState === WebSocket.OPEN) {
            try {
              // Optional: send a close message to the server
              this.socket.send(JSON.stringify({ type: 'client_close' }));
            } catch (sendError) {
              // Ignore errors when trying to send close message
              console.debug('Error sending close message:', sendError);
            }
          }
          
          // Close the connection
          this.socket.close(1000, 'Client closed connection');
        }
        
        // Reset socket reference
        this.socket = null;
      }
      
      // Clear any pending reconnect
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
      
      // Reset reconnect attempts
      this.reconnectAttempts = 0;
      
      console.log('Notification WebSocket closed');
      this.notifyConnectionListeners(false);
    } catch (error) {
      console.error('Error closing notification WebSocket:', error);
      
      // Make sure listeners are notified even if there's an error
      this.notifyConnectionListeners(false);
      
      // Reset state in case of error
      this.socket = null;
      this.reconnectAttempts = 0;
      
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
    }
  }
  
  /**
   * Add a notification listener
   * @param listener Function to call when a notification is received
   */
  public addListener(listener: (notification: NotificationDto) => void): void {
    this.listeners.push(listener);
  }
  
  /**
   * Remove a notification listener
   * @param listener Function to remove
   */
  public removeListener(listener: (notification: NotificationDto) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }
  
  /**
   * Add a connection state listener
   * @param listener Function to call when connection state changes
   */
  public addConnectionListener(listener: (connected: boolean) => void): void {
    this.connectionListeners.push(listener);
    
    // Immediately notify with current state
    if (this.socket) {
      listener(this.socket.readyState === WebSocket.OPEN);
    } else {
      listener(false);
    }
  }
  
  /**
   * Remove a connection state listener
   * @param listener Function to remove
   */
  public removeConnectionListener(listener: (connected: boolean) => void): void {
    this.connectionListeners = this.connectionListeners.filter(l => l !== listener);
  }
  
  /**
   * Check if the WebSocket is connected
   */
  public isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
  
  /**
   * Handle WebSocket connection opened
   */
  private handleOpen(_event: Event): void {
    console.log('Notification WebSocket connected');
    
    // Reset reconnect attempts on successful connection
    this.reconnectAttempts = 0;
    
    // Notify connection listeners
    this.notifyConnectionListeners(true);
  }
  
  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(event: MessageEvent): void {
    try {
      // Skip if no listeners are registered
      if (this.listeners.length === 0) {
        return;
      }
      
      // Parse message data as JSON
      const data = JSON.parse(event.data);
      
      // Handle different message types
      switch (data.type) {
        case 'notification':
          // Handle notification message
          if (data.notification) {
            const notification: NotificationDto = data.notification;
            
            // Notify all listeners
            this.notifyNotificationListeners(notification);
          }
          break;
          
        case 'unread_count':
          // Handle unread count update
          console.log('Unread notifications count:', data.count);
          break;
          
        case 'ping':
          // Handle heartbeat ping
          this.sendPong();
          break;
          
        default:
          console.log('Received unknown WebSocket message type:', data.type);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  }
  
  /**
   * Notify all notification listeners about a new notification
   */
  private notifyNotificationListeners(notification: NotificationDto): void {
    if (!notification) return;
    
    this.listeners.forEach(listener => {
      try {
        listener(notification);
      } catch (error) {
        console.error('Error in notification listener:', error);
      }
    });
  }
  
  /**
   * Send a pong response to the server
   */
  private sendPong(): void {
    if (this.isConnected()) {
      try {
        this.socket?.send(JSON.stringify({ type: 'pong' }));
      } catch (error) {
        console.error('Error sending pong message:', error);
      }
    }
  }
  
  /**
   * Handle WebSocket connection closed
   */
  private handleClose(event: CloseEvent): void {
    // Log close event with details
    const wasClean = event.wasClean ? 'cleanly' : 'unexpectedly';
    console.log(`Notification WebSocket closed ${wasClean}: code=${event.code}, reason=${event.reason || 'No reason provided'}`);
    
    // Check if this was an expected closure
    const isExpectedClosure = event.wasClean && (
      (// Normal closure
      event.code === 1000 || event.code === 1001)    // Going away (page unload)
    );
    
    // Only attempt to reconnect for unexpected closures
    if (!isExpectedClosure) {
      // Reset the socket reference
      this.socket = null;
      
      // Attempt to reconnect
      this.attemptReconnect();
    } else {
      // For expected closures, just reset the state
      this.socket = null;
      this.reconnectAttempts = 0;
    }
    
    // Notify connection listeners
    this.notifyConnectionListeners(false);
  }
  
  /**
   * Handle WebSocket error
   */
  private handleError(event: Event): void {
    console.error('Notification WebSocket error:', event);
    
    // For errors, we'll try to reconnect immediately
    // First reset the socket to avoid multiple reconnect attempts
    if (this.socket) {
      // Save the URL for reconnection
      const url = this.socket.url;
      
      try {
        // Try to close the socket cleanly
        this.socket.close();
      } catch (error) {
        console.debug('Error closing socket after error:', error);
      }
      
      this.socket = null;
      
      // Try to extract token and reconnect
      try {
        const parsedUrl = new URL(url);
        const token = parsedUrl.searchParams.get('token');
        
        if (token) {
          // Schedule reconnect with minimal delay
          setTimeout(() => {
            this.connect(token);
          }, 1000);
        }
      } catch (urlError) {
        console.error('Error parsing WebSocket URL for reconnection:', urlError);
      }
    }
    
    // Notify connection listeners
    this.notifyConnectionListeners(false);
  }
  
  /**
   * Schedule a reconnection with the provided token
   */
  private scheduleReconnect(authToken: string): void {
    // Clear any existing reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    // Don't reconnect if we've reached the maximum attempts
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Maximum reconnect attempts reached for notification WebSocket');
      return;
    }
    
    // Calculate backoff delay: 1s, 2s, 4s, 8s, 16s
    const delay = Math.pow(2, this.reconnectAttempts) * 1000;
    this.reconnectAttempts++;
    
    console.log(`Reconnecting notification WebSocket in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    // Set timeout for reconnect
    this.reconnectTimeout = setTimeout(() => {
      this.connect(authToken);
    }, delay);
  }
  
  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      // Get token from the current socket URL if available
      let token: string | null = null;
      
      if (this.socket?.url) {
        const url = new URL(this.socket.url);
        token = url.searchParams.get('token');
      }
      
      if (token) {
        this.scheduleReconnect(token);
      } else {
        console.error('Cannot reconnect: no authentication token available');
      }
    } catch (error) {
      console.error('Error attempting to reconnect WebSocket:', error);
    }
  }
  
  /**
   * Notify all connection listeners of connection state change
   */
  private notifyConnectionListeners(connected: boolean): void {
    this.connectionListeners.forEach(listener => {
      try {
        listener(connected);
      } catch (error) {
        console.error('Error in connection listener:', error);
      }
    });
  }
}

export default NotificationWebsocketService.getInstance();