import React from 'react';
import './VoiceIcon.css'; // 你的 CSS 动画

export default function VoiceIcon({ playing, reversed }: { playing: boolean; reversed?: boolean }) {
    const transformStyle = reversed ? { transform: 'scaleX(-1)' } : undefined;

    return (
        <div style={{ display: 'flex', alignItems: 'center', width: '16px', height: '16px', ...transformStyle }}>
            {playing ? (
                <div style={{ display: 'flex', gap: '2px', alignItems: 'flex-end' }}>
                    <div className="wave-bar" style={{ height: '8px' }} />
                    <div className="wave-bar" style={{ height: '12px', animationDelay: '0.1s' }} />
                    <div className="wave-bar" style={{ height: '10px', animationDelay: '0.2s' }} />
                </div>
            ) : (
                <svg
                    style={{ width: '16px', height: '16px' }}
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path d="M3 9v6h4l5 5V4l-5 5H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.06c1.48-.74 2.5-2.26 2.5-4.03z" />
                </svg>
            )}
        </div>
    );
}
