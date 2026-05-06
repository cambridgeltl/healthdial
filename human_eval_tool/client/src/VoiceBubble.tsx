import React, { useState, useEffect, useRef } from 'react';
import VoiceIcon from './VoiceIcon';

let globalAudio: HTMLAudioElement | null = null;

function calcBubbleWidth(duration: number): number {
    if (duration <= 2) return 80;
    if (duration <= 10) return 80 + (duration - 2) * 20;
    if (duration <= 60) return 240 + (duration - 10) * 2;
    return 340;
}

interface VoiceBubbleProps {
    url: string;
    duration?: number;
    position?: 'left' | 'right'; // ✅ 注意这里是可选
    sending?: boolean;
}

export default function VoiceBubble(props: VoiceBubbleProps) {
    const {
        url,
        duration,
        position = 'right',  // ✅ 正确的默认值设置（在这里）
        sending = false,
    } = props;

    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [playing, setPlaying] = useState(false);
    const [len, setLen] = useState<number>(duration ?? 0);

    const togglePlay = () => {
        if (sending) return;
        const audio = audioRef.current;
        if (!audio) return;

        if (audio === globalAudio) {
            audio.pause();
            return;
        }

        if (globalAudio) {
            globalAudio.pause();
        }

        audio.play();
        globalAudio = audio;
    };

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const onLoaded = () => {
            if (!len && isFinite(audio.duration)) {
                setLen(Math.round(audio.duration));
            }
        };

        const onPlay = () => setPlaying(true);
        const onPauseOrEnd = () => {
            setPlaying(false);
            if (globalAudio === audio) {
                globalAudio = null;
            }
        };

        audio.addEventListener('loadedmetadata', onLoaded);
        audio.addEventListener('play', onPlay);
        audio.addEventListener('pause', onPauseOrEnd);
        audio.addEventListener('ended', onPauseOrEnd);

        return () => {
            audio.removeEventListener('loadedmetadata', onLoaded);
            audio.removeEventListener('play', onPlay);
            audio.removeEventListener('pause', onPauseOrEnd);
            audio.removeEventListener('ended', onPauseOrEnd);
        };
    }, [len]);

    const bubbleWidth = calcBubbleWidth(len || 1);
    const isRight = position === 'right';

    return (
        <div
            onClick={togglePlay}
            style={{
                display: 'flex',
                flexDirection: isRight ? 'row-reverse' : 'row',
                alignItems: 'center',
                justifyContent: 'flex-start',
                gap: '6px',
                width: `${bubbleWidth}px`,
                padding: '8px 12px',
                borderRadius: '16px',
                backgroundColor: isRight ? '#95ec69' : '#ffffff',
                color: isRight ? '#ffffff' : '#333333',
                cursor: sending ? 'default' : 'pointer',
                userSelect: 'none',
                opacity: sending ? 0.6 : 1,
                height: '32px',
                boxSizing: 'border-box',
            }}
        >
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    height: '16px',
                    lineHeight: '1',
                }}
            >
                {sending ? (
                    <div
                        style={{
                            width: '16px',
                            height: '16px',
                            border: '2px solid currentColor',
                            borderTop: '2px solid transparent',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite',
                        }}
                    />
                ) : isRight ? (
                    <>
                        {/* 右边：秒数 + 喇叭 */}
                        <span
                            style={{
                                fontSize: '14px',
                                whiteSpace: 'nowrap',
                                display: 'inline-block',
                                height: '16px',
                                lineHeight: '16px',
                            }}
                        >
              {len ? `${len}″` : '…'}
            </span>
                        <VoiceIcon playing={playing} reversed={true} />
                    </>
                ) : (
                    <>
                        {/* 左边：喇叭 + 秒数 */}
                        <VoiceIcon playing={playing} reversed={false} />
                        <span
                            style={{
                                fontSize: '14px',
                                whiteSpace: 'nowrap',
                                display: 'inline-block',
                                height: '16px',
                                lineHeight: '16px',
                            }}
                        >
              {len ? `${len}″` : '…'}
            </span>
                    </>
                )}
            </div>

            <audio ref={audioRef} src={url} preload="metadata" hidden />
        </div>
    );
}
