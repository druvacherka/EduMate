import React from 'react';
import { RotateCw } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: number;
  message?: string;
  fullscreen?: boolean;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 24,
  message,
  fullscreen = false,
  className = '',
}) => {
  const content = (
    <div
      className={`fade-in ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 12,
        color: 'var(--text-secondary, #94a3b8)',
        padding: fullscreen ? 0 : 24,
      }}
    >
      <RotateCw
        className="animate-spin"
        size={size}
        style={{ color: 'var(--accent-secondary, #38bdf8)' }}
      />
      {message && (
        <span style={{ fontSize: '0.88rem', fontWeight: 500, letterSpacing: '0.2px' }}>
          {message}
        </span>
      )}
    </div>
  );

  if (fullscreen) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          width: '100%',
          minHeight: 280,
        }}
      >
        {content}
      </div>
    );
  }

  return content;
};

export default LoadingSpinner;
