// Persistent cache implementation using IndexedDB
interface CacheEntry {
  key: string;
  data: any;
  timestamp: number;
  expiresAt: number;
}

class PersistentCache {
  private dbName = 'linguify-cache';
  private storeName = 'api-cache';
  private version = 1;
  private db: IDBDatabase | null = null;
  private isSupported = typeof window !== 'undefined' && 'indexedDB' in window;

  async init(): Promise<void> {
    if (!this.isSupported || this.db) return;

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, { keyPath: 'key' });
          store.createIndex('expiresAt', 'expiresAt', { unique: false });
        }
      };
    });
  }

  async get(key: string): Promise<any | null> {
    if (!this.isSupported) return null;
    
    await this.init();
    if (!this.db) return null;

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.get(key);

      request.onsuccess = () => {
        const entry: CacheEntry = request.result;
        if (!entry) {
          resolve(null);
          return;
        }

        // Check if expired
        if (Date.now() > entry.expiresAt) {
          this.delete(key); // Clean up expired entry
          resolve(null);
          return;
        }

        resolve(entry.data);
      };

      request.onerror = () => resolve(null);
    });
  }

  async set(key: string, data: any, ttlMs: number): Promise<void> {
    if (!this.isSupported) return;
    
    await this.init();
    if (!this.db) return;

    const entry: CacheEntry = {
      key,
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + ttlMs
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.put(entry);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async delete(key: string): Promise<void> {
    if (!this.isSupported || !this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async clear(): Promise<void> {
    if (!this.isSupported || !this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async cleanup(): Promise<void> {
    if (!this.isSupported || !this.db) return;

    // Delete expired entries
    return new Promise((resolve) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const index = store.index('expiresAt');
      const range = IDBKeyRange.upperBound(Date.now());
      const request = index.openCursor(range);

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          store.delete(cursor.primaryKey);
          cursor.continue();
        } else {
          resolve();
        }
      };

      request.onerror = () => resolve();
    });
  }
}

// Create singleton instance
export const persistentCache = new PersistentCache();

// Auto-cleanup expired entries periodically (every 5 minutes)
if (typeof window !== 'undefined') {
  setInterval(() => {
    persistentCache.cleanup().catch(console.error);
  }, 5 * 60 * 1000);
}

export default persistentCache;