import React, { useState, useEffect, useRef, useCallback } from 'react';
import Chat from '@chatui/core';
import '@chatui/core/dist/index.css';
import { useReactMediaRecorder } from 'react-media-recorder';
import { nanoid } from 'nanoid';
import io from 'socket.io-client';
import { dialogue_url } from './configs';
import RenderMessageContent from "./renderMessageContent";

const BOT_AVATAR = 'https://cdn.who.int/media/images/default-source/infographics/who-emblem.png?sfvrsn=877bb56a_2';
const USER_AVATAR = '/logo192.png';
const LISTENING_MESSAGE_ID = 'listening-msg';
const THINKING_MESSAGE_ID = 'thinking-msg';

const initialMessages = [
  {
    type: 'system',
    content: { text: 'System connected. You are now chatting with the WHO health‑advisor chatbot.' },
  },
  {
    type: 'text',
    content: { text: 'Hello, I’m your WHO health‑advisor. How can I help you today?' },
    user: { avatar: BOT_AVATAR },
    position: 'left',
  },
];

export default function VoiceChatBox() {
  const [messages, setMessages] = useState<any[]>(initialMessages);
  const [recording, setRecording] = useState(false);
  const [recStart, setRecStart] = useState<number | null>(null);
  const { startRecording, stopRecording, mediaBlobUrl, clearBlobUrl } = useReactMediaRecorder({
    audio: true,
    mediaRecorderOptions: { mimeType: 'audio/webm' },
  });
  const socketRef = useRef<any>(null);

  const appendMsg = useCallback((msg: any) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const updateMsg = useCallback((id: string, newContent: Partial<any['content']>) => {
    setMessages((prev) =>
        prev.map((m) => (m._id === id ? { ...m, content: { ...m.content, ...newContent } } : m))
    );
  }, []);

  const removeMsg = useCallback((id: string) => {
    setMessages((prev) => prev.filter((m) => m._id !== id));
  }, []);

  useEffect(() => {
    const socket = io(dialogue_url, {
      transports: ['websocket', 'polling'],
      reconnectionDelayMax: 5002,
    });

    socket.on('system_message', (data: any) => {
      removeMsg(THINKING_MESSAGE_ID);

      if (typeof data === 'string') {
        appendMsg({
          _id: nanoid(),
          type: 'text',
          content: { text: data },
          position: 'left',
          user: { avatar: BOT_AVATAR },
        });
      } else if (data.type === 'text') {
        appendMsg({
          _id: nanoid(),
          type: 'text',
          content: { text: data.system_text },
          position: 'left',
          user: { avatar: BOT_AVATAR },
          snippet: data.snippet || [],
        });
      } else if (data.type === 'voice') {
        appendMsg({
          _id: nanoid(),
          type: 'voice',
          content: { url: data.audio_url, dur: parseInt(data.audio_dur || '5') },
          position: 'left',
          user: { avatar: BOT_AVATAR },
          snippet: data.snippet || [],
        });
      }
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [appendMsg, removeMsg]);

  const sendText = useCallback((text: string) => {
    const msg = {
      _id: nanoid(),
      type: 'text',
      content: { text },
      position: 'right',
      user: { avatar: USER_AVATAR },
    };
    appendMsg(msg);

    appendMsg({
      _id: THINKING_MESSAGE_ID,
      type: 'custom',
      content: { customType: 'thinking' },
      position: 'left',
    });

    socketRef.current?.emit('user_message', text);
  }, [appendMsg]);

  const sendVoice = useCallback(async (url: string, dur: number, blob: Blob) => {
    const id = nanoid();
    appendMsg({
      _id: id,
      type: 'voice',
      content: { url, dur, sending: true },
      position: 'right',
      user: { avatar: USER_AVATAR },
    });

    appendMsg({
      _id: THINKING_MESSAGE_ID,
      type: 'custom',
      content: { customType: 'thinking' },
      position: 'left',
    });

    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = () => {
      const base64data = reader.result;
      socketRef.current?.emit('user_voice', { audio: base64data });
      updateMsg(id, { sending: false });
    };
  }, [appendMsg, updateMsg]);

  const blobUrlRef = useRef<string | null>(null);
  useEffect(() => {
    if (mediaBlobUrl && mediaBlobUrl !== blobUrlRef.current) {
      blobUrlRef.current = mediaBlobUrl;
      (async () => {
        const blob = await (await fetch(mediaBlobUrl)).blob();
        const localUrl = URL.createObjectURL(blob);
        clearBlobUrl();
        const dur = recStart ? Math.max(1, Math.round((Date.now() - recStart) / 1000)) : 0;
        sendVoice(localUrl, dur, blob);
        setRecStart(null);
      })();
    }
  }, [mediaBlobUrl, clearBlobUrl, recStart, sendVoice]);

  const toggleRecord = () => {
    if (recording) {
      stopRecording();
      setRecording(false);
      removeMsg(LISTENING_MESSAGE_ID);
    } else {
      setRecStart(Date.now());
      startRecording();
      setRecording(true);
      appendMsg({
        _id: LISTENING_MESSAGE_ID,
        type: 'custom',
        content: { customType: 'listening' },
        position: 'right',
      });
    }
  };

  const handleSend = useCallback((type: string, val: string) => {
    if (type === 'text' && val.trim()) sendText(val.trim());
  }, [sendText]);

  return (

      <Chat
          locale="en-US"
          navbar={{ title: 'WHO Health Advice Chatbot' }}
          messages={messages}
          renderMessageContent={(m) => <RenderMessageContent m={m} />}
          onSend={handleSend}
          placeholder="Type your message here..."
          inputType="text"
          rightAction={{
            icon: recording ? 'x-circle-fill' : 'mic',
            title: recording ? 'Stop' : 'Voice',
            onClick: toggleRecord,
          }}
      />
  );
}
