/**
 * Service for managing personal profiles in local storage
 */

export interface PersonProfile {
  id: string;
  name: string;
  role?: string;
  address?: string;
  customFields: Array<{ key: string; value: string }>;
  isDefault?: boolean;
}

class ProfileService {
  private readonly STORAGE_KEY = 'personalProfiles';

  /**
   * Get all profiles from local storage
   */
  getProfiles(): PersonProfile[] {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Get the default profile
   */
  getDefaultProfile(): PersonProfile | null {
    const profiles = this.getProfiles();
    return profiles.find(p => p.isDefault) || null;
  }

  /**
   * Format default profile as prompt text
   */
  getDefaultProfilePrompt(): string {
    const profile = this.getDefaultProfile();
    if (!profile) return '';

    const parts = ['Personal context about the user you\'re assisting:'];
    
    if (profile.name) {
      parts.push(`- Name: ${profile.name}`);
    }
    
    if (profile.role) {
      parts.push(`- Role: ${profile.role}`);
    }
    
    if (profile.address) {
      parts.push(`- Location: ${profile.address}`);
    }
    
    // Add custom fields
    profile.customFields.forEach(field => {
      if (field.key && field.value) {
        parts.push(`- ${field.key}: ${field.value}`);
      }
    });
    
    return parts.length > 1 ? '\n\n' + parts.join('\n') : '';
  }

  /**
   * Save profiles to local storage
   */
  saveProfiles(profiles: PersonProfile[]): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(profiles));
  }
}

export const profileService = new ProfileService();