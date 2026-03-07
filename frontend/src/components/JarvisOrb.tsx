import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function JarvisOrb({ state }: { state: string }) {
  const points = useRef<THREE.Points>(null!);
  const count = 18000;
  const radius = 5;

  const { spherePositions, wavePositions } = useMemo(() => {
    const spherePos = new Float32Array(count * 3);
    const wavePos = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const phi = Math.acos(-1 + (2 * i) / count);
      const theta = Math.sqrt(count * Math.PI) * phi;

      spherePos[i3] = radius * Math.cos(theta) * Math.sin(phi);
      spherePos[i3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
      spherePos[i3 + 2] = radius * Math.cos(phi);

      wavePos[i3] = ((i / count) * 2 - 1) * radius * 3.5;
      wavePos[i3 + 1] = 0;
      wavePos[i3 + 2] = (Math.random() - 0.5) * 0.8;
    }
    return { spherePositions: spherePos, wavePositions: wavePos };
  }, [count]);

  const positions = useMemo(() => new Float32Array(count * 3), [count]);

  useFrame((stateContext) => {
    const time = stateContext.clock.getElapsedTime();
    const posAttr = points.current.geometry.attributes.position;
    
    let morphSpeed = 0.08;
    let targetPositions = spherePositions;
    
    if (state === 'listening') {
      morphSpeed = 0.15;
      targetPositions = spherePositions;
    } else if (state === 'thinking') {
      morphSpeed = 0.1;
      targetPositions = spherePositions;
    } else if (state === 'speaking') {
      morphSpeed = 0.12;
      targetPositions = wavePositions;
    }

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      let tx = targetPositions[i3];
      let ty = targetPositions[i3 + 1];
      let tz = targetPositions[i3 + 2];

      if (state === 'speaking' && targetPositions === wavePositions) {
        const x = tx;
        const envelope = Math.exp(-Math.pow(x / 4, 2));
        
        // Removi o volumeSim global. Agora a amplitude é baseada em fases defasadas
        // w1 e w2 nunca zeram ao mesmo tempo no mesmo X
        const w1 = Math.sin(x * 1.5 + time * 10) * 1.3;
        const w2 = Math.cos(x * 2.2 + time * 15) * 0.5;
        const w3 = Math.sin(x * 4.0 + time * 20) * 0.2;
        
        ty = (w1 + w2 + w3) * envelope;
        tz += Math.sin(x * 2 + time * 10) * 0.3 * envelope;
      } else {
        // Respiro da esfera sem corromper os dados de base
        const pulse = 1 + Math.sin(time * 2 + (i / count) * 5) * 0.02;
        tx *= pulse;
        ty *= pulse;
        tz *= pulse;

        if (state === 'thinking') {
          ty += Math.sin(time * 20 + i) * 0.15;
        }
      }

      posAttr.array[i3] += (tx - posAttr.array[i3]) * morphSpeed;
      posAttr.array[i3 + 1] += (ty - posAttr.array[i3 + 1]) * morphSpeed;
      posAttr.array[i3 + 2] += (tz - posAttr.array[i3 + 2]) * morphSpeed;
    }

    posAttr.needsUpdate = true;
    points.current.rotation.y += state === 'thinking' ? 0.04 : 0.005;
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.012}
        color={state === 'listening' ? '#00ffff' : state === 'thinking' ? '#ff00ff' : '#ffffff'}
        transparent
        opacity={0.7}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}