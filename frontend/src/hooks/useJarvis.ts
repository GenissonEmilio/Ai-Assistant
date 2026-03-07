import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

export const useJarvis = () => {
  const [state, setState] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  const [text, setText] = useState('');

  useEffect(() => {
    const socket = io('http://127.0.0.1:5000');

    socket.on('jarvis_state', (data) => {
      setState(data.state);
      if (data.data?.text) setText(data.data.text);
    });

    return () => { socket.disconnect(); };
  }, []);

  return { state, text };
};