import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { colors } from '../../styles/colors';

interface WelcomeScreenProps {
  hasProjects: boolean;
  onStartProject: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ hasProjects, onStartProject }) => {
  const { user } = useAuth();

  const getInitial = () => {
    return user?.username?.charAt(0).toUpperCase() || 'U';
  };

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
      }}
    >
      <div
        style={{
          backgroundColor: colors.navy.light,
          border: `2px solid ${colors.yellow}`,
          borderRadius: '24px',
          padding: '4rem 3rem',
          maxWidth: '600px',
          width: '100%',
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            color: colors.white,
            fontSize: '3rem',
            fontWeight: '300',
            marginBottom: '2rem',
          }}
        >
          Hi, {user?.username}!
        </h1>

        <div
          style={{
            width: '80px',
            height: '80px',
            backgroundColor: colors.yellow,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 3rem',
            fontSize: '2.5rem',
            fontWeight: '600',
            color: colors.navy.DEFAULT,
          }}
        >
          {getInitial()}
        </div>

        {!hasProjects && (
          <>
            <button
              onClick={onStartProject}
              style={{
                width: '60px',
                height: '60px',
                backgroundColor: 'transparent',
                border: `2px solid ${colors.yellow}`,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
                fontSize: '1.5rem',
                color: colors.yellow,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = colors.yellow;
                e.currentTarget.style.color = colors.navy.DEFAULT;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = colors.yellow;
              }}
            >
              +
            </button>
            <p style={{ color: colors.white, fontSize: '1.125rem' }}>
              Start a project
            </p>
          </>
        )}

        {hasProjects && (
          <p style={{ color: colors.whiteGray, fontSize: '1.125rem' }}>
            Welcome back! Select a project from the sidebar to continue.
          </p>
        )}
      </div>
    </div>
  );
};