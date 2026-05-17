const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

interface ApiResponse<T = any> {
  data: T;
  error?: string;
  status: number;
}

interface AuthTokens {
  access: string;
  refresh: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, ''); // remove trailing slash
    this.loadTokens();
  }

  // Load tokens from localStorage
  private loadTokens(): void {
    try {
      const stored = localStorage.getItem(TOKEN_KEY);
      if (stored) this.token = stored;
      const storedRefresh = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (storedRefresh) this.refreshToken = storedRefresh;
    } catch {
      // localStorage not available or corrupted
      this.token = null;
      this.refreshToken = null;
    }
  }

  // Save tokens to localStorage
  private saveTokens(tokens: AuthTokens): void {
    try {
      localStorage.setItem(TOKEN_KEY, tokens.access);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
      this.token = tokens.access;
      this.refreshToken = tokens.refresh;
    } catch {
      console.warn('Failed to save auth tokens to localStorage');
    }
  }

  // Clear tokens (logout)
  clearTokens(): void {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    } catch {
      // ignore
    }
    this.token = null;
    this.refreshToken = null;
  }

  // Set tokens (login)
  setTokens(tokens: AuthTokens): void {
    this.saveTokens(tokens);
  }

  // Get current token
  getToken(): string | null {
    return this.token;
  }

  // Refresh the access token using the refresh token
  private async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false;
    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken })
      });
      if (!response.ok) {
        this.clearTokens();
        return false;
      }
      const data: AuthTokens = await response.json();
      this.saveTokens(data);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
      return false;
    }
  }
}

// Export for use in other parts of the application
export { ApiClient, ApiResponse, AuthTokens, API_BASE_URL };