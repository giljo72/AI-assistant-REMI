import api from './api';

export interface PersonalProfile {
  id: string;
  name: string;
  preferred_name?: string;
  relationship: 'colleague' | 'family' | 'friend' | 'client' | 'acquaintance' | 'other';
  organization?: string;
  role?: string;
  birthday?: string;
  first_met?: string;
  preferred_contact?: string;
  timezone?: string;
  current_focus?: string;
  notes?: string;
  visibility: 'private' | 'shared' | 'global';
  user_id: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PersonalProfileCreate {
  name: string;
  preferred_name?: string;
  relationship: 'colleague' | 'family' | 'friend' | 'client' | 'acquaintance' | 'other';
  organization?: string;
  role?: string;
  birthday?: string;
  first_met?: string;
  preferred_contact?: string;
  timezone?: string;
  current_focus?: string;
  notes?: string;
  visibility: 'private' | 'shared' | 'global';
}

export interface PersonalProfileUpdate {
  name?: string;
  preferred_name?: string;
  relationship?: 'colleague' | 'family' | 'friend' | 'client' | 'acquaintance' | 'other';
  organization?: string;
  role?: string;
  birthday?: string;
  first_met?: string;
  preferred_contact?: string;
  timezone?: string;
  current_focus?: string;
  notes?: string;
  visibility?: 'private' | 'shared' | 'global';
  is_active?: boolean;
}

class PersonalProfileService {
  /**
   * Get all personal profiles for the current user
   */
  async getProfiles(includeGlobal: boolean = false): Promise<PersonalProfile[]> {
    const params = new URLSearchParams({
      user_id: 'default_user',
      include_global: includeGlobal.toString()
    });
    const response = await api.get(`/personal-profiles/?${params}`);
    return response.data;
  }

  /**
   * Search profiles by name, organization, role, or notes
   */
  async searchProfiles(
    query: string,
    includeShared: boolean = true,
    includeGlobal: boolean = true
  ): Promise<PersonalProfile[]> {
    const params = new URLSearchParams({
      query,
      user_id: 'default_user',
      include_shared: includeShared.toString(),
      include_global: includeGlobal.toString()
    });
    const response = await api.get(`/personal-profiles/search?${params}`);
    return response.data;
  }

  /**
   * Get profiles for chat context
   */
  async getProfilesForContext(
    projectId?: string,
    includeGlobal: boolean = true
  ): Promise<PersonalProfile[]> {
    const params = new URLSearchParams({
      user_id: 'default_user',
      include_global: includeGlobal.toString()
    });
    if (projectId) {
      params.append('project_id', projectId);
    }
    const response = await api.get(`/personal-profiles/context?${params}`);
    return response.data;
  }

  /**
   * Get a specific profile by ID
   */
  async getProfile(profileId: string): Promise<PersonalProfile> {
    const response = await api.get(`/personal-profiles/${profileId}?user_id=default_user`);
    return response.data;
  }

  /**
   * Create a new personal profile
   */
  async createProfile(profile: PersonalProfileCreate): Promise<PersonalProfile> {
    const response = await api.post('/personal-profiles/?user_id=default_user', profile);
    return response.data;
  }

  /**
   * Update an existing profile
   */
  async updateProfile(profileId: string, update: PersonalProfileUpdate): Promise<PersonalProfile> {
    const response = await api.put(`/personal-profiles/${profileId}?user_id=default_user`, update);
    return response.data;
  }

  /**
   * Delete a profile (soft delete)
   */
  async deleteProfile(profileId: string): Promise<void> {
    await api.delete(`/personal-profiles/${profileId}?user_id=default_user`);
  }

  /**
   * Get formatted profile for display
   */
  async getFormattedProfile(profileId: string): Promise<{ profile_id: string; name: string; formatted_context: string }> {
    const response = await api.get(`/personal-profiles/formatted/${profileId}?user_id=default_user`);
    return response.data;
  }

  /**
   * Format profile for display in UI
   */
  formatProfileForDisplay(profile: PersonalProfile): string {
    const parts = [`${profile.name}`];
    
    if (profile.preferred_name && profile.preferred_name !== profile.name) {
      parts.push(`(${profile.preferred_name})`);
    }
    
    if (profile.role && profile.organization) {
      parts.push(`- ${profile.role} at ${profile.organization}`);
    } else if (profile.role) {
      parts.push(`- ${profile.role}`);
    } else if (profile.organization) {
      parts.push(`- ${profile.organization}`);
    }
    
    parts.push(`- ${profile.relationship}`);
    
    return parts.join(' ');
  }

  /**
   * Get visibility icon and color
   */
  getVisibilityDisplay(visibility: 'private' | 'shared' | 'global'): { iconName: 'lock' | 'users' | 'global'; color: string; label: string } {
    switch (visibility) {
      case 'private':
        return { iconName: 'lock', color: '#ff4444', label: 'Private' };
      case 'shared':
        return { iconName: 'users', color: '#4a9eff', label: 'Shared' };
      case 'global':
        return { iconName: 'global', color: '#52c41a', label: 'Global' };
    }
  }

  /**
   * Format a list of profiles for the assistant prompt
   */
  formatProfilesForPrompt(profiles: PersonalProfile[]): string | undefined {
    if (!profiles || profiles.length === 0) {
      return undefined;
    }

    const formatted = profiles.map(profile => {
      let context = `Person: ${profile.name}`;
      
      if (profile.preferred_name && profile.preferred_name !== profile.name) {
        context += `\nPrefers to be called: ${profile.preferred_name}`;
      }
      
      context += `\nRelationship: ${profile.relationship}`;
      
      if (profile.organization) {
        context += `\nOrganization: ${profile.organization}`;
      }
      if (profile.role) {
        context += `\nRole: ${profile.role}`;
      }
      
      if (profile.birthday) {
        const date = new Date(profile.birthday);
        context += `\nBirthday: ${date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}`;
      }
      
      if (profile.current_focus) {
        context += `\nCurrently focused on: ${profile.current_focus}`;
      }
      
      if (profile.notes) {
        context += `\nAdditional context: ${profile.notes}`;
      }
      
      return context;
    }).join('\n\n---\n\n');

    return `IMPORTANT: The following are people the USER knows (contacts/relationships), NOT the user themselves:\n${'='.repeat(60)}\n${formatted}\n${'='.repeat(60)}\nREMEMBER: The user is NOT any of these people. These are their contacts.`;
  }

  /**
   * Get the default profile for the current user
   */
  async getDefaultProfile(): Promise<PersonalProfile | null> {
    try {
      const profiles = await this.getProfiles(false);
      return profiles.length > 0 ? profiles[0] : null;
    } catch (error) {
      console.error('Error fetching default profile:', error);
      return null;
    }
  }
}

export const personalProfileService = new PersonalProfileService();