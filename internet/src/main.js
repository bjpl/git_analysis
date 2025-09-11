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
    
    // Statistics
    this.stats = {
      cables: 0,
      datacenters: 0,
      bgpRoutes: 0,
      attacks: 0,
      fps: 60,
      objects: 0,
      particles: 0
    };
    
    // Animation states
    this.animationId = null;
    this.attackRipples = [];
    
    this.init();
  }
  
  async init() {
    this.createGlobe();
    this.setupEventListeners();
    
    // Load initial data
    await this.loadData();
    
    // Hide loading screen after data loads
    setTimeout(() => {
      document.getElementById('loading-screen').classList.add('hidden');
      this.animate();
    }, 2000);
  }
  
  createGlobe() {
    // Initialize Globe.gl
    this.globe = Globe()
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
      .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
      .showAtmosphere(true)
      .atmosphereColor('#00ffcc')
      .atmosphereAltitude(0.15);
    
    // Mount to container
    this.globe(this.container);
    
    // Access Three.js scene for custom effects
    const scene = this.globe.scene();
    const camera = this.globe.camera();
    const renderer = this.globe.renderer();
    
    // Configure renderer
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    
    // Add custom lighting
    this.setupLights(scene);
    
    // Add star field
    this.createStarField(scene);
    
    // Set initial camera position
    this.globe.pointOfView({ lat: 20, lng: 0, altitude: 2.5 });
  }
  
  createStarField(scene) {
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.7,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });
    
    const starsVertices = [];
    for (let i = 0; i < 10000; i++) {
      const x = (Math.random() - 0.5) * 2000;
      const y = (Math.random() - 0.5) * 2000;
      const z = -Math.random() * 2000;
      starsVertices.push(x, y, z);
    }
    
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starField = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starField);
  }
  
  setupLights(scene) {
    // Remove default lights first
    scene.traverse((child) => {
      if (child.type === 'DirectionalLight' || child.type === 'AmbientLight') {
        scene.remove(child);
      }
    });
    
    // Add custom lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);
    
    // Point lights for glow effects
    const pointLight1 = new THREE.PointLight(0x00ffcc, 0.5, 500);
    pointLight1.position.set(200, 100, 50);
    scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0xff00ff, 0.3, 500);
    pointLight2.position.set(-200, -100, 50);
    scene.add(pointLight2);
  }
  
  async loadData() {
    try {
      const loadingStatus = document.querySelector('.loading-status');
      
      // Load submarine cables
      loadingStatus.textContent = 'Loading submarine cable data...';
      const cablesData = await this.dataManager.loadSubmarineCables();
      this.visualizeSubmarineCables(cablesData);
      this.stats.cables = cablesData.length;
      
      // Load data centers
      loadingStatus.textContent = 'Mapping global data centers...';
      const datacentersData = await this.dataManager.loadDataCenters();
      this.visualizeDataCenters(datacentersData);
      this.stats.datacenters = datacentersData.length;
      
      // Load BGP routes
      loadingStatus.textContent = 'Initializing BGP route visualization...';
      const bgpData = await this.dataManager.loadBGPRoutes();
      this.visualizeBGPRoutes(bgpData);
      this.stats.bgpRoutes = bgpData.activeRoutes;
      
      // Initialize DDoS monitoring
      loadingStatus.textContent = 'Connecting to threat intelligence feeds...';
      this.initializeDDoSMonitoring();
      
      // Update UI stats
      this.updateStats();
      
    } catch (error) {
      console.error('Error loading data:', error);
      this.showDataError(error);
    }
  }
  
  visualizeSubmarineCables(cablesData) {
    // Format data for Globe.gl arcs
    const cableArcs = cablesData.map(cable => ({
      startLat: cable.landing_point_1.latitude,
      startLng: cable.landing_point_1.longitude,
      endLat: cable.landing_point_2.latitude,
      endLng: cable.landing_point_2.longitude,
      color: cable.status === 'active' ? '#00ffcc' : '#ffcc00',
      stroke: cable.capacity_tbps > 100 ? 3 : 2,
      label: cable.name,
      owner: cable.owner,
      capacity: cable.capacity_tbps,
      accuracy: cable.data_accuracy || 'estimated',
      status: cable.status
    }));
    
    // Apply arcs to globe with animation
    this.globe
      .arcsData(cableArcs)
      .arcColor('color')
      .arcStroke('stroke')
      .arcDashLength(0.5)
      .arcDashGap(0.2)
      .arcDashAnimateTime(2000)
      .arcAltitudeAutoScale(0.3)
      .arcsTransitionDuration(1000)
      .arcLabel(d => `
        <div style="font-family: 'Inter', sans-serif; padding: 8px;">
          <div style="color: #00ffcc; font-weight: bold;">${d.label || 'Submarine Cable'}</div>
          <div style="color: #fff; font-size: 12px;">
            <div>Owner: ${d.owner || 'Consortium'}</div>
            <div>Capacity: ${d.capacity || 'N/A'} Tbps</div>
            <div>Status: ${d.status || 'Active'}</div>
            <div style="color: ${d.accuracy === 'live' ? '#00ff00' : '#ffcc00'};">
              Accuracy: ${d.accuracy}
            </div>
          </div>
        </div>
      `);
  }
  
  visualizeDataCenters(datacenters) {
    // Format data for Globe.gl points
    const datacenterPoints = datacenters.map(dc => ({
      lat: dc.latitude,
      lng: dc.longitude,
      size: dc.tier === 1 ? 0.8 : dc.tier === 2 ? 0.5 : 0.3,
      color: dc.tier === 1 ? '#ff00ff' : dc.tier === 2 ? '#00ffcc' : '#ffcc00',
      label: dc.name,
      city: dc.city,
      country: dc.country,
      tier: dc.tier,
      accuracy: dc.data_accuracy || 'estimated',
      provider: dc.provider
    }));
    
    // Apply points to globe
    this.globe
      .pointsData(datacenterPoints)
      .pointLat('lat')
      .pointLng('lng')
      .pointColor('color')
      .pointAltitude(0.01)
      .pointRadius('size')
      .pointLabel(d => `
        <div style="font-family: 'Inter', sans-serif; padding: 8px;">
          <div style="color: ${d.color}; font-weight: bold;">${d.label || 'Data Center'}</div>
          <div style="color: #fff; font-size: 12px;">
            <div>Location: ${d.city}, ${d.country}</div>
            <div>Tier: ${d.tier}</div>
            <div>Provider: ${d.provider || 'Unknown'}</div>
            <div style="color: ${d.accuracy === 'live' ? '#00ff00' : '#ffcc00'};">
              Accuracy: ${d.accuracy}
            </div>
          </div>
        </div>
      `);
    
    // Add pulsing animation for Tier 1 data centers
    this.animateDataCenters(datacenterPoints.filter(dc => dc.tier === 1));
  }
  
  animateDataCenters(tier1Centers) {
    const scene = this.globe.scene();
    
    tier1Centers.forEach(dc => {
      const ringGeometry = new THREE.RingGeometry(0.5, 2, 32);
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(dc.color),
        transparent: true,
        opacity: 0.6,
        side: THREE.DoubleSide
      });
      
      const ring = new THREE.Mesh(ringGeometry, ringMaterial);
      
      // Convert lat/lng to 3D position
      const coords = this.globe.getCoords(dc.lat, dc.lng, 0.1);
      if (coords) {
        ring.position.set(coords.x, coords.y, coords.z);
        ring.lookAt(0, 0, 0);
        scene.add(ring);
        
        // Animate pulse
        gsap.to(ring.scale, {
          x: 2,
          y: 2,
          duration: 2,
          repeat: -1,
          ease: "power2.inOut"
        });
        
        gsap.to(ringMaterial, {
          opacity: 0,
          duration: 2,
          repeat: -1,
          ease: "power2.inOut"
        });
      }
    });
  }
  
  visualizeBGPRoutes(bgpData) {
    // For now, visualize BGP routes as additional arcs with different styling
    const routes = bgpData.routes.map(route => ({
      startLat: route.source.lat,
      startLng: route.source.lng,
      endLat: route.destination.lat,
      endLng: route.destination.lng,
      color: this.getTrafficColor(route.traffic_gbps),
      stroke: Math.min(route.traffic_gbps / 30, 3),
      label: `BGP: ${route.source.name} → ${route.destination.name}`,
      traffic: route.traffic_gbps,
      asn: route.asn
    }));
    
    // Store BGP routes separately for toggling
    this.bgpRoutes = routes;
  }
  
  getTrafficColor(gbps) {
    if (gbps > 100) return '#ff0000';
    if (gbps > 50) return '#ff6600';
    if (gbps > 20) return '#ffcc00';
    return '#00ff00';
  }
  
  initializeDDoSMonitoring() {
    // Simulate DDoS attacks
    setInterval(() => {
      if (Math.random() > 0.7) {
        const attack = this.dataManager.generateDDoSAttack();
        this.visualizeDDoSAttack(attack);
        this.stats.attacks++;
        this.updateStats();
      }
    }, 3000);
  }
  
  visualizeDDoSAttack(attack) {
    const scene = this.globe.scene();
    
    // Create ripple effect
    const geometry = new THREE.RingGeometry(0.1, 5, 64);
    const material = new THREE.MeshBasicMaterial({
      color: '#ff0000',
      transparent: true,
      opacity: 0.8,
      side: THREE.DoubleSide
    });
    
    const ripple = new THREE.Mesh(geometry, material);
    
    // Position at attack target
    const coords = this.globe.getCoords(attack.target.lat, attack.target.lng, 0.2);
    if (coords) {
      ripple.position.set(coords.x, coords.y, coords.z);
      ripple.lookAt(0, 0, 0);
      scene.add(ripple);
      
      // Animate ripple expansion
      gsap.to(ripple.scale, {
        x: attack.magnitude / 20,
        y: attack.magnitude / 20,
        z: 1,
        duration: 2,
        ease: 'power2.out',
        onComplete: () => {
          scene.remove(ripple);
          this.stats.attacks--;
          this.updateStats();
        }
      });
      
      gsap.to(material, {
        opacity: 0,
        duration: 2,
        ease: 'power2.out'
      });
      
      // Add to tracking array
      this.attackRipples.push(ripple);
    }
  }
  
  updateStats() {
    document.getElementById('cable-count').textContent = this.stats.cables.toLocaleString();
    document.getElementById('datacenter-count').textContent = this.stats.datacenters.toLocaleString();
    document.getElementById('bgp-routes').textContent = this.stats.bgpRoutes.toLocaleString();
    document.getElementById('attack-count').textContent = this.stats.attacks;
    document.getElementById('fps').textContent = Math.round(this.stats.fps);
    
    const scene = this.globe.scene();
    document.getElementById('object-count').textContent = scene.children.length;
    document.getElementById('particle-count').textContent = this.stats.particles;
  }
  
  setupEventListeners() {
    // Window resize
    window.addEventListener('resize', () => this.onWindowResize());
    
    // Layer toggles
    document.getElementById('toggle-cables').addEventListener('change', (e) => {
      this.globe.arcsData(e.target.checked ? this.globe.arcsData() : []);
    });
    
    document.getElementById('toggle-datacenters').addEventListener('change', (e) => {
      this.globe.pointsData(e.target.checked ? this.globe.pointsData() : []);
    });
    
    document.getElementById('toggle-bgp').addEventListener('change', (e) => {
      // Toggle BGP visualization (handled differently since we don't have pathsData)
      this.showBGPRoutes = e.target.checked;
    });
    
    document.getElementById('toggle-attacks').addEventListener('change', (e) => {
      if (!e.target.checked) {
        // Clear all attack ripples
        const scene = this.globe.scene();
        this.attackRipples.forEach(ripple => scene.remove(ripple));
        this.attackRipples = [];
      }
    });
    
    // Visual settings
    document.getElementById('toggle-atmosphere').addEventListener('change', (e) => {
      this.globe.showAtmosphere(e.target.checked);
    });
    
    document.getElementById('cable-glow').addEventListener('input', (e) => {
      // Update cable opacity
      const opacity = e.target.value / 100;
      this.globe.arcStroke(d => d.stroke * opacity);
    });
    
    document.getElementById('flow-speed').addEventListener('input', (e) => {
      const speed = e.target.value * 200;
      this.globe.arcDashAnimateTime(speed);
      this.globe.pathDashAnimateTime(speed);
    });
    
    // Data center filter
    document.getElementById('datacenter-filter').addEventListener('change', (e) => {
      const filter = e.target.value;
      const allData = this.globe.pointsData();
      
      if (filter === 'all') {
        this.globe.pointsData(allData);
      } else {
        const tierNum = parseInt(filter.replace('tier', ''));
        this.globe.pointsData(allData.filter(d => d.tier === tierNum));
      }
    });
  }
  
  showDataError(error) {
    console.error('Data loading error:', error);
    const panel = document.getElementById('info-panel');
    const content = document.getElementById('info-content');
    
    panel.classList.remove('hidden');
    content.innerHTML = `
      <div style="color: #ff3366;">
        Some data sources are currently unavailable. 
        Showing cached/estimated data where possible.
        <br><br>
        Error: ${error.message}
      </div>
    `;
  }
  
  onWindowResize() {
    this.globe.width(window.innerWidth);
    this.globe.height(window.innerHeight);
  }
  
  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());
    
    // Calculate FPS
    const now = performance.now();
    if (this.lastTime) {
      const delta = now - this.lastTime;
      this.stats.fps = 1000 / delta;
    }
    this.lastTime = now;
    
    // Update stats periodically
    if (Math.floor(now / 1000) !== Math.floor((now - 16) / 1000)) {
      this.updateStats();
    }
  }
  
  destroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    // Clean up Globe.gl
    this.globe._destructor();
  }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  const app = new InternetInfrastructureMap();
  
  // Close info panel
  document.querySelector('.info-close').addEventListener('click', () => {
    document.getElementById('info-panel').classList.add('hidden');
  });
  
  // Panel toggle
  document.getElementById('panel-toggle').addEventListener('click', () => {
    const controls = document.querySelector('.controls');
    controls.style.display = controls.style.display === 'none' ? 'block' : 'none';
  });
});

export default InternetInfrastructureMap;