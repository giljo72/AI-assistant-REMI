import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import authService from '../../services/authService';
import { colors } from '../../styles/colors';

export const SetupWizard: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [needsSetup, setNeedsSetup] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    recovery_pin: '',
    confirmPin: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    checkSetupStatus();
  }, []);

  const checkSetupStatus = async () => {
    try {
      const status = await authService.checkSetupStatus();
      if (!status.needs_setup) {
        // Admin already exists, redirect to login
        navigate('/login');
      } else {
        setNeedsSetup(true);
      }
    } catch (error) {
      console.error('Failed to check setup status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.username) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.recovery_pin) {
      newErrors.recovery_pin = 'Recovery PIN is required';
    } else if (!/^\d{4,6}$/.test(formData.recovery_pin)) {
      newErrors.recovery_pin = 'PIN must be 4-6 digits';
    }

    if (formData.recovery_pin !== formData.confirmPin) {
      newErrors.confirmPin = 'PINs do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.createAdminAccount({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        recovery_pin: formData.recovery_pin,
      });
      
      // Redirect to main app
      navigate('/');
    } catch (error: any) {
      setErrors({
        submit: error.response?.data?.detail || 'Failed to create admin account',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: colors.background,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{ color: colors.yellow, fontSize: '1.5rem' }}>
          Loading...
        </div>
      </div>
    );
  }

  if (!needsSetup) {
    return null;
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: colors.background,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
    }}>
      <div style={{
        background: `linear-gradient(135deg, ${colors.navy.light} 0%, ${colors.navy.DEFAULT} 100%)`,
        borderRadius: '16px',
        padding: '3rem',
        width: '100%',
        maxWidth: '500px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        border: `1px solid ${colors.fadedBlue3}`,
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{
            color: colors.white,
            fontSize: '2.5rem',
            fontWeight: '300',
            marginBottom: '0.5rem',
          }}>
            Welcome to AI Assistant
          </h1>
          <p style={{
            color: colors.whiteGray,
            fontSize: '1rem',
          }}>
            Let's create your administrator account
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {/* Username */}
            <div>
              <label style={{
                display: 'block',
                color: colors.whiteGray,
                fontSize: '0.875rem',
                marginBottom: '0.5rem',
              }}>
                Username
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: colors.fadedBlue2,
                  border: `1px solid ${errors.username ? colors.red : colors.fadedBlue3}`,
                  borderRadius: '8px',
                  color: colors.white,
                  fontSize: '1rem',
                  outline: 'none',
                }}
              />
              {errors.username && (
                <p style={{ color: colors.red, fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  {errors.username}
                </p>
              )}
            </div>

            {/* Email */}
            <div>
              <label style={{
                display: 'block',
                color: colors.whiteGray,
                fontSize: '0.875rem',
                marginBottom: '0.5rem',
              }}>
                Email Address
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: colors.fadedBlue2,
                  border: `1px solid ${errors.email ? colors.red : colors.fadedBlue3}`,
                  borderRadius: '8px',
                  color: colors.white,
                  fontSize: '1rem',
                  outline: 'none',
                }}
              />
              {errors.email && (
                <p style={{ color: colors.red, fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password fields in a row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{
                  display: 'block',
                  color: colors.whiteGray,
                  fontSize: '0.875rem',
                  marginBottom: '0.5rem',
                }}>
                  Password
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: colors.fadedBlue2,
                    border: `1px solid ${errors.password ? colors.red : colors.fadedBlue3}`,
                    borderRadius: '8px',
                    color: colors.white,
                    fontSize: '1rem',
                    outline: 'none',
                  }}
                />
                {errors.password && (
                  <p style={{ color: colors.red, fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.password}
                  </p>
                )}
              </div>

              <div>
                <label style={{
                  display: 'block',
                  color: colors.whiteGray,
                  fontSize: '0.875rem',
                  marginBottom: '0.5rem',
                }}>
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: colors.fadedBlue2,
                    border: `1px solid ${errors.confirmPassword ? colors.red : colors.fadedBlue3}`,
                    borderRadius: '8px',
                    color: colors.white,
                    fontSize: '1rem',
                    outline: 'none',
                  }}
                />
                {errors.confirmPassword && (
                  <p style={{ color: colors.red, fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.confirmPassword}
                  </p>
                )}
              </div>
            </div>

            {/* Recovery PIN section */}
            <div style={{
              padding: '1rem',
              backgroundColor: colors.fadedBlue3,
              borderRadius: '8px',
              marginTop: '0.5rem',
            }}>
              <p style={{
                color: colors.yellow,
                fontSize: '0.875rem',
                marginBottom: '1rem',
                fontWeight: '500',
              }}>
                🔐 Recovery PIN - Store this securely!
              </p>
              <p style={{
                color: colors.whiteGray,
                fontSize: '0.75rem',
                marginBottom: '1rem',
              }}>
                This PIN can be used to recover your admin account if you forget your password.
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{
                    display: 'block',
                    color: colors.whiteGray,
                    fontSize: '0.875rem',
                    marginBottom: '0.5rem',
                  }}>
                    Recovery PIN (4-6 digits)
                  </label>
                  <input
                    type="text"
                    maxLength={6}
                    value={formData.recovery_pin}
                    onChange={(e) => handleInputChange('recovery_pin', e.target.value.replace(/\D/g, ''))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      backgroundColor: colors.fadedBlue2,
                      border: `1px solid ${errors.recovery_pin ? colors.red : colors.fadedBlue3}`,
                      borderRadius: '8px',
                      color: colors.white,
                      fontSize: '1rem',
                      outline: 'none',
                    }}
                  />
                  {errors.recovery_pin && (
                    <p style={{ color: colors.red, fontSize: '0.75rem', marginTop: '0.25rem' }}>
                      {errors.recovery_pin}
                    </p>
                  )}
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    color: colors.whiteGray,
                    fontSize: '0.875rem',
                    marginBottom: '0.5rem',
                  }}>
                    Confirm PIN
                  </label>
                  <input
                    type="text"
                    maxLength={6}
                    value={formData.confirmPin}
                    onChange={(e) => handleInputChange('confirmPin', e.target.value.replace(/\D/g, ''))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      backgroundColor: colors.fadedBlue2,
                      border: `1px solid ${errors.confirmPin ? colors.red : colors.fadedBlue3}`,
                      borderRadius: '8px',
                      color: colors.white,
                      fontSize: '1rem',
                      outline: 'none',
                    }}
                  />
                  {errors.confirmPin && (
                    <p style={{ color: colors.red, fontSize: '0.75rem', marginTop: '0.25rem' }}>
                      {errors.confirmPin}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {errors.submit && (
              <div style={{
                backgroundColor: colors.darkRed,
                color: colors.red,
                padding: '0.75rem',
                borderRadius: '8px',
                fontSize: '0.875rem',
                textAlign: 'center',
              }}>
                {errors.submit}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                width: '100%',
                padding: '0.875rem',
                backgroundColor: colors.yellow,
                color: colors.navy.DEFAULT,
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                opacity: isSubmitting ? 0.7 : 1,
                transition: 'all 0.2s',
                marginTop: '1rem',
              }}
              onMouseEnter={(e) => {
                if (!isSubmitting) {
                  e.currentTarget.style.backgroundColor = colors.darkYellow;
                  e.currentTarget.style.color = colors.white;
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = colors.yellow;
                e.currentTarget.style.color = colors.navy.DEFAULT;
              }}
            >
              {isSubmitting ? 'Creating Account...' : 'Create Admin Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};