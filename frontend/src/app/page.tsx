'use client';
import { Canvas } from '@react-three/fiber';
import { useJarvis } from '@/hooks/useJarvis';
import JarvisOrb from '@/components/JarvisOrb';
import Image from 'next/image';

export default function Home() {
  const { state, text } = useJarvis();

  return (
    <main className="flex h-screen w-screen bg-transparent overflow-hidden font-sans justify-end">
      {/* Container Principal com área de arraste no topo */}
      <div className="w-[450px] h-full border-l border-white/10 bg-zinc-950/90 backdrop-blur-3xl flex flex-col p-6 relative shadow-[-20px_0_50px_rgba(0,0,0,0.8)]">
        
        {/* Barra de Arraste Invisível no topo */}
        <div className="absolute top-0 left-0 w-full h-8 cursor-move" style={{ WebkitAppRegion: 'drag' } as any} />

        <button 
          onClick={() => window.close()} 
          className="absolute top-4 right-4 text-zinc-600 hover:text-red-500 transition-colors z-50 p-2"
          style={{ WebkitAppRegion: 'no-drag' } as any} // Botões não devem ser arrastáveis
          title="Fechar Jarvis"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        {/* Header com Logo */}
        <div className="w-full flex items-center gap-4 mb-6 border-b border-white/5 pb-4">
          <div className="relative w-12 h-12 flex-shrink-0">
            <div className="absolute inset-0 rounded-full bg-cyan-500/10 animate-pulse" />
            <div className="relative w-full h-full rounded-full border border-cyan-500/30 overflow-hidden bg-black flex items-center justify-center">
              <Image 
                src="/jarvis.PNG" 
                alt="Jarvis Core" 
                fill
                className="object-cover scale-125"
              />
            </div>
          </div>
          
          <div className="flex flex-col">
            <h1 className="text-white tracking-[0.3em] uppercase text-[10px] font-bold opacity-60">
              Protocol Mark VII
            </h1>
            <p className={`text-[9px] font-mono uppercase tracking-[0.2em] ${
              state === 'idle' ? 'text-zinc-600' : 'text-cyan-400 animate-pulse'
            }`}>
              {state === 'idle' ? 'System_Standby' : `Active_${state}`}
            </p>
          </div>
        </div>

        {/* Orbe de Partículas */}
        <div className="w-full h-[300px] relative mt-2">
          <Canvas camera={{ position: [0, 0, 15] }}>
            <color attach="background" args={['#000000']} />
            <ambientLight intensity={0.5} />
            <JarvisOrb state={state} />
          </Canvas>
          <div className="absolute inset-0 pointer-events-none bg-radial-gradient from-transparent to-zinc-950" />
        </div>

        {/* Zona de Resposta Futurista */}
        <div className="w-full flex-1 mt-6 relative overflow-hidden flex flex-col">
          <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-500/40" />
          <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-500/40" />

          <div className="flex-1 bg-cyan-950/5 border border-white/5 rounded-sm p-5 overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-500/20 scrollbar-track-transparent">
            <div className="space-y-4">
              <div className="flex items-center gap-2 opacity-40">
                <div className="w-1 h-1 bg-cyan-400 rounded-full animate-ping" />
                <p className="text-cyan-400 font-mono text-[9px] uppercase tracking-widest">
                  Live_Terminal_Output
                </p>
              </div>
              
              <p className="text-white/80 font-light text-[1.05rem] leading-[1.7] text-justify selection:bg-cyan-500/30">
                {state === 'idle' ? (
                  <span className="opacity-20 italic">Sistemas em espera. Invoque para interagir.</span>
                ) : (
                  text
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Footer Minimalista */}
        <div className="w-full mt-6 pt-4 border-t border-white/5 flex justify-between items-center text-[8px] text-zinc-600 font-mono tracking-[0.2em] uppercase">
          <span>ENC_PROT_07</span>
          <span className="text-cyan-900/50">SRG_USR: GENILSSON</span> 
        </div>
      </div>
    </main>
  );
}