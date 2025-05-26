import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Box,
  Typography,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Person as PersonIcon
} from '@mui/icons-material';
import personalProfileService, { PersonalProfile } from '../../services/personalProfileService';
import { Icon, HelpIcon } from '../common/Icon';

interface PersonalProfilesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PersonalProfilesModal: React.FC<PersonalProfilesModalProps> = ({ isOpen, onClose }) => {
  const [profiles, setProfiles] = useState<PersonalProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<PersonalProfile | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    custom_fields: [] as Array<{ key: string; value: string }>
  });

  // Load profiles when modal opens
  useEffect(() => {
    if (isOpen) {
      loadProfiles();
      // Check for migration on first open
      personalProfileService.migrateFromLocalStorage();
    }
  }, [isOpen]);

  const loadProfiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await personalProfileService.getProfiles();
      setProfiles(data);
      
      // Set the default profile as selected
      const defaultProfile = data.find(p => p.is_default);
      if (defaultProfile) {
        setSelectedProfile(defaultProfile);
        setFormData({
          name: defaultProfile.name,
          role: defaultProfile.role || '',
          custom_fields: defaultProfile.custom_fields || []
        });
      }
    } catch (err: any) {
      setError('Failed to load profiles');
      console.error('Error loading profiles:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddProfile = async () => {
    try {
      const newProfile = await personalProfileService.createProfile({
        name: 'New Profile',
        role: '',
        custom_fields: [],
        is_default: profiles.length === 0
      });
      
      setProfiles([...profiles, newProfile]);
      setSelectedProfile(newProfile);
      setFormData({
        name: '',
        role: '',
        custom_fields: []
      });
      setEditMode(true);
    } catch (err: any) {
      setError('Failed to create profile');
      console.error('Error creating profile:', err);
    }
  };

  const handleSaveProfile = async () => {
    if (!selectedProfile) return;
    
    try {
      const updatedProfile = await personalProfileService.updateProfile(
        selectedProfile.id,
        formData
      );
      
      setProfiles(profiles.map(p => 
        p.id === selectedProfile.id ? updatedProfile : p
      ));
      setSelectedProfile(updatedProfile);
      setEditMode(false);
    } catch (err: any) {
      setError('Failed to save profile');
      console.error('Error saving profile:', err);
    }
  };

  const handleDeleteProfile = async (profileId: string) => {
    try {
      await personalProfileService.deleteProfile(profileId);
      
      const updatedProfiles = profiles.filter(p => p.id !== profileId);
      setProfiles(updatedProfiles);
      
      if (selectedProfile?.id === profileId) {
        setSelectedProfile(updatedProfiles[0] || null);
        if (updatedProfiles[0]) {
          setFormData({
            name: updatedProfiles[0].name,
            role: updatedProfiles[0].role || '',
            custom_fields: updatedProfiles[0].custom_fields || []
          });
        }
      }
    } catch (err: any) {
      setError('Failed to delete profile');
      console.error('Error deleting profile:', err);
    }
  };

  const handleSetDefault = async (profileId: string) => {
    try {
      const updatedProfile = await personalProfileService.updateProfile(
        profileId,
        { is_default: true }
      );
      
      // Update all profiles to reflect new default
      const updatedProfiles = profiles.map(p => ({
        ...p,
        is_default: p.id === profileId
      }));
      
      setProfiles(updatedProfiles);
    } catch (err: any) {
      setError('Failed to set default profile');
      console.error('Error setting default:', err);
    }
  };

  const handleAddCustomField = () => {
    setFormData({
      ...formData,
      custom_fields: [...formData.custom_fields, { key: '', value: '' }]
    });
  };

  const handleCustomFieldChange = (index: number, field: 'key' | 'value', value: string) => {
    const updatedFields = [...formData.custom_fields];
    updatedFields[index][field] = value;
    setFormData({ ...formData, custom_fields: updatedFields });
  };

  const handleRemoveCustomField = (index: number) => {
    const updatedFields = formData.custom_fields.filter((_, i) => i !== index);
    setFormData({ ...formData, custom_fields: updatedFields });
  };

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: '#0a0f1b',
          color: '#ffffff',
          minHeight: '600px'
        }
      }}
    >
      <DialogTitle sx={{ 
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PersonIcon sx={{ color: '#d4af37' }} />
          <Typography variant="h6" sx={{ color: '#FFFFFF' }}>Personal Profiles</Typography>
        </Box>
        <Icon 
          name="close" 
          size={24} 
          onClick={onClose}
          tooltip="Close"
          style={{ color: '#FFC000' }}
        />
      </DialogTitle>
      
      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', minHeight: '500px' }}>
        {/* Instructions Banner */}
        <Box sx={{ 
          p: 2, 
          backgroundColor: '#0a0f1b',
          borderBottom: '1px solid #2d3748',
          textAlign: 'center'
        }}>
          <Typography variant="body2" sx={{ color: 'rgb(59, 130, 246)', lineHeight: 1.6 }}>
            Create profiles for yourself and people you work with. The AI Assistant will use this information
            to better understand context when you mention these people or discuss related topics.
            Your profiles help the AI provide more personalized and relevant assistance.
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ flex: 1, display: 'flex' }}>
          {/* Left Panel - Profile List */}
          <Box sx={{ 
            width: '250px', 
            borderRight: '1px solid #1e293b',
            backgroundColor: '#0f1823'
          }}>
          <Box sx={{ p: 2, borderBottom: '1px solid #1e293b' }}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Icon name="add" size={20} />}
              onClick={handleAddProfile}
              disabled={loading}
              sx={{
                backgroundColor: '#d4af37',
                color: '#000000',
                '&:hover': {
                  backgroundColor: '#b8941f',
                  color: '#000000'
                }
              }}
            >
              Add Profile
            </Button>
          </Box>
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress sx={{ color: '#d4af37' }} />
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {profiles.map(profile => (
                <ListItem
                  key={profile.id}
                  button
                  selected={selectedProfile?.id === profile.id}
                  onClick={() => {
                    setSelectedProfile(profile);
                    setFormData({
                      name: profile.name,
                      role: profile.role || '',
                      custom_fields: profile.custom_fields || []
                    });
                    setEditMode(false);
                  }}
                  sx={{
                    '&.Mui-selected': {
                      backgroundColor: '#1e293b',
                      borderLeft: '3px solid #d4af37'
                    }
                  }}
                >
                  <ListItemText 
                    primary={profile.name}
                    primaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                    secondary={profile.is_default && (
                      <Chip 
                        label="Default" 
                        size="small" 
                        sx={{ 
                          backgroundColor: '#d4af37',
                          color: '#000000',
                          height: '16px',
                          fontSize: '0.7rem'
                        }}
                      />
                    )}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Right Panel - Profile Details */}
        <Box sx={{ flex: 1, p: 3 }}>
          {selectedProfile ? (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ color: '#FFFFFF' }}>
                  {editMode ? 'Edit Profile' : 'Profile Details'}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!editMode ? (
                    <>
                      <Button
                        size="small"
                        startIcon={<Icon name="userEdit" size={16} />}
                        onClick={() => setEditMode(true)}
                        sx={{ color: '#FFC000' }}
                      >
                        Edit
                      </Button>
                      {!selectedProfile.is_default && (
                        <Button
                          size="small"
                          onClick={() => handleSetDefault(selectedProfile.id)}
                          sx={{ color: '#FFC000' }}
                        >
                          Set as Default
                        </Button>
                      )}
                      <Icon
                        name="userDelete"
                        size={20}
                        onClick={() => handleDeleteProfile(selectedProfile.id)}
                        tooltip="Delete Profile"
                        style={{ color: '#FFC000', marginLeft: '8px' }}
                      />
                    </>
                  ) : (
                    <>
                      <Button
                        size="small"
                        startIcon={<Icon name="save" size={16} />}
                        onClick={handleSaveProfile}
                        sx={{ 
                          backgroundColor: '#4ade80',
                          color: '#000000',
                          '&:hover': {
                            backgroundColor: '#22c55e',
                            color: '#000000'
                          }
                        }}
                      >
                        Save
                      </Button>
                      <Button
                        size="small"
                        onClick={() => setEditMode(false)}
                        sx={{ color: '#FFC000' }}
                      >
                        Cancel
                      </Button>
                    </>
                  )}
                </Box>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="body2" sx={{ color: '#FFC000', mb: 1 }}>Name</Typography>
                  <TextField
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    disabled={!editMode}
                    fullWidth
                    variant="outlined"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: editMode ? '#1e293b' : 'transparent',
                        color: '#FFC000',
                        '& fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                        '&:hover fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                        '&.Mui-disabled fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: '#FFC000',
                      },
                      '& .MuiInputBase-input.Mui-disabled': {
                        color: '#FFC000',
                        WebkitTextFillColor: '#FFC000',
                      }
                    }}
                  />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ color: '#FFC000', mb: 1 }}>Role</Typography>
                  <TextField
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    disabled={!editMode}
                    fullWidth
                    variant="outlined"
                    placeholder="e.g., CEO, Developer, Client, Family Member"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: editMode ? '#1e293b' : 'transparent',
                        color: '#FFC000',
                        '& fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                        '&:hover fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                        '&.Mui-disabled fieldset': {
                          borderColor: '#FFC000 !important',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: '#FFC000',
                        '&::placeholder': {
                          color: '#FFC000',
                          opacity: 0.6,
                        },
                      },
                      '& .MuiInputBase-input.Mui-disabled': {
                        color: '#FFC000',
                        WebkitTextFillColor: '#FFC000',
                      }
                    }}
                  />
                </Box>
                <Box>
                  {editMode && (
                    <Button
                      startIcon={<Icon name="add" size={16} />}
                      onClick={handleAddCustomField}
                      sx={{ color: '#FFC000' }}
                    >
                      Add Field
                      <HelpIcon tooltip="Add custom fields like department, skills, or preferences" />
                    </Button>
                  )}
                  
                  {formData.custom_fields.map((field, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2, mt: 2 }}>
                      <TextField
                        label="Field Name"
                        value={field.key}
                        onChange={(e) => handleCustomFieldChange(index, 'key', e.target.value)}
                        disabled={!editMode}
                        sx={{
                          flex: 1,
                          '& .MuiInputLabel-root': {
                            color: '#FFC000',
                          },
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: editMode ? '#1e293b' : 'transparent',
                            color: '#FFC000',
                            '& fieldset': {
                              borderColor: '#FFC000',
                            },
                            '&:hover fieldset': {
                              borderColor: '#FFD700',
                            },
                            '&.Mui-focused fieldset': {
                              borderColor: '#FFD700',
                            },
                          },
                          '& .MuiInputBase-input': {
                            color: '#FFC000',
                          },
                          '& .MuiInputBase-input.Mui-disabled': {
                            color: '#FFC000',
                            WebkitTextFillColor: '#FFC000',
                          }
                        }}
                      />
                      <TextField
                        label="Value"
                        value={field.value}
                        onChange={(e) => handleCustomFieldChange(index, 'value', e.target.value)}
                        disabled={!editMode}
                        sx={{
                          flex: 2,
                          '& .MuiInputLabel-root': {
                            color: '#FFC000',
                          },
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: editMode ? '#1e293b' : 'transparent',
                            color: '#FFC000',
                            '& fieldset': {
                              borderColor: '#FFC000',
                            },
                            '&:hover fieldset': {
                              borderColor: '#FFD700',
                            },
                            '&.Mui-focused fieldset': {
                              borderColor: '#FFD700',
                            },
                          },
                          '& .MuiInputBase-input': {
                            color: '#FFC000',
                          },
                          '& .MuiInputBase-input.Mui-disabled': {
                            color: '#FFC000',
                            WebkitTextFillColor: '#FFC000',
                          }
                        }}
                      />
                      {editMode && (
                        <Icon
                          name="delete"
                          size={20}
                          onClick={() => handleRemoveCustomField(index)}
                          tooltip="Remove field"
                          style={{ color: '#FFC000', cursor: 'pointer' }}
                        />
                      )}
                    </Box>
                  ))}
                </Box>
              </Box>
            </>
          ) : (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '100%',
              color: '#FFC000'
            }}>
              <PersonIcon sx={{ fontSize: 64, mb: 2, color: '#FFC000' }} />
              <Typography variant="h6" sx={{ color: '#FFC000' }}>No Profile Selected</Typography>
              <Typography variant="body2" sx={{ color: '#FFC000' }}>Create a profile to get started</Typography>
            </Box>
          )}
        </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default PersonalProfilesModal;