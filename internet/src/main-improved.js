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
    
    // Application state
    this.state = {
      loaded: false,
      error: null,
      dataLoaded: {
        cables: false,
        datacenters: false,
        bgp: false
      }
    };
    
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
    this.bgpRoutes = [];
    this.showBGPRoutes = true;
    
    // Performance tracking
    this.lastTime = 0;
    this.frameCount = 0;
    
    this.init().catch(this.handleInitError.bind(this));
  }
  
  async init() {
    try {
      // Update loading status
      this.updateLoadingStatus('Initializing 3D globe...');
      
      // Create globe with error handling
      await this.createGlobe();
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Load data with progress updates
      await this.loadData();
      
      // Start animation loop
      this.animate();
      
      // Hide loading screen with fade
      this.hideLoadingScreen();
      
      this.state.loaded = true;
      
    } catch (error) {
      this.handleInitError(error);
    }
  }
  
  async createGlobe() {
    return new Promise((resolve, reject) => {
      try {
        // Initialize Globe.gl with error handling
        this.globe = Globe()
          .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
          .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
          .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
          .showAtmosphere(true)
          .atmosphereColor('#00ffcc')
          .atmosphereAltitude(0.15)
          .enablePointerInteraction(true)
          .onGlobeReady(() => {
            // Globe is ready
            this.setupSceneEnhancements();
            resolve();
          });
        
        // Mount to container
        this.globe(this.container);
        
        // Set initial view
        this.globe.pointOfView({ lat: 20, lng: 0, altitude: 2.5 }, 1000);
        
      } catch (error) {
        reject(error);
      }
    });
  }
  
  setupSceneEnhancements() {
    const scene = this.globe.scene();
    const camera = this.globe.camera();
    const renderer = this.globe.renderer();
    
    // Configure renderer for better quality
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // Setup custom lighting
    this.setupLights(scene);
    
    // Add star field
    this.createStarField(scene);
    
    // Add grid helper for debugging (can be toggled)
    this.addGridHelper(scene);
  }
  
  createStarField(scene) {
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.7,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true
    });
    
    const starsVertices = [];
    for (let i = 0; i < 10000; i++) {
      const x = (Math.random() - 0.5) * 2000;
      const y = (Math.random() - 0.5) * 2000;
      const z = -Math.random() * 2000 - 100;
      starsVertices.push(x, y, z);
    }
    
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starField = new THREE.Points(starsGeometry, starsMaterial);
    starField.name = 'starField';
    scene.add(starField);
  }
  
  setupLights(scene) {
    // Remove existing lights
    scene.traverse((child) => {
      if (child instanceof THREE.Light) {
        scene.remove(child);
      }
    });
    
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    // Main directional light (sun)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(100, 100, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    
    // Accent lights for visual interest
    const pointLight1 = new THREE.PointLight(0x00ffcc, 0.5, 500);
    pointLight1.position.set(200, 100, 50);
    scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0xff00ff, 0.3, 500);
    pointLight2.position.set(-200, -100, 50);
    scene.add(pointLight2);
    
    // Hemisphere light for realistic ambient
    const hemisphereLight = new THREE.HemisphereLight(0x5555ff, 0x555555, 0.3);
    scene.add(hemisphereLight);
  }
  
  addGridHelper(scene) {
    const gridHelper = new THREE.GridHelper(200, 20, 0x00ffcc, 0x004444);
    gridHelper.position.y = -100;
    gridHelper.visible = false; // Hidden by default
    gridHelper.name = 'gridHelper';
    scene.add(gridHelper);
  }
  
  async loadData() {
    try {
      const totalSteps = 4;
      let currentStep = 0;
      
      // Load submarine cables
      this.updateLoadingStatus('Loading submarine cable data...', (++currentStep / totalSteps) * 100);
      const cablesData = await this.dataManager.loadSubmarineCables();
      this.visualizeSubmarineCables(cablesData);
      this.stats.cables = cablesData.length;
      this.state.dataLoaded.cables = true;
      
      // Load data centers
      this.updateLoadingStatus('Mapping global data centers...', (++currentStep / totalSteps) * 100);
      const datacentersData = await this.dataManager.loadDataCenters();
      this.visualizeDataCenters(datacentersData);
      this.stats.datacenters = datacentersData.length;
      this.state.dataLoaded.datacenters = true;
      
      // Load BGP routes
      this.updateLoadingStatus('Initializing BGP route visualization...', (++currentStep / totalSteps) * 100);
      const bgpData = await this.dataManager.loadBGPRoutes();
      this.visualizeBGPRoutes(bgpData);
      this.stats.bgpRoutes = bgpData.activeRoutes;
      this.state.dataLoaded.bgp = true;
      
      // Initialize DDoS monitoring
      this.updateLoadingStatus('Connecting to threat intelligence feeds...', (++currentStep / totalSteps) * 100);
      this.initializeDDoSMonitoring();
      
      // Update UI stats
      this.updateStats();
      
    } catch (error) {
      console.error('Error loading data:', error);
      this.showDataError(error);
      // Continue with partial data
    }
  }
  
  visualizeSubmarineCables(cablesData) {
    // Limit initial render for performance
    const maxCables = 100; // Start with 100, load more progressively
    const initialCables = cablesData.slice(0, maxCables);
    
    const cableArcs = initialCables.map(cable => ({
      startLat: cable.landing_point_1.latitude,
      startLng: cable.landing_point_1.longitude,
      endLat: cable.landing_point_2.latitude,
      endLng: cable.landing_point_2.longitude,
      color: cable.status === 'active' ? ['#00ffcc', '#00ffcc'] : ['#ffcc00', '#ffcc00'],
      stroke: cable.capacity_tbps > 100 ? 2 : 1,
      label: cable.name,
      owner: cable.owner,
      capacity: cable.capacity_tbps,
      accuracy: cable.data_accuracy || 'estimated',
      status: cable.status
    }));
    
    // Apply arcs with custom rendering
    this.globe
      .arcsData(cableArcs)
      .arcColor(d => d.color)
      .arcStroke('stroke')
      .arcDashLength(0.5)
      .arcDashGap(0.2)
      .arcDashAnimateTime(2000)
      .arcAltitudeAutoScale(0.3)
      .arcsTransitionDuration(1000)
      .arcLabel(d => this.createCableTooltip(d));
    
    // Load remaining cables progressively
    if (cablesData.length > maxCables) {
      setTimeout(() => {
        this.loadRemainingCables(cablesData.slice(maxCables));
      }, 2000);
    }
  }
  
  loadRemainingCables(remainingCables) {
    const currentArcs = this.globe.arcsData();
    const additionalArcs = remainingCables.map(cable => ({
      startLat: cable.landing_point_1.latitude,
      startLng: cable.landing_point_1.longitude,
      endLat: cable.landing_point_2.latitude,
      endLng: cable.landing_point_2.longitude,
      color: cable.status === 'active' ? ['#00ffcc', '#00ffcc'] : ['#ffcc00', '#ffcc00'],
      stroke: cable.capacity_tbps > 100 ? 2 : 1,
      label: cable.name,
      owner: cable.owner,
      capacity: cable.capacity_tbps,
      accuracy: cable.data_accuracy || 'estimated',
      status: cable.status
    }));
    
    // Batch update for performance
    const batchSize = 50;
    let index = 0;
    
    const loadBatch = () => {
      const batch = additionalArcs.slice(index, index + batchSize);
      if (batch.length > 0) {
        this.globe.arcsData([...currentArcs, ...batch]);
        index += batchSize;
        setTimeout(loadBatch, 500);
      }
    };
    
    loadBatch();
  }
  
  createCableTooltip(cable) {
    const accuracyColor = cable.accuracy === 'live' ? '#00ff00' : '#ffcc00';
    return `
      <div style="
        font-family: 'Inter', sans-serif;
        padding: 12px;
        background: rgba(10, 10, 15, 0.95);
        border: 1px solid #00ffcc;
        border-radius: 8px;
        backdrop-filter: blur(10px);
      ">
        <div style="color: #00ffcc; font-weight: bold; font-size: 14px; margin-bottom: 8px;">
          ${cable.label || 'Submarine Cable'}
        </div>
        <div style="color: #fff; font-size: 12px; line-height: 1.5;">
          <div><strong>Owner:</strong> ${cable.owner || 'Consortium'}</div>
          <div><strong>Capacity:</strong> ${cable.capacity || 'N/A'} Tbps</div>
          <div><strong>Status:</strong> <span style="color: ${cable.status === 'active' ? '#00ff00' : '#ffcc00'};">${cable.status || 'Active'}</span></div>
          <div style="margin-top: 4px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.1);">
            <span style="color: ${accuracyColor};">● ${cable.accuracy.toUpperCase()}</span>
          </div>
        </div>
      </div>
    `;
  }
  
  visualizeDataCenters(datacenters) {
    // Cluster nearby data centers for performance
    const clustered = this.clusterDataCenters(datacenters);
    
    const datacenterPoints = clustered.map(dc => ({
      lat: dc.latitude,
      lng: dc.longitude,
      size: dc.tier === 1 ? 0.6 : dc.tier === 2 ? 0.4 : 0.2,
      color: dc.tier === 1 ? '#ff00ff' : dc.tier === 2 ? '#00ffcc' : '#ffcc00',
      label: dc.name,
      city: dc.city,
      country: dc.country,
      tier: dc.tier,
      count: dc.count || 1,
      accuracy: dc.data_accuracy || 'estimated',
      provider: dc.provider
    }));
    
    this.globe
      .pointsData(datacenterPoints)
      .pointLat('lat')
      .pointLng('lng')
      .pointColor('color')
      .pointAltitude(0.01)
      .pointRadius('size')
      .pointLabel(d => this.createDataCenterTooltip(d));
    
    // Add pulsing animation for Tier 1 data centers
    this.animateDataCenters(datacenterPoints.filter(dc => dc.tier === 1));
  }
  
  clusterDataCenters(datacenters) {
    // Simple clustering for nearby data centers
    const threshold = 2; // degrees
    const clusters = [];
    const processed = new Set();
    
    datacenters.forEach((dc, index) => {
      if (processed.has(index)) return;
      
      const cluster = {
        ...dc,
        count: 1,
        centers: [dc]
      };
      
      // Find nearby centers
      datacenters.forEach((other, otherIndex) => {
        if (index !== otherIndex && !processed.has(otherIndex)) {
          const dist = Math.sqrt(
            Math.pow(dc.latitude - other.latitude, 2) + 
            Math.pow(dc.longitude - other.longitude, 2)
          );
          
          if (dist < threshold) {
            cluster.count++;
            cluster.centers.push(other);
            processed.add(otherIndex);
          }
        }
      });
      
      processed.add(index);
      clusters.push(cluster);
    });
    
    return clusters;
  }
  
  createDataCenterTooltip(dc) {
    const accuracyColor = dc.accuracy === 'live' ? '#00ff00' : '#ffcc00';
    const tierColors = { 1: '#ff00ff', 2: '#00ffcc', 3: '#ffcc00' };
    
    return `
      <div style="
        font-family: 'Inter', sans-serif;
        padding: 12px;
        background: rgba(10, 10, 15, 0.95);
        border: 1px solid ${tierColors[dc.tier]};
        border-radius: 8px;
        backdrop-filter: blur(10px);
      ">
        <div style="color: ${tierColors[dc.tier]}; font-weight: bold; font-size: 14px; margin-bottom: 8px;">
          ${dc.label || 'Data Center'}
          ${dc.count > 1 ? `<span style="font-size: 10px;"> (${dc.count} centers)</span>` : ''}
        </div>
        <div style="color: #fff; font-size: 12px; line-height: 1.5;">
          <div><strong>Location:</strong> ${dc.city}, ${dc.country}</div>
          <div><strong>Tier:</strong> Tier ${dc.tier}</div>
          <div><strong>Provider:</strong> ${dc.provider || 'Unknown'}</div>
          <div style="margin-top: 4px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.1);">
            <span style="color: ${accuracyColor};">● ${dc.accuracy.toUpperCase()}</span>
          </div>
        </div>
      </div>
    `;
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
      ring.name = `datacenter-ring-${dc.label}`;
      
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
    // Store routes for later use
    this.bgpRoutes = bgpData.routes.map(route => ({
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
    
    // Create particle effects for traffic (separate from globe arcs)
    this.createTrafficVisualization(this.bgpRoutes);
  }
  
  createTrafficVisualization(routes) {
    const scene = this.globe.scene();
    
    // Create particle system for each route
    routes.forEach(route => {
      const particleCount = Math.min(route.traffic / 10, 20);
      const particles = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      
      for (let i = 0; i < particleCount; i++) {
        const t = i / particleCount;
        const startCoords = this.globe.getCoords(route.startLat, route.startLng, 0.1);
        const endCoords = this.globe.getCoords(route.endLat, route.endLng, 0.1);
        
        if (startCoords && endCoords) {
          positions[i * 3] = startCoords.x + (endCoords.x - startCoords.x) * t;
          positions[i * 3 + 1] = startCoords.y + (endCoords.y - startCoords.y) * t;
          positions[i * 3 + 2] = startCoords.z + (endCoords.z - startCoords.z) * t;
        }
      }
      
      particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      
      const material = new THREE.PointsMaterial({
        color: new THREE.Color(route.color),
        size: 2,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
      });
      
      const particleSystem = new THREE.Points(particles, material);
      particleSystem.name = `bgp-traffic-${route.asn}`;
      scene.add(particleSystem);
      
      // Animate particles along route
      this.animateTrafficParticles(particleSystem, route);
    });
  }
  
  animateTrafficParticles(particleSystem, route) {
    // Create flowing animation
    gsap.to(particleSystem.rotation, {
      z: Math.PI * 2,
      duration: 10 / (route.traffic / 50),
      repeat: -1,
      ease: "none"
    });
  }
  
  getTrafficColor(gbps) {
    if (gbps > 100) return '#ff0000';
    if (gbps > 50) return '#ff6600';
    if (gbps > 20) return '#ffcc00';
    return '#00ff00';
  }
  
  initializeDDoSMonitoring() {
    // Simulate DDoS attacks with controlled frequency
    this.attackInterval = setInterval(() => {
      if (Math.random() > 0.7) {
        const attack = this.dataManager.generateDDoSAttack();
        this.visualizeDDoSAttack(attack);
        this.stats.attacks++;
        this.updateStats();
      }
    }, 5000);
  }
  
  visualizeDDoSAttack(attack) {
    const scene = this.globe.scene();
    
    // Create multi-layered ripple effect
    const rippleGroup = new THREE.Group();
    rippleGroup.name = `attack-${Date.now()}`;
    
    for (let i = 0; i < 3; i++) {
      const geometry = new THREE.RingGeometry(0.1 + i * 0.5, 3 + i * 2, 64);
      const material = new THREE.MeshBasicMaterial({
        color: i === 0 ? '#ff0000' : i === 1 ? '#ff6600' : '#ffcc00',
        transparent: true,
        opacity: 0.8 - i * 0.2,
        side: THREE.DoubleSide
      });
      
      const ripple = new THREE.Mesh(geometry, material);
      
      // Position at attack target
      const coords = this.globe.getCoords(attack.target.lat, attack.target.lng, 0.2 + i * 0.1);
      if (coords) {
        ripple.position.set(coords.x, coords.y, coords.z);
        ripple.lookAt(0, 0, 0);
        rippleGroup.add(ripple);
        
        // Staggered animation
        gsap.to(ripple.scale, {
          x: attack.magnitude / (20 - i * 5),
          y: attack.magnitude / (20 - i * 5),
          z: 1,
          duration: 3,
          delay: i * 0.2,
          ease: 'power2.out'
        });
        
        gsap.to(material, {
          opacity: 0,
          duration: 3,
          delay: i * 0.2,
          ease: 'power2.out'
        });
      }
    }
    
    scene.add(rippleGroup);
    this.attackRipples.push(rippleGroup);
    
    // Remove after animation
    setTimeout(() => {
      scene.remove(rippleGroup);
      this.attackRipples = this.attackRipples.filter(r => r !== rippleGroup);
      this.stats.attacks--;
      this.updateStats();
    }, 4000);
  }
  
  updateStats() {
    // Update with smooth transitions
    const elements = {
      'cable-count': this.stats.cables,
      'datacenter-count': this.stats.datacenters,
      'bgp-routes': this.stats.bgpRoutes,
      'attack-count': this.stats.attacks,
      'fps': Math.round(this.stats.fps)
    };
    
    Object.entries(elements).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) {
        const current = parseInt(element.textContent.replace(/,/g, '')) || 0;
        if (current !== value) {
          // Animate number change
          gsap.to({ value: current }, {
            value: value,
            duration: 0.5,
            onUpdate: function() {
              element.textContent = Math.round(this.targets()[0].value).toLocaleString();
            }
          });
        }
      }
    });
    
    // Update scene stats
    const scene = this.globe.scene();
    document.getElementById('object-count').textContent = scene.children.length;
    
    // Count particles
    let particleCount = 0;
    scene.traverse(child => {
      if (child instanceof THREE.Points) {
        particleCount += child.geometry.attributes.position.count;
      }
    });
    document.getElementById('particle-count').textContent = particleCount;
  }
  
  setupEventListeners() {
    // Window resize with debouncing
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => this.onWindowResize(), 250);
    });
    
    // Layer toggles
    this.setupLayerToggles();
    
    // Visual settings
    this.setupVisualControls();
    
    // Interactive elements
    this.setupInteractiveElements();
    
    // Keyboard shortcuts
    this.setupKeyboardShortcuts();
  }
  
  setupLayerToggles() {
    document.getElementById('toggle-cables')?.addEventListener('change', (e) => {
      const arcsData = this.globe.arcsData();
      if (e.target.checked && arcsData.length === 0) {
        // Restore cables
        this.loadData().then(() => {
          // Cables reloaded
        });
      } else {
        this.globe.arcsData(e.target.checked ? arcsData : []);
      }
    });
    
    document.getElementById('toggle-datacenters')?.addEventListener('change', (e) => {
      const pointsData = this.globe.pointsData();
      this.globe.pointsData(e.target.checked ? pointsData : []);
    });
    
    document.getElementById('toggle-bgp')?.addEventListener('change', (e) => {
      this.showBGPRoutes = e.target.checked;
      const scene = this.globe.scene();
      scene.traverse(child => {
        if (child.name && child.name.startsWith('bgp-traffic-')) {
          child.visible = e.target.checked;
        }
      });
    });
    
    document.getElementById('toggle-attacks')?.addEventListener('change', (e) => {
      if (!e.target.checked) {
        // Clear all attack ripples
        const scene = this.globe.scene();
        this.attackRipples.forEach(ripple => scene.remove(ripple));
        this.attackRipples = [];
        clearInterval(this.attackInterval);
      } else {
        this.initializeDDoSMonitoring();
      }
    });
  }
  
  setupVisualControls() {
    document.getElementById('toggle-atmosphere')?.addEventListener('change', (e) => {
      this.globe.showAtmosphere(e.target.checked);
    });
    
    document.getElementById('toggle-stars')?.addEventListener('change', (e) => {
      const scene = this.globe.scene();
      const starField = scene.getObjectByName('starField');
      if (starField) starField.visible = e.target.checked;
    });
    
    document.getElementById('toggle-grid')?.addEventListener('change', (e) => {
      const scene = this.globe.scene();
      const grid = scene.getObjectByName('gridHelper');
      if (grid) grid.visible = e.target.checked;
    });
    
    document.getElementById('cable-glow')?.addEventListener('input', (e) => {
      const intensity = e.target.value / 100;
      this.globe.arcStroke(d => d.stroke * intensity);
    });
    
    document.getElementById('flow-speed')?.addEventListener('input', (e) => {
      const speed = 5000 / e.target.value;
      this.globe.arcDashAnimateTime(speed);
    });
    
    document.getElementById('datacenter-filter')?.addEventListener('change', (e) => {
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
  
  setupInteractiveElements() {
    // Close info panel
    document.querySelector('.info-close')?.addEventListener('click', () => {
      document.getElementById('info-panel').classList.add('hidden');
    });
    
    // Panel toggle
    document.getElementById('panel-toggle')?.addEventListener('click', () => {
      const controls = document.querySelector('.controls');
      if (controls) {
        controls.style.display = controls.style.display === 'none' ? 'block' : 'none';
      }
    });
  }
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'r':
        case 'R':
          // Reset view
          this.globe.pointOfView({ lat: 20, lng: 0, altitude: 2.5 }, 1000);
          break;
        case 'p':
        case 'P':
          // Toggle performance monitor
          const perfMon = document.querySelector('.performance-monitor');
          if (perfMon) {
            perfMon.style.display = perfMon.style.display === 'none' ? 'flex' : 'none';
          }
          break;
        case 'h':
        case 'H':
          // Toggle help/controls
          const panel = document.querySelector('.control-panel');
          if (panel) {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
          }
          break;
      }
    });
  }
  
  updateLoadingStatus(message, progress = null) {
    const statusElement = document.querySelector('.loading-status');
    const progressBar = document.querySelector('.loading-progress');
    
    if (statusElement) {
      statusElement.textContent = message;
    }
    
    if (progressBar && progress !== null) {
      progressBar.style.width = `${progress}%`;
    }
  }
  
  hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
      gsap.to(loadingScreen, {
        opacity: 0,
        duration: 1,
        onComplete: () => {
          loadingScreen.classList.add('hidden');
          loadingScreen.style.display = 'none';
        }
      });
    }
  }
  
  showDataError(error) {
    console.error('Data loading error:', error);
    
    // Show error notification
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.style.cssText = `
      position: fixed;
      top: 100px;
      right: 30px;
      background: rgba(255, 51, 102, 0.1);
      border: 1px solid #ff3366;
      border-radius: 8px;
      padding: 15px;
      color: #fff;
      font-family: 'Inter', sans-serif;
      font-size: 14px;
      z-index: 10000;
      max-width: 300px;
      backdrop-filter: blur(10px);
    `;
    
    notification.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 5px;">Data Loading Issue</div>
      <div style="font-size: 12px; opacity: 0.8;">
        Some data sources are unavailable. Using cached/estimated data.
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      gsap.to(notification, {
        opacity: 0,
        x: 20,
        duration: 0.5,
        onComplete: () => notification.remove()
      });
    }, 5000);
  }
  
  handleInitError(error) {
    console.error('Initialization error:', error);
    this.state.error = error;
    
    // Show error screen
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
      const content = loadingScreen.querySelector('.loading-content');
      if (content) {
        content.innerHTML = `
          <div style="text-align: center;">
            <h2 style="color: #ff3366;">Initialization Error</h2>
            <p style="color: #fff; margin: 20px 0;">
              Failed to initialize the infrastructure map.
            </p>
            <p style="color: #aaa; font-size: 14px;">
              ${error.message || 'Unknown error occurred'}
            </p>
            <button onclick="location.reload()" style="
              margin-top: 20px;
              padding: 10px 20px;
              background: #00ffcc;
              color: #000;
              border: none;
              border-radius: 5px;
              cursor: pointer;
              font-weight: bold;
            ">
              Retry
            </button>
          </div>
        `;
      }
    }
  }
  
  onWindowResize() {
    if (this.globe) {
      this.globe.width(window.innerWidth);
      this.globe.height(window.innerHeight);
    }
  }
  
  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());
    
    // Calculate FPS
    const now = performance.now();
    if (this.lastTime) {
      const delta = now - this.lastTime;
      this.stats.fps = 1000 / delta;
      this.frameCount++;
      
      // Update stats every 30 frames
      if (this.frameCount % 30 === 0) {
        this.updateStats();
      }
    }
    this.lastTime = now;
  }
  
  destroy() {
    // Cleanup
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    if (this.attackInterval) {
      clearInterval(this.attackInterval);
    }
    
    // Clean up GSAP animations
    gsap.killTweensOf('*');
    
    // Clean up Globe.gl
    if (this.globe) {
      this.globe._destructor && this.globe._destructor();
    }
  }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  window.app = new InternetInfrastructureMap();
  
  // Add cleanup on page unload
  window.addEventListener('beforeunload', () => {
    if (window.app) {
      window.app.destroy();
    }
  });
});

export default InternetInfrastructureMap;