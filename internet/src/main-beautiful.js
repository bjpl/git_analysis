import Globe from 'globe.gl';
import * as THREE from 'three';
import * as d3 from 'd3';
import gsap from 'gsap';
import { DataManager } from './dataManager.js';

class InternetInfrastructureMap {
  constructor() {
    this.container = document.getElementById('globe-container');
    this.globe = null;
    this.dataManager = new DataManager();
    
    // Cable categories for visual differentiation
    this.cableCategories = {
      transatlantic: { color: '#00ffcc', glow: '#00ffcc', intensity: 1.0 },
      transpacific: { color: '#ff00ff', glow: '#ff00ff', intensity: 0.9 },
      regional: { color: '#ffcc00', glow: '#ffcc00', intensity: 0.7 },
      domestic: { color: '#00ccff', glow: '#00ccff', intensity: 0.5 }
    };
    
    // Statistics
    this.stats = {
      cables: 0,
      datacenters: 0,
      bgpRoutes: 0,
      attacks: 0,
      fps: 60
    };
    
    // Animation controls
    this.animations = {
      cableFlow: true,
      datacenterPulse: true,
      attacks: true
    };
    
    this.init();
  }
  
  async init() {
    try {
      await this.createGlobe();
      await this.loadData();
      this.setupEventListeners();
      this.startAnimations();
      setTimeout(() => this.hideLoadingScreen(), 1500);
    } catch (error) {
      console.error('Initialization error:', error);
      this.showError(error);
    }
  }
  
  async createGlobe() {
    return new Promise((resolve) => {
      this.globe = Globe()
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
        .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .showAtmosphere(true)
        .atmosphereColor('#ffffff')
        .atmosphereAltitude(0.25)
        .onGlobeReady(() => {
          this.setupScene();
          resolve();
        });
      
      this.globe(this.container);
      
      // Set initial camera position for best view
      this.globe.pointOfView({ lat: 30, lng: -30, altitude: 2.5 }, 0);
    });
  }
  
  setupScene() {
    const scene = this.globe.scene();
    const renderer = this.globe.renderer();
    
    // High quality rendering
    renderer.antialias = true;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    
    // Clear existing lights
    scene.traverse((child) => {
      if (child instanceof THREE.Light) {
        scene.remove(child);
      }
    });
    
    // Atmospheric lighting setup
    const ambientLight = new THREE.AmbientLight(0x222244, 0.4);
    scene.add(ambientLight);
    
    const sunLight = new THREE.DirectionalLight(0xffffff, 0.6);
    sunLight.position.set(100, 100, 100);
    scene.add(sunLight);
    
    // Accent lights for cable glow
    const cyanLight = new THREE.PointLight(0x00ffcc, 0.3, 1000);
    cyanLight.position.set(-200, 0, 100);
    scene.add(cyanLight);
    
    const magentaLight = new THREE.PointLight(0xff00ff, 0.3, 1000);
    magentaLight.position.set(200, 0, 100);
    scene.add(magentaLight);
    
    // Add subtle star field
    this.createStarField(scene);
  }
  
  createStarField(scene) {
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.5,
      transparent: true,
      opacity: 0.6,
      sizeAttenuation: true
    });
    
    const starsVertices = [];
    for (let i = 0; i < 5000; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 800 + Math.random() * 500;
      
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);
      
      starsVertices.push(x, y, z);
    }
    
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starField = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starField);
  }
  
  async loadData() {
    try {
      this.updateLoadingStatus('Loading submarine cables...');
      const cablesData = await this.dataManager.loadSubmarineCables();
      this.visualizeSubmarineCables(cablesData);
      
      this.updateLoadingStatus('Mapping data centers...');
      const datacentersData = await this.dataManager.loadDataCenters();
      this.visualizeDataCenters(datacentersData);
      
      this.updateLoadingStatus('Initializing network flows...');
      const bgpData = await this.dataManager.loadBGPRoutes();
      this.visualizeBGPRoutes(bgpData);
      
      this.updateStats();
    } catch (error) {
      console.error('Data loading error:', error);
    }
  }
  
  visualizeSubmarineCables(cablesData) {
    // Categorize and style cables
    const styledCables = cablesData.map(cable => {
      const category = this.categorizeCable(cable);
      const style = this.cableCategories[category];
      
      return {
        startLat: cable.landing_point_1.latitude,
        startLng: cable.landing_point_1.longitude,
        endLat: cable.landing_point_2.latitude,
        endLng: cable.landing_point_2.longitude,
        color: this.getCableGradient(style.color, cable.capacity_tbps),
        stroke: this.getCableStroke(cable.capacity_tbps),
        altitude: this.getCableAltitude(category),
        label: cable.name,
        owner: cable.owner,
        capacity: cable.capacity_tbps,
        category: category,
        accuracy: cable.data_accuracy || 'estimated',
        status: cable.status,
        dashLength: category === 'transatlantic' ? 0.9 : 0.5,
        dashGap: category === 'transatlantic' ? 0.1 : 0.3,
        dashAnimateTime: this.getDashAnimateTime(cable.capacity_tbps)
      };
    });
    
    // Sort by category for proper layering
    styledCables.sort((a, b) => {
      const order = ['domestic', 'regional', 'transpacific', 'transatlantic'];
      return order.indexOf(a.category) - order.indexOf(b.category);
    });
    
    this.globe
      .arcsData(styledCables)
      .arcColor(d => d.color)
      .arcStroke(d => d.stroke)
      .arcDashLength(d => d.dashLength)
      .arcDashGap(d => d.dashGap)
      .arcDashAnimateTime(d => d.dashAnimateTime)
      .arcAltitude(d => d.altitude)
      .arcsTransitionDuration(2000)
      .arcLabel(d => this.createCableTooltip(d));
    
    this.stats.cables = styledCables.length;
    
    // Add glow effect to major cables
    this.addCableGlowEffects(styledCables.filter(c => c.category === 'transatlantic' || c.category === 'transpacific'));
  }
  
  categorizeCable(cable) {
    const distance = this.calculateDistance(
      cable.landing_point_1.latitude,
      cable.landing_point_1.longitude,
      cable.landing_point_2.latitude,
      cable.landing_point_2.longitude
    );
    
    // Check if it crosses major oceans
    const isAtlantic = this.crossesAtlantic(cable);
    const isPacific = this.crossesPacific(cable);
    
    if (isAtlantic) return 'transatlantic';
    if (isPacific) return 'transpacific';
    if (distance > 3000) return 'regional';
    return 'domestic';
  }
  
  crossesAtlantic(cable) {
    const p1 = cable.landing_point_1;
    const p2 = cable.landing_point_2;
    
    // Simple check: one point in Americas, other in Europe/Africa
    const isAmericasPoint = (p) => p.longitude < -30 && p.longitude > -180;
    const isEuroAfricaPoint = (p) => p.longitude > -30 && p.longitude < 60;
    
    return (isAmericasPoint(p1) && isEuroAfricaPoint(p2)) || 
           (isAmericasPoint(p2) && isEuroAfricaPoint(p1));
  }
  
  crossesPacific(cable) {
    const p1 = cable.landing_point_1;
    const p2 = cable.landing_point_2;
    
    // Simple check: one point in Americas, other in Asia/Oceania
    const isAmericasPoint = (p) => p.longitude < -60 && p.longitude > -180;
    const isAsiaOceaniaPoint = (p) => p.longitude > 60 || p.longitude < -160;
    
    return (isAmericasPoint(p1) && isAsiaOceaniaPoint(p2)) || 
           (isAmericasPoint(p2) && isAsiaOceaniaPoint(p1));
  }
  
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
  
  getCableGradient(baseColor, capacity) {
    // Create gradient based on capacity
    if (capacity > 200) {
      return [baseColor, '#ffffff']; // Ultra high capacity - white highlight
    } else if (capacity > 100) {
      return [baseColor, baseColor]; // High capacity - solid bright
    } else if (capacity > 50) {
      return [d3.color(baseColor).darker(0.5).toString(), baseColor]; // Medium - gradient
    } else {
      return d3.color(baseColor).darker(1).toString(); // Low - darker
    }
  }
  
  getCableStroke(capacity) {
    if (capacity > 200) return 3;
    if (capacity > 100) return 2.5;
    if (capacity > 50) return 2;
    if (capacity > 20) return 1.5;
    return 1;
  }
  
  getCableAltitude(category) {
    switch(category) {
      case 'transatlantic': return 0.5;
      case 'transpacific': return 0.4;
      case 'regional': return 0.3;
      case 'domestic': return 0.2;
      default: return 0.15;
    }
  }
  
  getDashAnimateTime(capacity) {
    // Faster animation for higher capacity cables
    if (capacity > 100) return 1000;
    if (capacity > 50) return 1500;
    if (capacity > 20) return 2000;
    return 3000;
  }
  
  addCableGlowEffects(majorCables) {
    const scene = this.globe.scene();
    
    majorCables.forEach(cable => {
      // Create glowing particles along cable path
      const particleCount = 20;
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      const colors = new Float32Array(particleCount * 3);
      
      const color = new THREE.Color(this.cableCategories[cable.category].color);
      
      for (let i = 0; i < particleCount; i++) {
        const t = i / particleCount;
        const coords = this.interpolateArc(
          cable.startLat, cable.startLng,
          cable.endLat, cable.endLng,
          t, cable.altitude
        );
        
        positions[i * 3] = coords.x;
        positions[i * 3 + 1] = coords.y;
        positions[i * 3 + 2] = coords.z;
        
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
      }
      
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      
      const material = new THREE.PointsMaterial({
        size: 3,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
      });
      
      const particles = new THREE.Points(geometry, material);
      particles.name = `cable-glow-${cable.label}`;
      scene.add(particles);
      
      // Animate glow
      gsap.to(material, {
        opacity: 0.2,
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: "power2.inOut"
      });
    });
  }
  
  interpolateArc(startLat, startLng, endLat, endLng, t, altitude) {
    // Interpolate along great circle arc
    const startCoords = this.globe.getCoords(startLat, startLng, 0);
    const endCoords = this.globe.getCoords(endLat, endLng, 0);
    
    if (!startCoords || !endCoords) {
      return { x: 0, y: 0, z: 0 };
    }
    
    // Calculate arc height
    const arcHeight = 100 * altitude * Math.sin(t * Math.PI);
    
    // Linear interpolation with arc
    const x = startCoords.x + (endCoords.x - startCoords.x) * t;
    const y = startCoords.y + (endCoords.y - startCoords.y) * t + arcHeight;
    const z = startCoords.z + (endCoords.z - startCoords.z) * t;
    
    return { x, y, z };
  }
  
  createCableTooltip(cable) {
    const categoryColors = {
      transatlantic: '#00ffcc',
      transpacific: '#ff00ff',
      regional: '#ffcc00',
      domestic: '#00ccff'
    };
    
    const color = categoryColors[cable.category];
    const accuracyIcon = cable.accuracy === 'live' ? '🟢' : '🟡';
    
    return `
      <div style="
        font-family: 'Inter', sans-serif;
        padding: 15px;
        background: linear-gradient(135deg, rgba(10,10,20,0.98), rgba(20,20,40,0.98));
        border: 2px solid ${color};
        border-radius: 12px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        min-width: 250px;
      ">
        <div style="
          color: ${color};
          font-weight: bold;
          font-size: 16px;
          margin-bottom: 10px;
          text-shadow: 0 0 10px ${color};
        ">
          ${cable.label || 'Submarine Cable'}
        </div>
        <div style="
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
          padding: 8px;
          margin-bottom: 8px;
        ">
          <div style="color: #fff; font-size: 13px; line-height: 1.6;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #888;">Category:</span>
              <span style="color: ${color}; text-transform: uppercase; font-weight: 500;">
                ${cable.category}
              </span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #888;">Capacity:</span>
              <span style="color: #fff; font-weight: 500;">
                ${cable.capacity || 'N/A'} Tbps
              </span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #888;">Owner:</span>
              <span style="color: #fff; font-size: 11px;">
                ${(cable.owner || 'Consortium').substring(0, 25)}...
              </span>
            </div>
          </div>
        </div>
        <div style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 8px;
          border-top: 1px solid rgba(255,255,255,0.1);
        ">
          <span style="color: ${cable.status === 'active' ? '#00ff00' : '#ff9900'}; font-size: 11px;">
            ${cable.status?.toUpperCase() || 'ACTIVE'}
          </span>
          <span style="font-size: 11px; color: #888;">
            ${accuracyIcon} ${cable.accuracy}
          </span>
        </div>
      </div>
    `;
  }
  
  visualizeDataCenters(datacenters) {
    // Simple, clean visualization for data centers
    const points = datacenters.slice(0, 500).map(dc => ({
      lat: dc.latitude,
      lng: dc.longitude,
      size: dc.tier === 1 ? 0.4 : 0.2,
      color: dc.tier === 1 ? '#ff00ff' : dc.tier === 2 ? '#00ffcc' : '#ffffff',
      label: dc.name,
      city: dc.city,
      country: dc.country,
      tier: dc.tier
    }));
    
    this.globe
      .pointsData(points)
      .pointLat('lat')
      .pointLng('lng')
      .pointColor('color')
      .pointAltitude(0.01)
      .pointRadius('size')
      .pointLabel(d => `
        <div style="font-family: 'Inter', sans-serif; padding: 8px;">
          <strong>${d.label}</strong><br/>
          ${d.city}, ${d.country}<br/>
          Tier ${d.tier}
        </div>
      `);
    
    this.stats.datacenters = points.length;
  }
  
  visualizeBGPRoutes(bgpData) {
    this.stats.bgpRoutes = bgpData.activeRoutes;
    // Keep BGP visualization minimal to not clutter the cables
  }
  
  startAnimations() {
    // Smooth camera rotation
    const controls = this.globe.controls();
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.3;
    
    // Start DDoS monitoring
    this.initializeDDoSMonitoring();
    
    // Animation loop
    this.animate();
  }
  
  initializeDDoSMonitoring() {
    setInterval(() => {
      if (Math.random() > 0.8 && this.animations.attacks) {
        const attack = this.dataManager.generateDDoSAttack();
        this.visualizeDDoSAttack(attack);
      }
    }, 8000);
  }
  
  visualizeDDoSAttack(attack) {
    const scene = this.globe.scene();
    const coords = this.globe.getCoords(attack.target.lat, attack.target.lng, 0.1);
    
    if (!coords) return;
    
    // Create beautiful ripple effect
    const rippleGroup = new THREE.Group();
    
    for (let i = 0; i < 3; i++) {
      const geometry = new THREE.RingGeometry(0.5, 3 + i * 2, 64);
      const material = new THREE.MeshBasicMaterial({
        color: new THREE.Color('#ff0066'),
        transparent: true,
        opacity: 0.6 - i * 0.15,
        side: THREE.DoubleSide
      });
      
      const ring = new THREE.Mesh(geometry, material);
      ring.position.set(coords.x, coords.y, coords.z);
      ring.lookAt(0, 0, 0);
      rippleGroup.add(ring);
      
      gsap.to(ring.scale, {
        x: 3 + i,
        y: 3 + i,
        duration: 3,
        delay: i * 0.3,
        ease: "power2.out"
      });
      
      gsap.to(material, {
        opacity: 0,
        duration: 3,
        delay: i * 0.3,
        onComplete: () => {
          if (i === 2) scene.remove(rippleGroup);
        }
      });
    }
    
    scene.add(rippleGroup);
    this.stats.attacks++;
    setTimeout(() => this.stats.attacks--, 3000);
    this.updateStats();
  }
  
  updateLoadingStatus(message) {
    const status = document.querySelector('.loading-status');
    if (status) status.textContent = message;
  }
  
  hideLoadingScreen() {
    const screen = document.getElementById('loading-screen');
    if (screen) {
      gsap.to(screen, {
        opacity: 0,
        duration: 1,
        onComplete: () => {
          screen.style.display = 'none';
        }
      });
    }
  }
  
  showError(error) {
    console.error(error);
    const status = document.querySelector('.loading-status');
    if (status) {
      status.textContent = 'Error loading visualization. Please refresh.';
      status.style.color = '#ff3366';
    }
  }
  
  updateStats() {
    const updates = [
      ['cable-count', this.stats.cables],
      ['datacenter-count', this.stats.datacenters],
      ['bgp-routes', this.stats.bgpRoutes],
      ['attack-count', this.stats.attacks],
      ['fps', Math.round(this.stats.fps)]
    ];
    
    updates.forEach(([id, value]) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value.toLocaleString();
    });
  }
  
  setupEventListeners() {
    // Cable glow intensity
    document.getElementById('cable-glow')?.addEventListener('input', (e) => {
      const intensity = e.target.value / 100;
      this.globe.arcStroke(d => d.stroke * (0.5 + intensity * 0.5));
    });
    
    // Flow speed
    document.getElementById('flow-speed')?.addEventListener('input', (e) => {
      const speed = 5000 / e.target.value;
      this.globe.arcDashAnimateTime(speed);
    });
    
    // Layer toggles
    document.getElementById('toggle-cables')?.addEventListener('change', (e) => {
      const data = e.target.checked ? this.globe.arcsData() : [];
      this.globe.arcsData(data);
    });
    
    document.getElementById('toggle-datacenters')?.addEventListener('change', (e) => {
      const data = e.target.checked ? this.globe.pointsData() : [];
      this.globe.pointsData(data);
    });
    
    document.getElementById('toggle-attacks')?.addEventListener('change', (e) => {
      this.animations.attacks = e.target.checked;
    });
    
    document.getElementById('toggle-atmosphere')?.addEventListener('change', (e) => {
      this.globe.showAtmosphere(e.target.checked);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'r' || e.key === 'R') {
        this.globe.pointOfView({ lat: 30, lng: -30, altitude: 2.5 }, 1000);
      }
    });
    
    // Close buttons
    document.querySelector('.info-close')?.addEventListener('click', () => {
      document.getElementById('info-panel').classList.add('hidden');
    });
    
    // Window resize
    window.addEventListener('resize', () => {
      this.globe.width(window.innerWidth);
      this.globe.height(window.innerHeight);
    });
  }
  
  animate() {
    requestAnimationFrame(() => this.animate());
    
    // Update FPS
    const now = performance.now();
    if (this.lastTime) {
      const delta = now - this.lastTime;
      this.stats.fps = 1000 / delta;
    }
    this.lastTime = now;
    
    // Update stats every second
    if (Math.floor(now / 1000) !== Math.floor((now - 16) / 1000)) {
      this.updateStats();
    }
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new InternetInfrastructureMap();
});

export default InternetInfrastructureMap;