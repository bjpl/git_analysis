import * as THREE from 'three';
import gsap from 'gsap';

export class VisualizationEffects {
  constructor() {
    this.particleSystems = [];
    this.glowMaterials = [];
    this.trafficParticles = null;
    this.flowSpeed = 5;
    this.glowIntensity = 0.7;
    this.activeEffects = new Map();
  }
  
  addCableGlow(globe, cables) {
    // Create glowing effect for submarine cables
    cables.forEach(cable => {
      const material = new THREE.ShaderMaterial({
        uniforms: {
          time: { value: 0 },
          glowIntensity: { value: this.glowIntensity },
          color: { value: new THREE.Color(cable.color || '#00ffcc') }
        },
        vertexShader: `
          varying vec3 vNormal;
          varying vec3 vPosition;
          
          void main() {
            vNormal = normalize(normalMatrix * normal);
            vPosition = position;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          uniform float time;
          uniform float glowIntensity;
          uniform vec3 color;
          
          varying vec3 vNormal;
          varying vec3 vPosition;
          
          void main() {
            float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
            vec3 glow = color * intensity * glowIntensity;
            
            // Animated pulse
            float pulse = sin(time * 2.0 + vPosition.x * 0.1) * 0.5 + 0.5;
            glow *= (0.8 + pulse * 0.4);
            
            gl_FragColor = vec4(glow, intensity * 0.8);
          }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide
      });
      
      this.glowMaterials.push(material);
    });
  }
  
  addDataCenterPulse(globe, datacenters) {
    // Create pulsing rings around data centers
    datacenters.forEach(dc => {
      if (dc.tier === 1) {
        const pulseGeometry = new THREE.RingGeometry(0.5, 2, 32);
        const pulseMaterial = new THREE.MeshBasicMaterial({
          color: new THREE.Color(dc.color),
          transparent: true,
          opacity: 0.6,
          side: THREE.DoubleSide
        });
        
        const pulseMesh = new THREE.Mesh(pulseGeometry, pulseMaterial);
        
        // Position on globe surface
        const coords = this.latLngToVector3(dc.lat, dc.lng, 101);
        pulseMesh.position.copy(coords);
        pulseMesh.lookAt(new THREE.Vector3(0, 0, 0));
        
        // Animate pulse
        gsap.to(pulseMesh.scale, {
          x: 2,
          y: 2,
          duration: 2,
          repeat: -1,
          ease: "power2.inOut"
        });
        
        gsap.to(pulseMaterial, {
          opacity: 0,
          duration: 2,
          repeat: -1,
          ease: "power2.inOut"
        });
        
        this.activeEffects.set(`dc-pulse-${dc.name}`, pulseMesh);
      }
    });
  }
  
  createTrafficParticles(scene, globe, routes) {
    // Create particle system for BGP traffic flow
    const particleCount = 10000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const velocities = new Float32Array(particleCount * 3);
    const routes_data = new Float32Array(particleCount * 6); // start and end positions
    
    // Initialize particles along routes
    let particleIndex = 0;
    routes.forEach((route, routeIndex) => {
      const particlesPerRoute = Math.floor(particleCount / routes.length);
      
      for (let i = 0; i < particlesPerRoute && particleIndex < particleCount; i++) {
        const t = i / particlesPerRoute;
        
        // Start position
        const start = this.latLngToVector3(route.startLat, route.startLng, 101);
        const end = this.latLngToVector3(route.endLat, route.endLng, 101);
        
        // Interpolate position along arc
        const pos = new THREE.Vector3().lerpVectors(start, end, t);
        
        // Add some height for arc effect
        const arcHeight = 10 + route.value / 10;
        const arcT = Math.sin(t * Math.PI);
        pos.multiplyScalar(1 + arcT * arcHeight / 100);
        
        positions[particleIndex * 3] = pos.x;
        positions[particleIndex * 3 + 1] = pos.y;
        positions[particleIndex * 3 + 2] = pos.z;
        
        // Color based on traffic volume
        const color = new THREE.Color(route.color);
        colors[particleIndex * 3] = color.r;
        colors[particleIndex * 3 + 1] = color.g;
        colors[particleIndex * 3 + 2] = color.b;
        
        // Size based on traffic
        sizes[particleIndex] = Math.min(route.value / 50, 3);
        
        // Store route data for animation
        routes_data[particleIndex * 6] = start.x;
        routes_data[particleIndex * 6 + 1] = start.y;
        routes_data[particleIndex * 6 + 2] = start.z;
        routes_data[particleIndex * 6 + 3] = end.x;
        routes_data[particleIndex * 6 + 4] = end.y;
        routes_data[particleIndex * 6 + 5] = end.z;
        
        // Random velocity along route
        velocities[particleIndex * 3] = (Math.random() - 0.5) * 0.1;
        velocities[particleIndex * 3 + 1] = (Math.random() - 0.5) * 0.1;
        velocities[particleIndex * 3 + 2] = (Math.random() - 0.5) * 0.1;
        
        particleIndex++;
      }
    });
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geometry.setAttribute('route', new THREE.BufferAttribute(routes_data, 6));
    
    // Custom shader material for particles
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        flowSpeed: { value: this.flowSpeed },
        pixelRatio: { value: window.devicePixelRatio }
      },
      vertexShader: `
        attribute vec3 velocity;
        attribute vec3 color;
        attribute float size;
        attribute vec6 route;
        
        varying vec3 vColor;
        varying float vOpacity;
        
        uniform float time;
        uniform float flowSpeed;
        uniform float pixelRatio;
        
        void main() {
          vColor = color;
          
          // Animate along route
          float t = mod(time * flowSpeed * 0.1 + position.x * 0.01, 1.0);
          
          // Calculate position along arc
          vec3 start = route.xyz;
          vec3 end = route.zyx;
          vec3 pos = mix(start, end, t);
          
          // Add arc height
          float arcHeight = 15.0;
          float arcT = sin(t * 3.14159);
          pos *= 1.0 + arcT * arcHeight / 100.0;
          
          // Fade in/out at ends
          vOpacity = sin(t * 3.14159);
          
          vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
          gl_Position = projectionMatrix * mvPosition;
          gl_PointSize = size * pixelRatio * (300.0 / -mvPosition.z);
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        varying float vOpacity;
        
        void main() {
          // Circular particle shape
          vec2 center = gl_PointCoord - vec2(0.5);
          float dist = length(center);
          
          if (dist > 0.5) discard;
          
          // Soft edges
          float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
          alpha *= vOpacity;
          
          // Glow effect
          vec3 glow = vColor * (1.0 + (1.0 - dist) * 2.0);
          
          gl_FragColor = vec4(glow, alpha * 0.8);
        }
      `,
      vertexColors: true,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    
    this.trafficParticles = new THREE.Points(geometry, material);
    scene.add(this.trafficParticles);
    this.particleSystems.push(this.trafficParticles);
  }
  
  createAttackRipple(lat, lng, magnitude) {
    // Create expanding ripple effect for DDoS attacks
    const position = this.latLngToVector3(lat, lng, 102);
    
    const geometry = new THREE.RingGeometry(0.1, 5, 64);
    const material = new THREE.MeshBasicMaterial({
      color: '#ff0000',
      transparent: true,
      opacity: 0.8,
      side: THREE.DoubleSide
    });
    
    const ripple = new THREE.Mesh(geometry, material);
    ripple.position.copy(position);
    ripple.lookAt(new THREE.Vector3(0, 0, 0));
    
    // Create multiple ripples for dramatic effect
    const rippleGroup = new THREE.Group();
    rippleGroup.add(ripple);
    
    // Add secondary ripple
    const ripple2 = ripple.clone();
    ripple2.material = material.clone();
    ripple2.material.color = new THREE.Color('#ff6600');
    ripple2.material.opacity = 0.5;
    rippleGroup.add(ripple2);
    
    // Add glow sphere at center
    const glowGeometry = new THREE.SphereGeometry(magnitude / 20, 16, 16);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: '#ff0000',
      transparent: true,
      opacity: 0.9,
      emissive: '#ff0000',
      emissiveIntensity: 2
    });
    
    const glowSphere = new THREE.Mesh(glowGeometry, glowMaterial);
    glowSphere.position.copy(position);
    rippleGroup.add(glowSphere);
    
    // Animate glow sphere
    gsap.to(glowSphere.scale, {
      x: 2,
      y: 2,
      z: 2,
      duration: 0.5,
      repeat: 3,
      yoyo: true,
      ease: "power2.inOut"
    });
    
    return rippleGroup;
  }
  
  updateCableGlow(intensity) {
    this.glowIntensity = intensity;
    this.glowMaterials.forEach(material => {
      if (material.uniforms && material.uniforms.glowIntensity) {
        material.uniforms.glowIntensity.value = intensity;
      }
    });
  }
  
  updateFlowSpeed(speed) {
    this.flowSpeed = speed;
    if (this.trafficParticles && this.trafficParticles.material.uniforms) {
      this.trafficParticles.material.uniforms.flowSpeed.value = speed;
    }
  }
  
  toggleTrafficParticles(enabled) {
    if (this.trafficParticles) {
      this.trafficParticles.visible = enabled;
    }
  }
  
  latLngToVector3(lat, lng, radius = 100) {
    // Convert lat/lng to 3D position on sphere
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    
    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const y = radius * Math.cos(phi);
    const z = radius * Math.sin(phi) * Math.sin(theta);
    
    return new THREE.Vector3(x, y, z);
  }
  
  update(delta, elapsed) {
    // Update all shader uniforms
    this.glowMaterials.forEach(material => {
      if (material.uniforms && material.uniforms.time) {
        material.uniforms.time.value = elapsed;
      }
    });
    
    // Update particle system
    if (this.trafficParticles && this.trafficParticles.material.uniforms) {
      this.trafficParticles.material.uniforms.time.value = elapsed;
      
      // Rotate particles slightly for movement effect
      this.trafficParticles.rotation.y += delta * 0.01;
    }
    
    // Update any active effects
    this.activeEffects.forEach((effect, key) => {
      if (effect.update) {
        effect.update(delta, elapsed);
      }
    });
  }
  
  dispose() {
    // Clean up resources
    this.particleSystems.forEach(system => {
      if (system.geometry) system.geometry.dispose();
      if (system.material) system.material.dispose();
    });
    
    this.glowMaterials.forEach(material => {
      material.dispose();
    });
    
    this.activeEffects.clear();
  }
}