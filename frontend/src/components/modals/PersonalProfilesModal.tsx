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
  Tabs,
  Tab,
  Box,
  Typography,
  Chip,
  Divider
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Save as SaveIcon
} from '@mui/icons-material';

interface PersonProfile {
  id: string;
  name: string;
  role?: string;
  address?: string;
  customFields: Array<{ key: string; value: string }>;
  isDefault?: boolean;
}

interface PersonalProfilesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PersonalProfilesModal: React.FC<PersonalProfilesModalProps> = ({ isOpen, onClose }) => {
  const [profiles, setProfiles] = useState<PersonProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<PersonProfile | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [editMode, setEditMode] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    address: '',
    customFields: [] as Array<{ key: string; value: string }>
  });

  // Load profiles from localStorage on mount
  useEffect(() => {
    const savedProfiles = localStorage.getItem('personalProfiles');
    if (savedProfiles) {
      const parsed = JSON.parse(savedProfiles);
      setProfiles(parsed);
      // Set the default profile as selected
      const defaultProfile = parsed.find((p: PersonProfile) => p.isDefault);
      if (defaultProfile) {
        setSelectedProfile(defaultProfile);
        setFormData({
          name: defaultProfile.name,
          role: defaultProfile.role || '',
          address: defaultProfile.address || '',
          customFields: defaultProfile.customFields || []
        });
      }
    }
  }, []);

  // Save profiles to localStorage
  const saveProfiles = (updatedProfiles: PersonProfile[]) => {
    localStorage.setItem('personalProfiles', JSON.stringify(updatedProfiles));
    setProfiles(updatedProfiles);
  };

  const handleAddProfile = () => {
    const newProfile: PersonProfile = {
      id: Date.now().toString(),
      name: 'New Profile',
      role: '',
      address: '',
      customFields: [],
      isDefault: profiles.length === 0
    };
    
    const updatedProfiles = [...profiles, newProfile];
    saveProfiles(updatedProfiles);
    setSelectedProfile(newProfile);
    setFormData({
      name: newProfile.name,
      role: '',
      address: '',
      customFields: []
    });
    setEditMode(true);
    setActiveTab(0);
  };

  const handleSaveProfile = () => {
    if (!selectedProfile) return;
    
    const updatedProfiles = profiles.map(p => 
      p.id === selectedProfile.id 
        ? { ...p, ...formData }
        : p
    );
    
    saveProfiles(updatedProfiles);
    setSelectedProfile({ ...selectedProfile, ...formData });
    setEditMode(false);
  };

  const handleDeleteProfile = (profileId: string) => {
    const updatedProfiles = profiles.filter(p => p.id !== profileId);
    
    // If deleting the default, make the first remaining profile default
    if (profiles.find(p => p.id === profileId)?.isDefault && updatedProfiles.length > 0) {
      updatedProfiles[0].isDefault = true;
    }
    
    saveProfiles(updatedProfiles);
    
    if (selectedProfile?.id === profileId) {
      setSelectedProfile(updatedProfiles[0] || null);
      if (updatedProfiles[0]) {
        setFormData({
          name: updatedProfiles[0].name,
          address: updatedProfiles[0].address || '',
          customFields: updatedProfiles[0].customFields || []
        });
      }
    }
  };

  const handleSetDefault = (profileId: string) => {
    const updatedProfiles = profiles.map(p => ({
      ...p,
      isDefault: p.id === profileId
    }));
    saveProfiles(updatedProfiles);
  };

  const handleAddCustomField = () => {
    setFormData({
      ...formData,
      customFields: [...formData.customFields, { key: '', value: '' }]
    });
  };

  const handleCustomFieldChange = (index: number, field: 'key' | 'value', value: string) => {
    const updatedFields = [...formData.customFields];
    updatedFields[index][field] = value;
    setFormData({ ...formData, customFields: updatedFields });
  };

  const handleRemoveCustomField = (index: number) => {
    const updatedFields = formData.customFields.filter((_, i) => i !== index);
    setFormData({ ...formData, customFields: updatedFields });
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
          <Typography variant="h6">Personal Profiles</Typography>
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', minHeight: '500px' }}>
        {/* Instructions Banner */}
        <Box sx={{ 
          p: 2, 
          backgroundColor: '#1a2b47',
          borderBottom: '1px solid #2d3748',
          textAlign: 'center'
        }}>
          <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.6 }}>
            Create profiles for yourself and people you work with. The AI Assistant will use this information
            to better understand context when you mention these people or discuss related topics.
            Your profiles help the AI provide more personalized and relevant assistance.
          </Typography>
        </Box>
        
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
              startIcon={<AddIcon />}
              onClick={handleAddProfile}
              sx={{
                backgroundColor: '#d4af37',
                color: '#FFC000',
                '&:hover': {
                  backgroundColor: '#b8941f',
                  color: '#FFD700'
                }
              }}
            >
              Add Profile
            </Button>
          </Box>
          
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
                    address: profile.address || '',
                    customFields: profile.customFields || []
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
                  secondary={profile.isDefault && (
                    <Chip 
                      label="Default" 
                      size="small" 
                      sx={{ 
                        backgroundColor: '#d4af37',
                        color: '#FFC000',
                        height: '16px',
                        fontSize: '0.7rem'
                      }}
                    />
                  )}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        {/* Right Panel - Profile Details */}
        <Box sx={{ flex: 1, p: 3 }}>
          {selectedProfile ? (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  {editMode ? 'Edit Profile' : 'Profile Details'}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!editMode ? (
                    <>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => setEditMode(true)}
                        sx={{ color: '#d4af37' }}
                      >
                        Edit
                      </Button>
                      {!selectedProfile.isDefault && (
                        <Button
                          size="small"
                          onClick={() => handleSetDefault(selectedProfile.id)}
                          sx={{ color: '#4ade80' }}
                        >
                          Set as Default
                        </Button>
                      )}
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteProfile(selectedProfile.id)}
                        sx={{ color: '#ef4444' }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </>
                  ) : (
                    <>
                      <Button
                        size="small"
                        startIcon={<SaveIcon />}
                        onClick={handleSaveProfile}
                        sx={{ 
                          backgroundColor: '#4ade80',
                          color: '#FFC000',
                          '&:hover': {
                            backgroundColor: '#22c55e',
                            color: '#FFD700'
                          }
                        }}
                      >
                        Save
                      </Button>
                      <Button
                        size="small"
                        onClick={() => setEditMode(false)}
                        sx={{ color: '#94a3b8' }}
                      >
                        Cancel
                      </Button>
                    </>
                  )}
                </Box>
              </Box>

              <Tabs 
                value={activeTab} 
                onChange={(_, v) => setActiveTab(v)}
                sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
              >
                <Tab label="Basic Info" />
                <Tab label="Custom Fields" />
              </Tabs>

              {activeTab === 0 && (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField
                    label="Name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    disabled={!editMode}
                    fullWidth
                    variant="outlined"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: editMode ? '#1e293b' : 'transparent',
                      }
                    }}
                  />
                  <TextField
                    label="Role"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    disabled={!editMode}
                    fullWidth
                    variant="outlined"
                    placeholder="e.g., CEO, Developer, Client, Family Member"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: editMode ? '#1e293b' : 'transparent',
                      }
                    }}
                  />
                  <TextField
                    label="Address"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    disabled={!editMode}
                    fullWidth
                    multiline
                    rows={3}
                    variant="outlined"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: editMode ? '#1e293b' : 'transparent',
                      }
                    }}
                  />
                </Box>
              )}

              {activeTab === 1 && (
                <Box>
                  {editMode && (
                    <Button
                      startIcon={<AddIcon />}
                      onClick={handleAddCustomField}
                      sx={{ mb: 2, color: '#d4af37' }}
                    >
                      Add Field
                    </Button>
                  )}
                  
                  {formData.customFields.map((field, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                      <TextField
                        label="Field Name"
                        value={field.key}
                        onChange={(e) => handleCustomFieldChange(index, 'key', e.target.value)}
                        disabled={!editMode}
                        sx={{
                          flex: 1,
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: editMode ? '#1e293b' : 'transparent',
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
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: editMode ? '#1e293b' : 'transparent',
                          }
                        }}
                      />
                      {editMode && (
                        <IconButton
                          onClick={() => handleRemoveCustomField(index)}
                          sx={{ color: '#ef4444' }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </>
          ) : (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '100%',
              color: '#64748b'
            }}>
              <PersonIcon sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h6">No Profile Selected</Typography>
              <Typography variant="body2">Create a profile to get started</Typography>
            </Box>
          )}
        </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default PersonalProfilesModal;