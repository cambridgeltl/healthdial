import { Tag, Card } from 'antd';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bubble, Typing } from '@chatui/core';
import VoiceBubble from "./VoiceBubble";

export default function RenderMessageContent({ m }: { m: any }) {
    const [showEvidence, setShowEvidence] = useState(false);

    if (m.type === 'text' || m.type === 'voice') {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: m.position === 'right' ? 'flex-end' : 'flex-start', gap: 6 }}>
                {/* 文字泡泡 or 语音泡泡 */}
                {m.type === 'text' ? (
                    <Bubble content={m.content.text} />
                ) : (
                    <VoiceBubble
                        url={m.content.url}
                        duration={m.content.dur}
                        position={m.position as 'left' | 'right'}
                        sending={m.content?.sending === true}
                    />
                )}

                {/* snippet evidences */}
                {m.snippet && m.snippet.length > 0 && (
                    <div style={{ marginTop: '4px' }}>
                        <Tag
                            bordered={false}
                            color="blue"
                            style={{ width: 'fit-content', cursor: 'pointer' }}
                            onClick={() => setShowEvidence((prev) => !prev)}
                        >
                            {showEvidence ? 'Hide Evidence' : 'Show Evidence'}
                        </Tag>

                        {/* 动画展开收起 */}
                        <AnimatePresence>
                            {showEvidence && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.3 }}
                                    style={{ overflow: 'hidden', marginTop: '8px', width: '100%' }}
                                >
                                    {/* 每条 Evidence 用一个小卡片 Card 展示 */}
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        {m.snippet.map((item: any, idx: number) => (
                                            <Card key={idx} size="small" bordered style={{ background: '#f4f6f8' }}>
                                                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{item.data.title}</div>
                                                <div style={{ marginBottom: '6px', fontSize: '13px', color: '#555' }}>{item.data.content}</div>
                                                <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '12px', color: '#1a73e8' }}>
                                                    {item.url}
                                                </a>
                                            </Card>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                )}
            </div>
        );
    }

    if (m.type === 'custom') {
        if (m.content?.customType === 'listening') {
            return <Typing text="Listening..." />;
        }
        if (m.content?.customType === 'thinking') {
            return <Typing text="System is thinking..." />;
        }
    }

    return null;
}
