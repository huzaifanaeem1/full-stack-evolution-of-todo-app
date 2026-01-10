// Auth utility for token management
const TOKEN_KEY = 'jwt_token';
const USER_ID_KEY = 'user_id';

/**
 * Store JWT token and user ID in localStorage
 */
export const setAuthToken = (token: string, userId: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_ID_KEY, userId);
  }
};

/**
 * Get JWT token from localStorage
 */
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
};

/**
 * Get user ID from localStorage
 */
export const getUserId = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(USER_ID_KEY);
  }
  return null;
};

/**
 * Remove authentication tokens from localStorage
 */
export const removeAuthToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_ID_KEY);
  }
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  return !!token && !isTokenExpired(token);
};

/**
 * Check if token is expired
 */
export const isTokenExpired = (token: string): boolean => {
  try {
    if (!token) return true;

    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));

    // Check if token is expired (compare with current time)
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true;
  }
};

/**
 * Get token expiration time
 */
export const getTokenExpirationTime = (token: string): number | null => {
  try {
    if (!token) return null;

    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));

    return payload.exp;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

/**
 * Check if token will expire soon (within 5 minutes)
 */
export const isTokenExpiringSoon = (token: string): boolean => {
  try {
    if (!token) return true;

    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));

    // Check if token expires within 5 minutes (300 seconds)
    const fiveMinutesFromNow = Math.floor(Date.now() / 1000) + 300;
    return payload.exp < fiveMinutesFromNow;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true;
  }
};

/**
 * Refresh token by calling backend endpoint
 */
export const refreshToken = async (): Promise<string | null> => {
  try {
    const token = getAuthToken();
    if (!token || isTokenExpired(token)) {
      // Token is expired, user needs to log in again
      removeAuthToken();
      return null;
    }

    // In a real implementation, you would call a refresh endpoint
    // For now, we'll just return the existing token if it's still valid
    // But in a production app, you'd make a request to a refresh endpoint
    if (!isTokenExpiringSoon(token)) {
      return token; // Token is still valid and not expiring soon
    }

    // In a real app, you would make a request to refresh the token
    // This is a simplified implementation
    console.warn('Token is expiring soon. In a real app, implement refresh token logic.');
    return token;
  } catch (error) {
    console.error('Error refreshing token:', error);
    removeAuthToken(); // Clear invalid token
    return null;
  }
};