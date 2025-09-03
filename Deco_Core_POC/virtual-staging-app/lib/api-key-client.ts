/**
 * Client for communicating with the API Key Manager
 * This allows the Next.js app to validate API keys against the standalone API Key Manager
 */

export interface APIKeyValidationResponse {
  valid: boolean;
  message: string;
  key_info?: {
    id: number;
    key_prefix: string;
    name: string;
    status: string;
    user_email: string;
    organization?: string;
    rate_limit: number;
    daily_quota: number;
    current_daily_usage: number;
  };
  remaining_quota?: number;
  rate_limit_remaining?: number;
}

export class APIKeyManagerClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8004') {
    this.baseUrl = baseUrl;
  }

  /**
   * Validate an API key against the API Key Manager
   */
  async validateAPIKey(apiKey: string): Promise<APIKeyValidationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/keys/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error validating API key:', error);
      return {
        valid: false,
        message: 'Unable to validate API key. API Key Manager may be unavailable.',
      };
    }
  }

  /**
   * Record API usage (optional - for future use)
   */
  async recordUsage(apiKey: string, serviceName: string = 'image-generation'): Promise<boolean> {
    try {
      // This would be implemented when we add usage tracking to the API Key Manager
      // For now, we'll just return true
      return true;
    } catch (error) {
      console.error('Error recording usage:', error);
      return false;
    }
  }
}

// API Key Manager configuration
const API_KEY_MANAGER_URL = 'http://localhost:8004';

// Singleton instance
export const apiKeyManager = new APIKeyManagerClient(API_KEY_MANAGER_URL);
