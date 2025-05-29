import React, { useState, useEffect } from 'react';
import {
  Modal,
  Box,
  Typography,
  IconButton,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextareaAutosize,
  Chip,
  Card,
  CardContent,
  CardActions,
  Grid,
  Tooltip,
  Alert,
  Divider,
  FormHelperText,
  CircularProgress,
} from '@mui/material';
import { Icon } from '../common/Icon';
import { personalProfileService, PersonalProfile, PersonalProfileCreate, PersonalProfileUpdate } from '../../services/personalProfileService';

interface PersonalProfilesModalProps {
  open: boolean;
  onClose: () => void;
}

const PersonalProfilesModal: React.FC<PersonalProfilesModalProps> = ({ open, onClose }) => {
  // Common styles for form fields
  const fieldStyles = {
    '& .MuiInputLabel-root': { color: '#FCC000' },
    '& .MuiOutlinedInput-root': {
      color: '#fff',
      '& fieldset': { borderColor: '#1a2b47' },
      '&:hover fieldset': { borderColor: '#FCC000' },
      '&.Mui-focused fieldset': { borderColor: '#FCC000' }
    },
    '& .MuiSelect-icon': { color: '#FCC000' }
  };

  const [profiles, setProfiles] = useState<PersonalProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingProfile, setEditingProfile] = useState<PersonalProfile | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const [formData, setFormData] = useState<Partial<PersonalProfileCreate>>({
    name: '',
    preferred_name: '',
    relationship: 'colleague',
    organization: '',
    role: '',
    birthday: '',
    first_met: '',
    preferred_contact: '',
    timezone: '',
    current_focus: '',
    notes: '',
    visibility: 'private'
  });

  useEffect(() => {
    if (open) {
      loadProfiles();
    }
  }, [open]);

  const loadProfiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await personalProfileService.getProfiles(true);
      setProfiles(data);
    } catch (err) {
      setError('Failed to load profiles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.name || !formData.relationship) {
      setError('Name and relationship are required');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await personalProfileService.createProfile(formData as PersonalProfileCreate);
      await loadProfiles();
      setCreatingNew(false);
      resetForm();
    } catch (err) {
      setError('Failed to create profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!editingProfile) return;

    setLoading(true);
    setError(null);
    try {
      const update: PersonalProfileUpdate = {
        ...formData
      };
      await personalProfileService.updateProfile(editingProfile.id, update);
      await loadProfiles();
      setEditingProfile(null);
      resetForm();
    } catch (err) {
      setError('Failed to update profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (profileId: string) => {
    if (!confirm('Are you sure you want to delete this profile?')) return;

    setLoading(true);
    setError(null);
    try {
      await personalProfileService.deleteProfile(profileId);
      await loadProfiles();
    } catch (err) {
      setError('Failed to delete profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      preferred_name: '',
      relationship: 'colleague',
      organization: '',
      role: '',
      birthday: '',
      first_met: '',
      preferred_contact: '',
      timezone: '',
      current_focus: '',
      notes: '',
      visibility: 'private'
    });
  };

  const startEdit = (profile: PersonalProfile) => {
    setEditingProfile(profile);
    setFormData({
      name: profile.name,
      preferred_name: profile.preferred_name || '',
      relationship: profile.relationship,
      organization: profile.organization || '',
      role: profile.role || '',
      birthday: profile.birthday || '',
      first_met: profile.first_met || '',
      preferred_contact: profile.preferred_contact || '',
      timezone: profile.timezone || '',
      current_focus: profile.current_focus || '',
      notes: profile.notes || '',
      visibility: profile.visibility
    });
    setCreatingNew(false);
  };

  const cancelEdit = () => {
    setEditingProfile(null);
    setCreatingNew(false);
    resetForm();
  };

  const renderForm = () => (
    <Box sx={{ mt: 2, p: 2, backgroundColor: '#121922', borderRadius: 2, border: '1px solid #1a2b47' }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Name *"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Preferred Name"
            value={formData.preferred_name}
            onChange={(e) => setFormData({ ...formData, preferred_name: e.target.value })}
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Relationship *</InputLabel>
            <Select
              value={formData.relationship}
              label="Relationship *"
              onChange={(e) => setFormData({ ...formData, relationship: e.target.value as any })}
            >
              <MenuItem value="colleague">Colleague</MenuItem>
              <MenuItem value="family">Family</MenuItem>
              <MenuItem value="friend">Friend</MenuItem>
              <MenuItem value="client">Client</MenuItem>
              <MenuItem value="acquaintance">Acquaintance</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Visibility</InputLabel>
            <Select
              value={formData.visibility}
              label="Visibility"
              onChange={(e) => setFormData({ ...formData, visibility: e.target.value as any })}
            >
              <MenuItem value="private">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Icon name="lock" size={16} />
                  <span>Private</span>
                </Box>
              </MenuItem>
              <MenuItem value="shared">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Icon name="users" size={16} />
                  <span>Shared</span>
                </Box>
              </MenuItem>
              <MenuItem value="global">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Icon name="global" size={16} />
                  <span>Global</span>
                </Box>
              </MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Organization"
            value={formData.organization}
            onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Role/Title"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Birthday"
            type="date"
            value={formData.birthday}
            onChange={(e) => setFormData({ ...formData, birthday: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="First Met"
            type="date"
            value={formData.first_met}
            onChange={(e) => setFormData({ ...formData, first_met: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Preferred Contact</InputLabel>
            <Select
              value={formData.preferred_contact || ''}
              label="Preferred Contact"
              onChange={(e) => setFormData({ ...formData, preferred_contact: e.target.value })}
            >
              <MenuItem value="">None</MenuItem>
              <MenuItem value="email">Email</MenuItem>
              <MenuItem value="phone">Phone</MenuItem>
              <MenuItem value="teams">Teams</MenuItem>
              <MenuItem value="slack">Slack</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Timezone"
            value={formData.timezone}
            onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
            placeholder="e.g., GMT+1, EST"
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Current Focus"
            value={formData.current_focus}
            onChange={(e) => setFormData({ ...formData, current_focus: e.target.value })}
            placeholder="What are they currently working on?"
            sx={{ mb: 2, ...fieldStyles }}
          />
        </Grid>
        
        <Grid item xs={12}>
          <Typography variant="body2" sx={{ mb: 1 }}>Additional Notes (Markdown supported)</Typography>
          <TextareaAutosize
            minRows={4}
            style={{
              width: '100%',
              backgroundColor: '#0d1929',
              color: '#fff',
              border: '1px solid #152238',
              borderRadius: 4,
              padding: 8,
              fontSize: '14px',
              fontFamily: 'monospace',
              resize: 'vertical'
            }}
            placeholder="Any additional information about this person..."
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          />
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          onClick={cancelEdit}
          sx={{ 
            color: '#fff',
            borderColor: '#FCC000',
            '&:hover': {
              borderColor: '#FCC000',
              backgroundColor: 'rgba(212, 175, 55, 0.1)'
            }
          }}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={editingProfile ? handleUpdate : handleCreate}
          disabled={loading || !formData.name || !formData.relationship}
          sx={{
            backgroundColor: '#FCC000',
            color: '#000',
            '&:hover': {
              backgroundColor: '#b8941c'
            },
            '&:disabled': {
              backgroundColor: 'rgba(212, 175, 55, 0.3)',
              color: 'rgba(0, 0, 0, 0.5)'
            }
          }}
        >
          {editingProfile ? 'Update' : 'Create'}
        </Button>
      </Box>
    </Box>
  );

  const renderProfile = (profile: PersonalProfile) => {
    const visibilityDisplay = personalProfileService.getVisibilityDisplay(profile.visibility);
    
    return (
      <Card key={profile.id} sx={{ mb: 2, backgroundColor: '#121922', border: '1px solid #1a2b47' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ mb: 1, color: '#fff' }}>
                {profile.name}
                {profile.preferred_name && profile.preferred_name !== profile.name && (
                  <Typography component="span" variant="body2" sx={{ ml: 1, color: '#888' }}>
                    ({profile.preferred_name})
                  </Typography>
                )}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                <Chip 
                  label={profile.relationship} 
                  size="small" 
                  sx={{ 
                    backgroundColor: '#1a2b47',
                    border: '2px solid #FFC300',
                    color: '#FFC300'
                  }}
                />
                <Chip 
                  label={visibilityDisplay.label} 
                  icon={<Icon name={visibilityDisplay.iconName} size={14} />}
                  size="small" 
                  sx={{ backgroundColor: visibilityDisplay.color + '22', color: visibilityDisplay.color }}
                />
                {profile.organization && (
                  <Chip 
                    label={profile.organization} 
                    size="small" 
                    sx={{ 
                      backgroundColor: '#1a2b47',
                      border: '2px solid #FFC300',
                      color: '#FFC300'
                    }}
                  />
                )}
                {profile.role && (
                  <Chip 
                    label={profile.role} 
                    size="small" 
                    sx={{ 
                      backgroundColor: '#1a2b47',
                      border: '2px solid #FFC300',
                      color: '#FFC300'
                    }}
                  />
                )}
              </Box>
              
              {profile.current_focus && (
                <Typography variant="body2" sx={{ mb: 1, color: '#FCC000' }}>
                  Currently: {profile.current_focus}
                </Typography>
              )}
              
              {profile.notes && (
                <Typography variant="body2" sx={{ color: '#aaa', whiteSpace: 'pre-wrap' }}>
                  {profile.notes.length > 200 ? profile.notes.substring(0, 200) + '...' : profile.notes}
                </Typography>
              )}
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                size="small"
                onClick={() => startEdit(profile)}
                sx={{ color: '#FCC000' }}
              >
                <Icon name="userEdit" size={18} />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => handleDelete(profile.id)}
                sx={{ color: '#ff4444' }}
              >
                <Icon name="trash" size={18} />
              </IconButton>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="personal-profiles-modal"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '90%',
        maxWidth: 800,
        maxHeight: '90vh',
        bgcolor: '#080d13',
        border: '2px solid #1a2b47',
        borderRadius: 2,
        boxShadow: 24,
        display: 'flex',
        flexDirection: 'column',
      }}>
        <Box sx={{ 
          p: 3, 
          borderBottom: '1px solid #1a2b47',
          backgroundColor: '#121922'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h5" sx={{ color: '#FCC000', fontWeight: 'bold' }}>
                Contacts
              </Typography>
              {!creatingNew && !editingProfile && (
                <IconButton
                  size="small"
                  onClick={() => setCreatingNew(true)}
                  sx={{ color: '#FCC000', '&:hover': { backgroundColor: 'rgba(252, 192, 0, 0.1)' } }}
                  title="Add New Contact"
                >
                  <Icon name="add" size={20} />
                </IconButton>
              )}
            </Box>
            <IconButton
              aria-label="close"
              onClick={onClose}
              sx={{ color: '#FCC000' }}
            >
              <Icon name="close" size={24} />
            </IconButton>
          </Box>
          <Typography variant="body2" sx={{ color: '#3E5B8F', fontSize: '13px' }}>
            This is your network of colleagues and contacts the assistant will reference when working within projects. 
            You choose how they interact within your projects, team and global users of the tool.
          </Typography>
        </Box>
        
        <Box sx={{ p: 3, overflowY: 'auto', flex: 1, backgroundColor: '#080d13' }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          
          {(creatingNew || editingProfile) && renderForm()}
          
          {!creatingNew && !editingProfile && (
            <>
              <Divider sx={{ mb: 0.25, mt: 1 }} />
              <Typography variant="h6" sx={{ mt: 0.25, mb: 0.5, color: '#FCC000' }}>Your Contacts</Typography>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : profiles.length === 0 ? (
                <Typography variant="body2" sx={{ textAlign: 'center', color: '#666', p: 4 }}>
                  No contacts yet. Add people you interact with to have the AI remember context about them.
                </Typography>
              ) : (
                profiles.map(renderProfile)
              )}
            </>
          )}
        </Box>
      </Box>
    </Modal>
  );
};

export default PersonalProfilesModal;