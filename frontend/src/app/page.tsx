'use client';
import { Canvas } from '@react-three/fiber';
import { useJarvis } from '@/hooks/useJarvis';
import JarvisOrb from '@/components/JarvisOrb';

export default function Home() {
  const { state, text } = useJarvis();

  return (
    <main className="flex h-screen w-screen bg-black overflow-hidden">
      {/* Lado Esquerdo (Vazio ou seu Desktop) */}
      <div className="flex-1" />

      {/* Lado Direito (Interface do Jarvis) */}
      <div className="w-[400px] border-l border-white/10 bg-zinc-900/50 backdrop-blur-xl flex flex-col items-center justify-between p-8 relative">
        <div className="text-center">
          <h1 className="text-white tracking-widest uppercase text-sm opacity-50">Jarvis Systems</h1>
          <p className="text-cyan-400 font-mono text-xs mt-2 uppercase">{state}</p>
        </div>

        {/* Orbe de Partículas */}
        <div className="w-full h-[400px]">
          <Canvas camera={{ position: [0, 0, 15] }}>
            <color attach="background" args={['#000000']} />
            <ambientLight intensity={0.5} />
            <JarvisOrb state={state} />
          </Canvas>
        </div>

        {/* Legendas/Texto de resposta */}
        <div className="w-full min-h-[100px] text-center">
          <p className="text-white/80 font-light text-lg transition-all duration-500">
            {state === 'idle' ? 'Aguardando comando...' : text}
          </p>
        </div>
      </div>
    </main>
  );
}