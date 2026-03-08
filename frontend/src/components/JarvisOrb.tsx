import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function JarvisOrb({ state }: { state: string }) {
  const points = useRef<THREE.Points>(null!);
  const count = 18000;
  const radius = 5;

  const { spherePositions, waveBasePositions } = useMemo(() => {
    const spherePos = new Float32Array(count * 3);
    const waveBase = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      const phi = Math.acos(-1 + (2 * i) / count);
      const theta = Math.sqrt(count * Math.PI) * phi;

      spherePos[i3] = radius * Math.cos(theta) * Math.sin(phi);
      spherePos[i3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
      spherePos[i3 + 2] = radius * Math.cos(phi);

      const xPos = ((i / count) * 2 - 1) * radius * 2.5;
      waveBase[i3] = xPos;
      waveBase[i3 + 1] = 0; 
      waveBase[i3 + 2] = Math.sin(i * 0.5) * 0.5;
    }
    return { spherePositions: spherePos, waveBasePositions: waveBase };
  }, [count]);

  const positions = useMemo(() => new Float32Array(count * 3), [count]);

  useFrame((stateContext) => {
    const time = stateContext.clock.getElapsedTime();
    const posAttr = points.current.geometry.attributes.position;
    
    let morphSpeed = 0.08;
    let targetPositions = spherePositions;

    if (state === 'speaking') {
      targetPositions = waveBasePositions;
      morphSpeed = 0.12; 
    } else if (state === 'listening') {
      morphSpeed = 0.15;
    } else if (state === 'thinking') {
      morphSpeed = 0.1;
    }

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      let tx = targetPositions[i3];
      let ty = targetPositions[i3 + 1];
      let tz = targetPositions[i3 + 2];

      if (state === 'speaking') {
        const x = tx;
        const freq1 = Math.sin(x * 1.2 + time * 8) * 1.5;
        const freq2 = Math.cos(x * 2.5 + time * 12) * 0.6;
        const noise = Math.sin(x * 5 + time * 20) * 0.2;
        const edgeSoftener = Math.cos((x / (radius * 2.5)) * (Math.PI / 2));
        
        ty = (freq1 + freq2 + noise) * edgeSoftener;
        tz = Math.sin(x * 0.8 + time * 5) * 1.0 * edgeSoftener;
      } else {
        const pulse = 1 + Math.sin(time * 2 + (i / count) * 5) * 0.02;
        tx *= pulse;
        ty *= pulse;
        tz *= pulse;

        if (state === 'thinking') {
          ty += Math.sin(time * 20 + i) * 0.15;
        }
      }

      // Interpolação para movimento fluido
      posAttr.array[i3] += (tx - posAttr.array[i3]) * morphSpeed;
      posAttr.array[i3 + 1] += (ty - posAttr.array[i3 + 1]) * morphSpeed;
      posAttr.array[i3 + 2] += (tz - posAttr.array[i3 + 2]) * morphSpeed;
    }

    posAttr.needsUpdate = true;
    
    // Rotação da Esfera
    points.current.rotation.y += state === 'thinking' ? 0.04 : 0.005;
    if (state === 'speaking') {
        points.current.rotation.y *= 0.9; 
    }
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.012}
        color={
          state === 'listening' ? '#00e5ff' : 
          state === 'thinking' ? '#ff00ff' : 
          state === 'speaking' ? '#ffffff' : '#444444'
        }
        transparent
        opacity={0.7}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}