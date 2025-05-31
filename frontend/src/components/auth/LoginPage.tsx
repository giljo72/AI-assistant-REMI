import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import authService from '../../services/authService';
import { colors } from '../../styles/colors';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isCheckingSetup, setIsCheckingSetup] = useState(true);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    checkSetupStatus();
  }, []);

  const checkSetupStatus = async () => {
    try {
      const status = await authService.checkSetupStatus();
      if (status.needs_setup) {
        navigate('/setup');
      }
    } catch (error) {
      console.error('Failed to check setup status:', error);
    } finally {
      setIsCheckingSetup(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ username, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  if (isCheckingSetup) {
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

  return (
    <div 
      style={{
        minHeight: '100vh',
        backgroundColor: colors.background,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
      }}
    >
      <div
        style={{
          background: `linear-gradient(135deg, ${colors.navy.light} 0%, ${colors.navy.DEFAULT} 100%)`,
          borderRadius: '16px',
          padding: '3rem',
          width: '100%',
          maxWidth: '400px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          border: `1px solid ${colors.fadedBlue3}`,
        }}
      >
        <h1
          style={{
            color: colors.white,
            fontSize: '2.5rem',
            fontWeight: '300',
            textAlign: 'center',
            marginBottom: '2rem',
          }}
        >
          Welcome Back
        </h1>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label
              htmlFor="username"
              style={{
                display: 'block',
                color: colors.whiteGray,
                fontSize: '0.875rem',
                marginBottom: '0.5rem',
              }}
            >
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: colors.fadedBlue2,
                border: `1px solid ${colors.fadedBlue3}`,
                borderRadius: '8px',
                color: colors.white,
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = colors.yellow;
              }}
              onBlur={(e) => {
                e.target.style.borderColor = colors.fadedBlue3;
              }}
            />
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <label
              htmlFor="password"
              style={{
                display: 'block',
                color: colors.whiteGray,
                fontSize: '0.875rem',
                marginBottom: '0.5rem',
              }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: colors.fadedBlue2,
                border: `1px solid ${colors.fadedBlue3}`,
                borderRadius: '8px',
                color: colors.white,
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = colors.yellow;
              }}
              onBlur={(e) => {
                e.target.style.borderColor = colors.fadedBlue3;
              }}
            />
          </div>

          {error && (
            <div
              style={{
                backgroundColor: colors.darkRed,
                color: colors.red,
                padding: '0.75rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontSize: '0.875rem',
                textAlign: 'center',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '0.875rem',
              backgroundColor: colors.yellow,
              color: colors.navy.DEFAULT,
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = colors.darkYellow;
                e.currentTarget.style.color = colors.white;
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = colors.yellow;
              e.currentTarget.style.color = colors.navy.DEFAULT;
            }}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div
          style={{
            marginTop: '2rem',
            paddingTop: '2rem',
            borderTop: `1px solid ${colors.fadedBlue3}`,
            textAlign: 'center',
          }}
        >
          <p style={{ color: colors.darkGray, fontSize: '0.875rem' }}>
            First time user?
          </p>
          <button
            onClick={() => navigate('/setup')}
            style={{
              color: colors.yellow,
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.875rem',
              marginTop: '0.5rem',
              textDecoration: 'underline',
            }}
          >
            Create Admin Account
          </button>
        </div>
      </div>
    </div>
  );
};