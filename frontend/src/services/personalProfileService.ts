import api from './api';

export interface PersonalProfile {
  id: string;
  name: string;
  role?: string;
  custom_fields: Array<{ key: string; value: string }>;
  is_default: boolean;
  is_private: boolean;
  shared_with_team: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreatePersonalProfileRequest {
  user_id: string;
  name: string;
  role?: string;
  custom_fields?: Array<{ key: string; value: string }>;
  is_default?: boolean;
  is_private?: boolean;
  shared_with_team?: boolean;
}

export interface UpdatePersonalProfileRequest {
  name?: string;
  role?: string;
  custom_fields?: Array<{ key: string; value: string }>;
  is_default?: boolean;
  is_private?: boolean;
  shared_with_team?: boolean;
}

class PersonalProfileService {
  private getUserId(): string {
    // In production, this would come from authentication
    // For now, use a default user ID stored in localStorage
    const userId = localStorage.getItem('userId');
    if (!userId) {
      const newUserId = `user_${Date.now()}`;
      localStorage.setItem('userId', newUserId);
      return newUserId;
    }
    return userId;
  }

  async getProfiles(includeShared = false): Promise<PersonalProfile[]> {
    const userId = this.getUserId();
    const response = await api.get('/personal-profiles/', {
      params: { user_id: userId, include_shared: includeShared }
    });
    return response.data;
  }

  async getProfile(profileId: string): Promise<PersonalProfile> {
    const userId = this.getUserId();
    const response = await api.get(`/personal-profiles/${profileId}`, {
      params: { user_id: userId }
    });
    return response.data;
  }

  async createProfile(data: Omit<CreatePersonalProfileRequest, 'user_id'>): Promise<PersonalProfile> {
    const userId = this.getUserId();
    const response = await api.post('/personal-profiles/', {
      ...data,
      user_id: userId
    });
    return response.data;
  }

  async updateProfile(profileId: string, data: UpdatePersonalProfileRequest): Promise<PersonalProfile> {
    const userId = this.getUserId();
    const response = await api.put(`/personal-profiles/${profileId}`, data, {
      params: { user_id: userId }
    });
    return response.data;
  }

  async deleteProfile(profileId: string): Promise<void> {
    const userId = this.getUserId();
    await api.delete(`/personal-profiles/${profileId}`, {
      params: { user_id: userId }
    });
  }

  async getDefaultProfile(): Promise<PersonalProfile | null> {
    try {
      const userId = this.getUserId();
      const response = await api.get(`/personal-profiles/default/${userId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  // Format profile for inclusion in prompts
  formatProfileForPrompt(profile: PersonalProfile): string {
    let prompt = `Personal Information:\n`;
    prompt += `Name: ${profile.name}\n`;
    
    if (profile.role) {
      prompt += `Role: ${profile.role}\n`;
    }
    
    if (profile.custom_fields && profile.custom_fields.length > 0) {
      profile.custom_fields.forEach(field => {
        prompt += `${field.key}: ${field.value}\n`;
      });
    }
    
    return prompt;
  }

  // Migrate existing localStorage profiles to database
  async migrateFromLocalStorage(): Promise<void> {
    const localProfiles = localStorage.getItem('personalProfiles');
    if (!localProfiles) return;

    try {
      const profiles = JSON.parse(localProfiles);
      
      for (const profile of profiles) {
        await this.createProfile({
          name: profile.name,
          role: profile.role,
          custom_fields: profile.customFields || [],
          is_default: profile.isDefault || false
        });
      }
      
      // Remove from localStorage after successful migration
      localStorage.removeItem('personalProfiles');
      console.log('Successfully migrated profiles to database');
    } catch (error) {
      console.error('Failed to migrate profiles:', error);
    }
  }
}

export default new PersonalProfileService();