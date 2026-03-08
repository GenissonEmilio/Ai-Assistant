'use client';
import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { useJarvis } from '@/hooks/useJarvis';
import JarvisOrb from '@/components/JarvisOrb';
import Image from 'next/image';
import { io } from 'socket.io-client';

const socket = io('http://127.0.0.1:5000');

export default function Home() {
  const { state, text, setState, setText } = useJarvis();
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    socket.emit('send_text_command', { text: inputValue });
    setInputValue('');
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT') return;
      if (e.key === '1') setState('listening');
      if (e.key === '2') setState('thinking');
      if (e.key === '3') setState('speaking');
      if (e.key === '0') setState('idle');
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setState]);

  return (
    <main className="flex h-screen w-screen bg-zinc-950 overflow-hidden font-sans justify-end">
      <div className="w-[450px] h-full border-l border-white/10 bg-zinc-900/90 backdrop-blur-3xl flex flex-col p-6 relative shadow-[-20px_0_50px_rgba(0,0,0,0.8)]">
        
        <div className="absolute top-0 left-0 w-full h-10 cursor-move z-40" style={{ WebkitAppRegion: 'drag' } as any} />

        {/* Header */}
        <div className="w-full flex items-center gap-4 mb-4 border-b border-white/5 pb-4">
          <div className="relative w-12 h-12">
            <div className="absolute inset-0 rounded-full bg-cyan-500/10 animate-pulse" />
            <div className="relative w-full h-full rounded-full border border-cyan-500/30 overflow-hidden bg-black flex items-center justify-center">
              <Image src="/jarvis.PNG" alt="Jarvis" fill className="object-cover scale-125" />
            </div>
          </div>
          <div>
            <h1 className="text-white tracking-[0.3em] uppercase text-[10px] font-bold opacity-60">Protocol Mark VII</h1>
            <p className={`text-[9px] font-mono uppercase tracking-[0.2em] ${state === 'idle' ? 'text-zinc-600' : 'text-cyan-400 animate-pulse'}`}>
              {state === 'idle' ? 'System_Standby' : `Active_${state}`}
            </p>
          </div>
        </div>

        {/* Orbe */}
        <div className="w-full h-[250px] relative">
          <Canvas camera={{ position: [0, 0, 15] }}>
            <ambientLight intensity={0.5} />
            <JarvisOrb state={state} />
          </Canvas>
        </div>

        {/* Console / Resposta */}
        <div className="flex-1 bg-black/40 border border-white/5 rounded-sm p-4 overflow-y-auto mb-4 font-mono text-[13px]">
          <div className="flex items-center gap-2 opacity-40 mb-2">
            <div className="w-1 h-1 bg-cyan-400 rounded-full animate-ping" />
            <span className="text-cyan-400 text-[9px] tracking-widest uppercase">Live_Terminal</span>
          </div>
          <p className="text-white/80 leading-relaxed italic">
            {state === 'idle' ? '> Aguardando comando...' : text}
          </p>
        </div>

        {/* INPUT DE TEXTO HÍBRIDO */}
        <form onSubmit={handleSendMessage} className="relative group mb-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Digite um comando para o Jarvis..."
            className="w-full bg-zinc-950 border border-white/10 rounded-sm py-3 px-4 text-white text-xs focus:outline-none focus:border-cyan-500/50 transition-all font-mono placeholder:opacity-30"
          />
          <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 text-cyan-500 opacity-50 hover:opacity-100">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
          </button>
        </form>

        {/* Footer com botões de teste de Orbe */}
        <div className="flex justify-between items-center text-[8px] text-zinc-600 font-mono tracking-tighter uppercase mt-2">
          <div className="flex gap-2">
            <span>MODO_TESTE:</span>
            <button onClick={() => setState('listening')} className="hover:text-cyan-500">[OUVIR]</button>
            <button onClick={() => setState('thinking')} className="hover:text-cyan-500">[PENSAR]</button>
            <button onClick={() => setState('speaking')} className="hover:text-cyan-500">[FALAR]</button>
            <button onClick={() => setState('idle')} className="hover:text-white">[RESET]</button>
          </div>
          <span>SRG_USR: GENILSSON</span> 
        </div>
      </div>
    </main>
  );
}