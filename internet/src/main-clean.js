import Globe from 'globe.gl';
import * as THREE from 'three';
import * as d3 from 'd3';
import { DataManager } from './dataManager.js';
// Removed custom cable renderer - using globe.gl paths instead

class CleanInfrastructureMap {
  constructor() {
    this.container = document.getElementById('globe-container');
    this.globe = null;
    this.dataManager = new DataManager();
    
    // Store original data for toggling
    this.originalData = {
      cables: [],
      datacenters: []
    };
    
    // Store all cables and datacenters for filtering
    this.allCables = [];
    this.allDatacenters = [];
    
    // Design system
    this.design = {
      colors: {
        // Minimal, professional color palette
        primary: 'rgba(0, 200, 255, 0.6)',      // Light blue for main cables
        secondary: 'rgba(255, 100, 150, 0.4)',   // Soft pink for secondary
        tertiary: 'rgba(150, 200, 100, 0.3)',    // Soft green for regional
        accent: 'rgba(255, 200, 50, 0.5)',       // Gold for highlights
        datacenter: 'rgba(255, 255, 255, 0.8)',  // White for data centers
      },
      cable: {
        maxStroke: 2.0,  // Slightly thicker for visibility
        minStroke: 0.5,
        maxAltitude: 0.25, // Higher arcs to prevent cutoff
        minAltitude: 0.08
      }
    };
    
    this.stats = {
      cables: 0,
      datacenters: 0,
    };
    
    this.init();
  }
  
  async init() {
    this.setupLoadingScreen();
    await this.createCleanGlobe();
    await this.loadCleanData();
    this.setupMinimalControls();
    this.hideLoadingScreen();
  }
  
  setupLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
      // Simplify loading screen
      const content = loadingScreen.querySelector('.loading-content');
      if (content) {
        content.innerHTML = `
          <div style="text-align: center;">
            <div style="
              width: 60px;
              height: 60px;
              border: 2px solid rgba(0, 200, 255, 0.2);
              border-top-color: rgba(0, 200, 255, 0.8);
              border-radius: 50%;
              animation: spin 1s linear infinite;
              margin: 0 auto 20px;
            "></div>
            <h2 style="font-weight: 300; font-size: 1.5rem; color: #fff;">
              Loading Infrastructure Data
            </h2>
            <p style="color: #666; font-size: 0.9rem;" class="loading-status">
              Initializing globe...
            </p>
          </div>
          <style>
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          </style>
        `;
      }
    }
  }
  
  async createCleanGlobe() {
    return new Promise((resolve) => {
      // Dark, minimal globe
      this.globe = Globe()
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
        .showAtmosphere(true)
        .atmosphereColor('rgba(100, 150, 200, 0.15)')
        .atmosphereAltitude(0.2)
        .backgroundColor('rgba(0, 0, 0, 0)')
        .onGlobeReady(() => {
          this.setupCleanScene();
          resolve();
        });
      
      this.globe(this.container);
      
      // Using globe.gl's path rendering for cables
      
      // Set initial view to Atlantic for cable visibility
      this.globe.pointOfView({ 
        lat: 20, 
        lng: -40, 
        altitude: 2.8  // Further out to see full arcs without clipping
      }, 0);
    });
  }
  
  setupCleanScene() {
    const scene = this.globe.scene();
    const renderer = this.globe.renderer();
    const controls = this.globe.controls();
    const camera = this.globe.camera();
    
    // High quality rendering
    renderer.antialias = true;
    renderer.toneMapping = THREE.LinearToneMapping;
    renderer.toneMappingExposure = 0.8;
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Adjust camera settings for better arc visibility
    camera.near = 0.1;
    camera.far = 10000;
    camera.updateProjectionMatrix();
    
    // Smooth rotation
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5; // Slightly faster for better visibility
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 0.8;
    controls.minDistance = 120; // Prevent too close zoom that might clip arcs
    controls.maxDistance = 500; // Allow further zoom out to see full arcs
    
    // Minimal lighting
    scene.traverse((child) => {
      if (child instanceof THREE.Light) {
        scene.remove(child);
      }
    });
    
    // Single ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);
    
    // Soft directional light
    const sunLight = new THREE.DirectionalLight(0xffffff, 0.3);
    sunLight.position.set(50, 50, 50);
    scene.add(sunLight);
    
    // Very subtle stars
    this.addSubtleStars(scene);
  }
  
  addSubtleStars(scene) {
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.3,
      transparent: true,
      opacity: 0.3
    });
    
    const starsVertices = [];
    // Fewer, more subtle stars
    for (let i = 0; i < 2000; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 600;
      
      starsVertices.push(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      );
    }
    
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    scene.add(new THREE.Points(starsGeometry, starsMaterial));
  }
  
  async loadCleanData() {
    try {
      // Load only essential data
      this.updateLoadingStatus('Loading submarine cables...');
      const cables = await this.dataManager.loadSubmarineCables();
      this.allCables = cables; // Store all cables for filtering
      
      // Use default filters (all)
      const defaultFilters = {
        accuracy: 'all',
        region: 'all',
        capacity: 'all',
        majorOnly: false
      };
      this.renderCleanCables(cables, defaultFilters);
      
      this.updateLoadingStatus('Loading data centers...');
      const datacenters = await this.dataManager.loadDataCenters();
      this.renderMinimalDataCenters(datacenters);
      
      this.updateStats();
    } catch (error) {
      console.error('Data loading error:', error);
    }
  }
  
  renderCleanCables(cables, filters = {}) {
    // Default filters
    const {
      accuracy = 'all',
      region = 'all',
      capacity = 'all',
      majorOnly = false
    } = filters;
    
    // Group cables by importance and region
    const importantCables = majorOnly ? 
      cables.filter(c => c.capacity_tbps > 100 || c.name.includes('MAREA') || c.name.includes('Grace') || c.name.includes('2Africa')) :
      this.selectImportantCables(cables);
    
    // Apply filters
    let filteredCables = importantCables;
    console.log(`Starting with ${filteredCables.length} cables`);
    
    // Accuracy filter
    if (accuracy === 'live') {
      filteredCables = filteredCables.filter(cable => cable.data_accuracy === 'live');
      console.log(`After accuracy filter (live): ${filteredCables.length} cables`);
    } else if (accuracy === 'estimated') {
      filteredCables = filteredCables.filter(cable => cable.data_accuracy !== 'live');
      console.log(`After accuracy filter (estimated): ${filteredCables.length} cables`);
    }
    
    // Region filter
    if (region !== 'all') {
      const beforeRegion = filteredCables.length;
      filteredCables = filteredCables.filter(cable => {
        const avgLng = (cable.landing_point_1.longitude + cable.landing_point_2.longitude) / 2;
        const avgLat = (cable.landing_point_1.latitude + cable.landing_point_2.latitude) / 2;
        const distance = this.calculateDistance(
          cable.landing_point_1.latitude,
          cable.landing_point_1.longitude,
          cable.landing_point_2.latitude,
          cable.landing_point_2.longitude
        );
        
        const lng1 = cable.landing_point_1.longitude;
        const lng2 = cable.landing_point_2.longitude;
        const lat1 = cable.landing_point_1.latitude;
        const lat2 = cable.landing_point_2.latitude;
        const loc1 = cable.landing_point_1.location || '';
        const loc2 = cable.landing_point_2.location || '';
        
        switch(region) {
          case 'transatlantic':
            // Cables crossing the Atlantic (Americas to Europe/Africa)
            const isTransAtlantic = 
              (lng1 < -40 && lng2 > -20 && lng2 < 30) || // Americas to Europe/Africa
              (lng2 < -40 && lng1 > -20 && lng1 < 30);   // Europe/Africa to Americas
            return isTransAtlantic && distance > 2000;
            
          case 'transpacific':
            // Cables crossing the Pacific Ocean
            const crossesPacific = 
              (Math.abs(lng1 - lng2) > 120) && // Large longitude difference
              ((lng1 > 100 || lng1 < -100) || (lng2 > 100 || lng2 < -100)); // One end in Pacific region
            return crossesPacific && distance > 3000;
            
          case 'europe-asia':
            // Cables connecting Europe to Asia
            const europeToAsia = 
              ((lng1 > -10 && lng1 < 50 && lng2 > 50) || // Europe to Asia
               (lng2 > -10 && lng2 < 50 && lng1 > 50)) && // Asia to Europe
              distance > 1000;
            return europeToAsia;
            
          case 'americas-internal':
            // Cables within the Americas
            return lng1 < -30 && lng2 < -30 && distance < 8000;
            
          case 'europe-internal':
            // Cables within Europe
            return lng1 > -15 && lng1 < 50 && lng2 > -15 && lng2 < 50 && 
                   lat1 > 35 && lat2 > 35 && distance < 4000;
            
          case 'asia-internal':
            // Cables within Asia-Pacific
            return lng1 > 60 && lng2 > 60 && distance < 6000;
            
          case 'africa-connected':
            // Cables connecting to/from Africa
            return loc1.includes('Africa') || loc2.includes('Africa') ||
                   loc1.includes('Cape Town') || loc2.includes('Cape Town') ||
                   loc1.includes('Cairo') || loc2.includes('Cairo') ||
                   loc1.includes('Lagos') || loc2.includes('Lagos') ||
                   loc1.includes('Nairobi') || loc2.includes('Nairobi') ||
                   (avgLng > -20 && avgLng < 55 && avgLat < 35 && avgLat > -35);
                   
          default:
            return true;
        }
      });
      console.log(`After region filter (${region}): ${filteredCables.length} cables`);
    }
    
    // Capacity filter
    if (capacity !== 'all') {
      const beforeCapacity = filteredCables.length;
      filteredCables = filteredCables.filter(cable => {
        const cap = cable.capacity_tbps || 0;
        switch(capacity) {
          case 'high':
            return cap > 150;
          case 'medium':
            return cap >= 50 && cap <= 150;
          case 'low':
            return cap < 50;
          default:
            return true;
        }
      });
      console.log(`After capacity filter (${capacity}): ${filteredCables.length} cables`);
    }
    
    console.log(`Final filtered cables: ${filteredCables.length}`);
    
    const cableArcs = filteredCables.map(cable => {
      const importance = this.calculateImportance(cable);
      const opacity = 0.85 + (importance * 0.15); // High opacity for better visibility
      
      // Ensure valid coordinates
      let startLat = parseFloat(cable.landing_point_1.latitude);
      let startLng = parseFloat(cable.landing_point_1.longitude);
      let endLat = parseFloat(cable.landing_point_2.latitude);
      let endLng = parseFloat(cable.landing_point_2.longitude);
      
      // Skip invalid cables
      if (isNaN(startLat) || isNaN(startLng) || isNaN(endLat) || isNaN(endLng)) {
        return null;
      }
      
      // Normalize coordinates to [-180, 180] for longitude
      startLng = ((startLng + 180) % 360) - 180;
      endLng = ((endLng + 180) % 360) - 180;
      
      // Don't handle date line crossing - let globe.gl handle it
      // This prevents arc cutoff issues
      
      // Calculate great circle distance for proper altitude
      const distance = this.calculateDistance(startLat, startLng, endLat, endLng);
      
      // Increased altitude for better visibility of long cables
      // Using a more aggressive scaling for ultra-long cables to prevent cutoff
      let altitude;
      if (distance > 15000) {
        // Ultra-long transoceanic cables need higher arcs to avoid cutoff
        // Scale more aggressively for distances beyond 15000km
        altitude = 0.5 + ((distance - 15000) / 5000) * 0.2; // 0.5 to 0.7 for longest cables
      } else if (distance > 10000) {
        altitude = 0.35; // Transoceanic cables - high arc
      } else if (distance > 5000) {
        altitude = 0.25; // Long distance - medium-high arc
      } else if (distance > 2000) {
        altitude = 0.15; // Regional - moderate arc
      } else if (distance > 1000) {
        altitude = 0.08; // Medium distance - low arc
      } else {
        altitude = 0.04; // Short distance - minimal arc
      }
      
      return {
        startLat: startLat,
        startLng: startLng,
        endLat: endLat,
        endLng: endLng,
        startLocation: cable.landing_point_1.location || null,
        endLocation: cable.landing_point_2.location || null,
        color: this.getCableColor(cable, opacity),
        stroke: Math.max(0.8, this.getCableStroke(importance)), // Ensure minimum visibility
        altitude: altitude,
        label: cable.name,
        capacity: cable.capacity_tbps,
        owner: cable.owner,
        status: cable.status,
        accuracy: cable.data_accuracy || 'estimated',
        importance: importance
      };
    }).filter(arc => arc !== null); // Remove invalid arcs
    
    // Sort by importance (render less important first)
    cableArcs.sort((a, b) => a.importance - b.importance);
    
    // Store original data
    this.originalData.cables = cableArcs;
    
    console.log(`Rendering ${cableArcs.length} cable arcs`);
    
    // Use arcs with altitude based on distance for natural curve
    this.globe
      .arcsData(cableArcs)
      .arcStartLat('startLat')
      .arcStartLng('startLng')
      .arcEndLat('endLat')
      .arcEndLng('endLng')
      .arcColor('color')
      .arcStroke('stroke')
      .arcAltitude('altitude') // Use the altitude property from arc data
      .arcDashLength(0)
      .arcDashGap(0)
      .arcDashAnimateTime(0)
      .arcCurveResolution(64) // Higher resolution for smoother curves
      .arcsTransitionDuration(0) // Instant rendering
      .arcLabel(arc => this.createCleanTooltip(arc));
    
    this.stats.cables = filteredCables.length;
  }
  
  selectImportantCables(cables) {
    // Select only the most important cables to avoid clutter
    const important = [];
    const seen = new Set();
    
    // First, add known major cables (with full data)
    const majorCableNames = [
      'MAREA', 'Grace Hopper', '2Africa', 'Dunant', 'FASTER',
      'Pacific Light Cable Network', 'JUPITER', 'SEA-ME-WE 5',
      'EllaLink', 'Australia-Singapore Cable'
    ];
    
    cables.forEach(cable => {
      if (cable.name && majorCableNames.some(name => cable.name.includes(name))) {
        // Ensure all properties are included
        important.push({
          ...cable,
          data_accuracy: cable.data_accuracy || 'estimated'
        });
        seen.add(cable.name);
      }
    });
    
    // Add high-capacity cables
    cables
      .filter(c => !seen.has(c.name) && c.capacity_tbps > 30)
      .slice(0, 100)
      .forEach(cable => {
        important.push({
          ...cable,
          data_accuracy: cable.data_accuracy || 'estimated'
        });
        seen.add(cable.name);
      });
    
    // Add medium-capacity cables for coverage
    cables
      .filter(c => !seen.has(c.name) && c.capacity_tbps > 10)
      .slice(0, 50)
      .forEach(cable => {
        important.push({
          ...cable,
          data_accuracy: cable.data_accuracy || 'estimated'
        });
        seen.add(cable.name);
      });
    
    // Add regional diversity
    const regions = this.groupByRegion(cables);
    Object.values(regions).forEach(regionCables => {
      regionCables
        .filter(c => !seen.has(c.name))
        .slice(0, 5)
        .forEach(cable => {
          important.push({
            ...cable,
            data_accuracy: cable.data_accuracy || 'estimated'
          });
          seen.add(cable.name);
        });
    });
    
    // Return all cables instead of limiting to 200
    return cables; // Show all 550+ cables
  }
  
  groupByRegion(cables) {
    const regions = {
      atlantic: [],
      pacific: [],
      indian: [],
      mediterranean: [],
      caribbean: [],
      other: []
    };
    
    cables.forEach(cable => {
      const avgLng = (cable.landing_point_1.longitude + cable.landing_point_2.longitude) / 2;
      const avgLat = (cable.landing_point_1.latitude + cable.landing_point_2.latitude) / 2;
      
      if (avgLng > -100 && avgLng < -20 && Math.abs(avgLat) < 60) {
        regions.atlantic.push(cable);
      } else if (avgLng > 100 || avgLng < -100) {
        regions.pacific.push(cable);
      } else if (avgLng > 20 && avgLng < 100 && avgLat < 30) {
        regions.indian.push(cable);
      } else if (avgLng > -20 && avgLng < 45 && avgLat > 30 && avgLat < 45) {
        regions.mediterranean.push(cable);
      } else if (avgLng > -90 && avgLng < -60 && avgLat > 10 && avgLat < 30) {
        regions.caribbean.push(cable);
      } else {
        regions.other.push(cable);
      }
    });
    
    return regions;
  }
  
  calculateImportance(cable) {
    let importance = 0;
    
    // Capacity factor (0-0.4)
    if (cable.capacity_tbps > 200) importance += 0.4;
    else if (cable.capacity_tbps > 100) importance += 0.3;
    else if (cable.capacity_tbps > 50) importance += 0.2;
    else importance += 0.1;
    
    // Distance factor (0-0.3)
    const distance = this.calculateDistance(
      cable.landing_point_1.latitude,
      cable.landing_point_1.longitude,
      cable.landing_point_2.latitude,
      cable.landing_point_2.longitude
    );
    
    if (distance > 8000) importance += 0.3;
    else if (distance > 5000) importance += 0.2;
    else if (distance > 2000) importance += 0.1;
    
    // Status factor (0-0.3)
    if (cable.status === 'active') importance += 0.3;
    else if (cable.status === 'planned') importance += 0.1;
    
    return Math.min(importance, 1);
  }
  
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
  
  getCableColor(cable, opacity) {
    // Color based on capacity to match legend - using higher opacity for visibility
    const capacity = cable.capacity_tbps || 50;
    const minOpacity = 0.6; // Ensure minimum visibility
    const actualOpacity = Math.max(minOpacity, opacity);
    
    if (capacity > 150) {
      // High capacity - bright cyan/green gradient
      return `rgba(0, 255, 204, ${actualOpacity})`; // Matches high-capacity in legend
    } else if (capacity >= 50 && capacity <= 150) {
      // Medium capacity - golden/orange gradient
      return `rgba(255, 204, 0, ${actualOpacity})`; // Matches medium-capacity in legend
    } else {
      // Low capacity - pink/magenta gradient
      return `rgba(255, 0, 255, ${actualOpacity})`; // Matches low-capacity in legend
    }
  }
  
  getCableColorForPath(cable) {
    // Color based on capacity to match legend (hex for paths)
    const capacity = cable.capacity || cable.capacity_tbps || 50;
    
    if (capacity > 150) {
      return '#00ffcc'; // Cyan
    } else if (capacity >= 50) {
      return '#ffcc00'; // Gold
    } else {
      return '#ff00ff'; // Magenta
    }
  }
  
  getCableStroke(importance) {
    // Balanced stroke widths for visibility
    const minStroke = 0.8; // Visible minimum
    const maxStroke = 2.0; // Thicker for major cables
    return minStroke + (importance * (maxStroke - minStroke));
  }
  
  getCableAltitude(importance) {
    return this.design.cable.minAltitude + 
           (importance * (this.design.cable.maxAltitude - this.design.cable.minAltitude));
  }
  
  createMinimalTooltip(cable) {
    const importance = cable.importance || 0;
    const borderColor = importance > 0.7 ? 'rgba(0, 200, 255, 0.8)' : 
                       importance > 0.4 ? 'rgba(150, 150, 255, 0.6)' : 
                       'rgba(200, 200, 200, 0.4)';
    
    const accuracyIcon = cable.accuracy === 'live' ? '🟢' : 
                        cable.accuracy === 'estimated' ? '🟡' : '⚪';
    
    const distance = this.calculateDistance(
      cable.startLat, cable.startLng,
      cable.endLat, cable.endLng
    ).toFixed(0);
    
    return `
      <div style="
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        padding: 16px;
        background: linear-gradient(135deg, rgba(10, 10, 20, 0.95), rgba(20, 20, 40, 0.95));
        border: 2px solid ${borderColor};
        border-radius: 12px;
        font-size: 13px;
        color: #fff;
        min-width: 280px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 40px ${borderColor};
      ">
        <div style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
          padding-bottom: 10px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        ">
          <div style="
            font-weight: 600;
            font-size: 15px;
            color: ${borderColor};
            text-shadow: 0 0 10px ${borderColor};
          ">
            ${cable.label || 'Submarine Cable'}
          </div>
          <div style="
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
          ">
            ${accuracyIcon} ${cable.accuracy || 'Unknown'}
          </div>
        </div>
        
        <div style="
          display: grid;
          grid-template-columns: auto 1fr;
          gap: 8px;
          font-size: 12px;
          line-height: 1.6;
        ">
          <span style="color: rgba(255, 255, 255, 0.5);">From:</span>
          <span style="
            color: #fff;
            text-align: right;
            font-size: 11px;
          ">
            ${cable.startLocation || `${cable.startLat.toFixed(2)}°, ${cable.startLng.toFixed(2)}°`}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">To:</span>
          <span style="
            color: #fff;
            text-align: right;
            font-size: 11px;
          ">
            ${cable.endLocation || `${cable.endLat.toFixed(2)}°, ${cable.endLng.toFixed(2)}°`}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Capacity:</span>
          <span style="
            color: #fff;
            font-weight: 500;
            text-align: right;
          ">
            ${cable.capacity ? `${cable.capacity} Tbps` : 'Not specified'}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Distance:</span>
          <span style="
            color: #fff;
            text-align: right;
          ">
            ~${distance} km
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Owner:</span>
          <span style="
            color: #fff;
            text-align: right;
            font-size: 11px;
          ">
            ${cable.owner ? (cable.owner.substring(0, 30) + (cable.owner.length > 30 ? '...' : '')) : 'Consortium'}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Status:</span>
          <span style="
            color: ${cable.status === 'active' ? '#00ff88' : '#ffaa00'};
            text-align: right;
            font-weight: 500;
          ">
            ${(cable.status || 'Active').toUpperCase()}
          </span>
        </div>
        
        <div style="
          margin-top: 12px;
          padding-top: 10px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <div style="
            font-size: 10px;
            color: rgba(255, 255, 255, 0.4);
          ">
            Landing Points
          </div>
          <div style="
            font-size: 10px;
            color: rgba(255, 255, 255, 0.6);
            text-align: right;
          ">
            ${cable.startLat.toFixed(1)}°, ${cable.startLng.toFixed(1)}° → 
            ${cable.endLat.toFixed(1)}°, ${cable.endLng.toFixed(1)}°
          </div>
        </div>
      </div>
    `;
  }
  
  renderMinimalDataCenters(datacenters, tierFilter = 'all') {
    // Store all datacenters
    this.allDatacenters = datacenters;
    
    // Apply tier filter
    let filteredDCs = datacenters;
    if (tierFilter === 'tier1') {
      filteredDCs = datacenters.filter(dc => dc.tier === 1);
    } else if (tierFilter === 'tier2') {
      filteredDCs = datacenters.filter(dc => dc.tier === 2);
    } else if (tierFilter === 'tier3') {
      filteredDCs = datacenters.filter(dc => dc.tier === 3);
    }
    
    // Limit display for performance
    const tier1 = filteredDCs.filter(dc => dc.tier === 1).slice(0, 50);
    const tier2 = filteredDCs.filter(dc => dc.tier === 2).slice(0, 30);
    const tier3 = filteredDCs.filter(dc => dc.tier === 3).slice(0, 20);
    
    const allDCs = [...tier1, ...tier2, ...tier3];
    
    const points = allDCs.map(dc => ({
      lat: dc.latitude,
      lng: dc.longitude,
      size: dc.tier === 1 ? 0.5 : dc.tier === 2 ? 0.35 : 0.25, // Larger, more visible sizes
      color: dc.tier === 1 ? 'rgba(0, 255, 204, 0.9)' :  // Cyan for tier 1 (matches legend)
             dc.tier === 2 ? 'rgba(255, 204, 0, 0.8)' :  // Gold for tier 2 (matches legend)
             'rgba(255, 0, 255, 0.7)', // Magenta for tier 3 (matches legend)
      label: `${dc.city}, ${dc.country}`,
      name: dc.name,
      city: dc.city,
      country: dc.country,
      tier: dc.tier,
      provider: dc.provider,
      accuracy: dc.data_accuracy
    }));
    
    // Store original data
    this.originalData.datacenters = points;
    
    this.globe
      .pointsData(points)
      .pointLat('lat')
      .pointLng('lng')
      .pointColor('color')
      .pointAltitude(0.01) // Slightly raised from surface
      .pointRadius('size')
      .pointLabel(d => this.createDataCenterTooltip(d));
    
    this.stats.datacenters = points.length;
  }
  
  createCleanTooltip(cable) {
    // Create tooltip for cable arcs
    const distance = this.calculateDistance(
      cable.startLat,
      cable.startLng, 
      cable.endLat,
      cable.endLng
    );
    
    const accuracyIcon = cable.accuracy === 'live' ? '🟢' : 
                        cable.accuracy === 'estimated' ? '🟡' : '⚪';
    
    const borderColor = cable.capacity > 150 ? '#00ffcc' :
                       cable.capacity > 50 ? '#ffcc00' : '#ff00ff';
    
    return `
      <div style="
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        padding: 16px;
        background: linear-gradient(135deg, rgba(10, 10, 20, 0.98), rgba(20, 15, 30, 0.98));
        border: 2px solid ${borderColor};
        border-radius: 12px;
        font-size: 12px;
        color: #fff;
        min-width: 280px;
        max-width: 350px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 40px ${borderColor}33;
      ">
        <div style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
          padding-bottom: 10px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        ">
          <div style="
            font-weight: 600;
            font-size: 15px;
            color: ${borderColor};
            text-shadow: 0 0 10px ${borderColor};
          ">
            ${cable.label || 'Submarine Cable'}
          </div>
          <div style="
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
          ">
            ${accuracyIcon} ${cable.accuracy || 'Unknown'}
          </div>
        </div>
        
        <div style="
          display: grid;
          grid-template-columns: auto 1fr;
          gap: 8px;
          font-size: 12px;
          line-height: 1.6;
        ">
          <span style="color: rgba(255, 255, 255, 0.5);">From:</span>
          <span style="
            color: #fff;
            text-align: right;
            font-size: 11px;
          ">
            ${cable.startLocation || `${cable.startLat.toFixed(2)}°, ${cable.startLng.toFixed(2)}°`}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">To:</span>
          <span style="
            color: #fff;
            text-align: right;
            font-size: 11px;
          ">
            ${cable.endLocation || `${cable.endLat.toFixed(2)}°, ${cable.endLng.toFixed(2)}°`}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Capacity:</span>
          <span style="
            color: #fff;
            font-weight: 500;
            text-align: right;
          ">
            ${cable.capacity ? `${cable.capacity} Tbps` : 'Not specified'}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Distance:</span>
          <span style="
            color: #fff;
            text-align: right;
          ">
            ~${Math.round(distance)} km
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Owner:</span>
          <span style="
            color: #fff;
            text-align: right;
            font-size: 11px;
          ">
            ${cable.owner ? (cable.owner.substring(0, 30) + (cable.owner.length > 30 ? '...' : '')) : 'Consortium'}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Status:</span>
          <span style="
            color: ${cable.status === 'active' ? '#00ff88' : '#ffaa00'};
            text-align: right;
            font-weight: 500;
          ">
            ${(cable.status || 'Active').toUpperCase()}
          </span>
        </div>
      </div>
    `;
  }
  
  createDataCenterTooltip(dc) {
    const accuracyIcon = dc.accuracy === 'live' ? '🟢' : 
                        dc.accuracy === 'estimated' ? '🟡' : '⚪';
    
    return `
      <div style="
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        padding: 14px;
        background: linear-gradient(135deg, rgba(10, 10, 20, 0.95), rgba(30, 20, 40, 0.95));
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        font-size: 12px;
        color: #fff;
        min-width: 240px;
        backdrop-filter: blur(20px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4), 0 0 30px rgba(255, 255, 255, 0.1);
      ">
        <div style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 10px;
          padding-bottom: 8px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        ">
          <div style="
            font-weight: 600;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
          ">
            ${dc.name || 'Data Center'}
          </div>
          <div style="
            font-size: 10px;
            color: rgba(255, 255, 255, 0.5);
          ">
            ${accuracyIcon} ${dc.accuracy || 'estimated'}
          </div>
        </div>
        
        <div style="
          display: grid;
          grid-template-columns: auto 1fr;
          gap: 6px;
          font-size: 11px;
        ">
          <span style="color: rgba(255, 255, 255, 0.5);">Location:</span>
          <span style="color: #fff; text-align: right;">
            ${dc.city}, ${dc.country}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Tier:</span>
          <span style="
            color: #00ffcc;
            text-align: right;
            font-weight: 500;
          ">
            Tier ${dc.tier}
          </span>
          
          <span style="color: rgba(255, 255, 255, 0.5);">Provider:</span>
          <span style="color: #fff; text-align: right; font-size: 10px;">
            ${dc.provider || 'Unknown'}
          </span>
        </div>
        
        <div style="
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          font-size: 9px;
          color: rgba(255, 255, 255, 0.4);
          text-align: center;
        ">
          ${dc.lat.toFixed(4)}°, ${dc.lng.toFixed(4)}°
        </div>
      </div>
    `;
  }
  
  renderCablesAsCustomLines(cables, filters = {}) {
    // Apply filters first
    let filteredCables = this.applyFilters(cables, filters);
    
    // Clear any existing custom objects
    if (this.cableGroup) {
      this.globe.scene().remove(this.cableGroup);
    }
    
    // Create a new group for cables
    this.cableGroup = new THREE.Group();
    
    // Render each cable as a custom line on the globe surface
    filteredCables.forEach(cable => {
      const points = [];
      const radius = 100; // Globe radius in globe.gl
      
      // Create points along the great circle
      const lat1 = cable.landing_point_1.latitude * Math.PI / 180;
      const lon1 = cable.landing_point_1.longitude * Math.PI / 180;
      const lat2 = cable.landing_point_2.latitude * Math.PI / 180;
      const lon2 = cable.landing_point_2.longitude * Math.PI / 180;
      
      // Calculate great circle segments
      const segments = 50;
      for (let i = 0; i <= segments; i++) {
        const f = i / segments;
        
        // Spherical interpolation
        const sinLat = Math.sin(lat1) * (1-f) + Math.sin(lat2) * f;
        const cosLat = Math.sqrt(1 - sinLat * sinLat);
        const lon = lon1 + (lon2 - lon1) * f;
        
        // Convert to cartesian coordinates
        const x = radius * cosLat * Math.cos(lon);
        const y = radius * sinLat;
        const z = radius * cosLat * Math.sin(lon);
        
        points.push(new THREE.Vector3(x, y, z));
      }
      
      // Create the line
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const material = new THREE.LineBasicMaterial({
        color: new THREE.Color(cable.color || 0x00ffcc),
        linewidth: 2,
        transparent: true,
        opacity: 0.8
      });
      
      const line = new THREE.Line(geometry, material);
      this.cableGroup.add(line);
    });
    
    // Add the group to the scene
    this.globe.scene().add(this.cableGroup);
    
    // Store for reference
    this.originalData.cables = filteredCables;
    this.stats.cables = filteredCables.length;
  }
  
  applyFilters(cables, filters) {
    const {
      accuracy = 'all',
      region = 'all',
      capacity = 'all',
      majorOnly = false
    } = filters;
    
    let filtered = majorOnly ? 
      cables.filter(c => c.capacity_tbps > 100 || c.name.includes('MAREA') || c.name.includes('Grace') || c.name.includes('2Africa')) :
      this.selectImportantCables(cables);
    
    // Apply other filters...
    if (accuracy === 'live') {
      filtered = filtered.filter(cable => cable.data_accuracy === 'live');
    } else if (accuracy === 'estimated') {
      filtered = filtered.filter(cable => cable.data_accuracy !== 'live');
    }
    
    // Add region and capacity filters as before...
    
    return filtered;
  }
  
  renderCablesAsLines(cables, filters = {}) {
    const {
      accuracy = 'all',
      region = 'all',
      capacity = 'all',
      majorOnly = false
    } = filters;
    
    // Apply same filtering logic
    let filteredCables = majorOnly ? 
      cables.filter(c => c.capacity_tbps > 100 || c.name.includes('MAREA') || c.name.includes('Grace') || c.name.includes('2Africa')) :
      this.selectImportantCables(cables);
    
    // Accuracy filter
    if (accuracy === 'live') {
      filteredCables = filteredCables.filter(cable => cable.data_accuracy === 'live');
    } else if (accuracy === 'estimated') {
      filteredCables = filteredCables.filter(cable => cable.data_accuracy !== 'live');
    }
    
    // Region filter
    if (region !== 'all') {
      filteredCables = filteredCables.filter(cable => {
        const lat1 = cable.landing_point_1.latitude;
        const lng1 = cable.landing_point_1.longitude;
        const lat2 = cable.landing_point_2.latitude;
        const lng2 = cable.landing_point_2.longitude;
        
        switch(region) {
          case 'transatlantic':
            return ((lng1 < -40 && lng2 > -20) || (lng2 < -40 && lng1 > -20)) && 
                   Math.abs(lat1 - lat2) < 30;
          case 'transpacific':
            return Math.abs(lng1 - lng2) > 100 && 
                   ((lng1 > 100 || lng1 < -100) && (lng2 > 100 || lng2 < -100));
          case 'europe-asia':
            return ((lng1 < 40 && lng2 > 40) || (lng2 < 40 && lng1 > 40)) &&
                   lat1 > 20 && lat2 > 0;
          case 'americas-internal':
            return lng1 < -30 && lng2 < -30;
          case 'europe-internal':
            return lng1 > -10 && lng1 < 40 && lng2 > -10 && lng2 < 40 &&
                   lat1 > 35 && lat2 > 35;
          case 'asia-internal':
            return lng1 > 60 && lng2 > 60;
          case 'africa-connected':
            return (lat1 < 35 && lat1 > -35 && lng1 > -20 && lng1 < 55) ||
                   (lat2 < 35 && lat2 > -35 && lng2 > -20 && lng2 < 55);
          default:
            return true;
        }
      });
    }
    
    // Capacity filter
    if (capacity !== 'all') {
      filteredCables = filteredCables.filter(cable => {
        const cap = cable.capacity_tbps || 50;
        switch(capacity) {
          case 'high': return cap > 150;
          case 'medium': return cap >= 50 && cap <= 150;
          case 'low': return cap < 50;
          default: return true;
        }
      });
    }
    
    // Create path data with multiple points for smooth curves
    const pathData = filteredCables.map(cable => {
      const points = [];
      const startLat = cable.landing_point_1.latitude;
      const startLng = cable.landing_point_1.longitude;
      const endLat = cable.landing_point_2.latitude;
      const endLng = cable.landing_point_2.longitude;
      
      // Generate intermediate points for a smooth curve
      const numPoints = 50;
      for (let i = 0; i <= numPoints; i++) {
        const t = i / numPoints;
        
        // Interpolate along great circle
        const lat = startLat + (endLat - startLat) * t;
        const lng = startLng + (endLng - startLng) * t;
        
        // Add slight curve by adjusting altitude based on position
        const altitude = Math.sin(t * Math.PI) * 0.02; // Very low curve
        
        points.push([lat, lng, altitude]);
      }
      
      const importance = cable.capacity_tbps ? cable.capacity_tbps / 200 : 0.5;
      const opacity = 0.3 + importance * 0.4;
      
      return {
        coords: points,
        color: this.getCableColor(cable, opacity),
        stroke: Math.max(0.5, importance * 2),
        label: cable.name,
        cable: cable // Store original cable data
      };
    });
    
    // Use paths data instead of arcs
    this.globe
      .pathsData(pathData)
      .pathPoints('coords')
      .pathColor('color')
      .pathStroke('stroke')
      .pathDashLength(0)
      .pathDashGap(0)
      .pathDashAnimateTime(0)
      .pathLabel(d => this.createMinimalTooltip(d.cable))
      .pathTransitionDuration(1500);
    
    this.stats.cables = pathData.length;
    this.originalData.cables = pathData;
  }
  
  setupInfoTooltips() {
    // Smart positioning function - centers tooltip for maximum visibility
    const positionTooltip = (tooltip, triggerElement) => {
      // Get viewport dimensions
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight
      };
      
      // Set tooltip width with responsive sizing
      const tooltipWidth = Math.min(420, viewport.width - 40);
      const tooltipMaxHeight = viewport.height - 40;
      
      // Calculate centered position
      const centerX = (viewport.width - tooltipWidth) / 2;
      const centerY = 20; // Fixed top position with margin
      
      // Apply styles
      tooltip.style.width = `${tooltipWidth}px`;
      tooltip.style.left = `${centerX}px`;
      tooltip.style.top = `${centerY}px`;
      tooltip.style.maxHeight = `${tooltipMaxHeight}px`;
      tooltip.style.transform = 'none'; // Clear any transform
      
      // Add semi-transparent overlay behind tooltip for better focus
      const overlay = document.getElementById('tooltip-overlay');
      if (overlay) {
        overlay.classList.remove('hidden');
      } else {
        // Create overlay if it doesn't exist
        const newOverlay = document.createElement('div');
        newOverlay.id = 'tooltip-overlay';
        newOverlay.className = 'tooltip-overlay';
        newOverlay.addEventListener('click', () => {
          document.querySelectorAll('.info-tooltip').forEach(t => {
            t.classList.remove('visible');
          });
          newOverlay.classList.add('hidden');
        });
        document.body.appendChild(newOverlay);
      }
      
      // For mobile, adjust margins
      if (viewport.width < 768) {
        tooltip.style.left = '10px';
        tooltip.style.width = `${viewport.width - 20}px`;
        tooltip.style.top = '10px';
        tooltip.style.maxHeight = `${viewport.height - 20}px`;
      }
    };
    
    // Helper function to toggle tooltip with smart positioning
    const toggleTooltip = (tooltipId, triggerElement) => {
      const tooltip = document.getElementById(tooltipId);
      const overlay = document.getElementById('tooltip-overlay');
      
      if (tooltip) {
        // Hide all other tooltips first
        document.querySelectorAll('.info-tooltip').forEach(t => {
          if (t.id !== tooltipId) {
            t.classList.remove('visible');
          }
        });
        
        // Toggle the clicked tooltip
        const isVisible = tooltip.classList.contains('visible');
        
        if (!isVisible) {
          // Show tooltip
          tooltip.classList.add('visible');
          positionTooltip(tooltip, triggerElement);
        } else {
          // Hide tooltip
          tooltip.classList.remove('visible');
          if (overlay) {
            overlay.classList.add('hidden');
          }
        }
      }
    };
    
    // Major Cables info
    const majorCablesInfo = document.getElementById('major-cables-info');
    majorCablesInfo?.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleTooltip('major-cables-tooltip', majorCablesInfo);
    });
    
    // Capacity info
    const capacityInfo = document.getElementById('capacity-info');
    capacityInfo?.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleTooltip('capacity-tooltip', capacityInfo);
    });
    
    // Tiers info
    const tiersInfo = document.getElementById('tiers-info');
    tiersInfo?.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleTooltip('tiers-tooltip', tiersInfo);
    });
    
    // Close buttons for tooltips
    const closeTooltip = (tooltipId) => {
      const tooltip = document.getElementById(tooltipId);
      const overlay = document.getElementById('tooltip-overlay');
      if (tooltip) {
        tooltip.classList.remove('visible');
        if (overlay) {
          overlay.classList.add('hidden');
        }
      }
    };
    
    document.getElementById('close-major-tooltip')?.addEventListener('click', () => {
      closeTooltip('major-cables-tooltip');
    });
    
    document.getElementById('close-capacity-tooltip')?.addEventListener('click', () => {
      closeTooltip('capacity-tooltip');
    });
    
    document.getElementById('close-tiers-tooltip')?.addEventListener('click', () => {
      closeTooltip('tiers-tooltip');
    });
    
    // Click outside to close tooltips
    document.addEventListener('click', (e) => {
      // If click is not on an info icon or inside a tooltip, close all tooltips
      if (!e.target.closest('.info-icon') && !e.target.closest('.info-tooltip')) {
        const overlay = document.getElementById('tooltip-overlay');
        document.querySelectorAll('.info-tooltip').forEach(tooltip => {
          tooltip.classList.remove('visible');
        });
        if (overlay) {
          overlay.classList.add('hidden');
        }
      }
    });
    
    // Reposition tooltips on window resize
    window.addEventListener('resize', () => {
      document.querySelectorAll('.info-tooltip.visible').forEach(tooltip => {
        // Find the corresponding trigger element
        let triggerElement = null;
        if (tooltip.id === 'major-cables-tooltip') {
          triggerElement = document.getElementById('major-cables-info');
        } else if (tooltip.id === 'capacity-tooltip') {
          triggerElement = document.getElementById('capacity-info');
        } else if (tooltip.id === 'tiers-tooltip') {
          triggerElement = document.getElementById('tiers-info');
        }
        
        if (triggerElement) {
          positionTooltip(tooltip, triggerElement);
        }
      });
    });
  }
  
  setupDataTables() {
    // Cable table functionality
    const cableTableToggle = document.getElementById('cable-table-toggle');
    const listViewModal = document.getElementById('list-view-modal');
    const listViewClose = document.getElementById('list-view-close');
    const exportBtn = document.getElementById('export-csv');
    const tbody = document.getElementById('cable-tbody');
    const filteredCount = document.getElementById('filtered-count');
    const totalCount = document.getElementById('total-count');
    
    // Function to get current filtered cables
    const getFilteredCables = () => {
      const filters = {
        accuracy: document.getElementById('cable-filter')?.value || 'all',
        region: document.getElementById('region-filter')?.value || 'all',
        capacity: document.getElementById('capacity-filter')?.value || 'all',
        majorOnly: document.getElementById('show-major-only')?.checked || false
      };
      
      // Apply same filtering logic as renderCleanCables
      let filtered = [...this.allCables];
      
      if (filters.majorOnly) {
        filtered = filtered.filter(c => c.capacity_tbps > 100 || c.name.includes('MAREA') || c.name.includes('Grace') || c.name.includes('2Africa'));
      }
      
      if (filters.accuracy === 'live') {
        filtered = filtered.filter(c => c.data_accuracy === 'live');
      } else if (filters.accuracy === 'estimated') {
        filtered = filtered.filter(c => c.data_accuracy !== 'live');
      }
      
      if (filters.region !== 'all') {
        filtered = filtered.filter(cable => {
          const lat1 = cable.landing_point_1.latitude;
          const lng1 = cable.landing_point_1.longitude;
          const lat2 = cable.landing_point_2.latitude;
          const lng2 = cable.landing_point_2.longitude;
          
          switch(filters.region) {
            case 'transatlantic':
              return ((lng1 < -40 && lng2 > -20) || (lng2 < -40 && lng1 > -20)) && 
                     Math.abs(lat1 - lat2) < 30;
            case 'transpacific':
              return Math.abs(lng1 - lng2) > 100 && 
                     ((lng1 > 100 || lng1 < -100) && (lng2 > 100 || lng2 < -100));
            case 'europe-asia':
              return ((lng1 < 40 && lng2 > 40) || (lng2 < 40 && lng1 > 40)) &&
                     lat1 > 20 && lat2 > 0;
            case 'americas-internal':
              return lng1 < -30 && lng2 < -30;
            case 'europe-internal':
              return lng1 > -10 && lng1 < 40 && lng2 > -10 && lng2 < 40 &&
                     lat1 > 35 && lat2 > 35;
            case 'asia-internal':
              return lng1 > 60 && lng2 > 60;
            case 'africa-connected':
              return (lat1 < 35 && lat1 > -35 && lng1 > -20 && lng1 < 55) ||
                     (lat2 < 35 && lat2 > -35 && lng2 > -20 && lng2 < 55);
            default:
              return true;
          }
        });
      }
      
      if (filters.capacity !== 'all') {
        filtered = filtered.filter(cable => {
          const capacity = cable.capacity_tbps || 50;
          switch(filters.capacity) {
            case 'high': return capacity > 150;
            case 'medium': return capacity >= 50 && capacity <= 150;
            case 'low': return capacity < 50;
            default: return true;
          }
        });
      }
      
      return filtered;
    };
    
    // Function to populate table
    const populateTable = () => {
      const cables = getFilteredCables();
      
      // Update counts
      if (filteredCount) filteredCount.textContent = cables.length;
      if (totalCount) totalCount.textContent = this.allCables.length;
      
      // Clear tbody
      if (tbody) {
        tbody.innerHTML = '';
        
        // Add rows
        cables.forEach(cable => {
          const distance = this.calculateDistance(
            cable.landing_point_1.latitude,
            cable.landing_point_1.longitude,
            cable.landing_point_2.latitude,
            cable.landing_point_2.longitude
          );
          
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${cable.name || 'Unknown Cable'}</td>
            <td>${cable.capacity_tbps ? cable.capacity_tbps.toFixed(1) : 'N/A'}</td>
            <td>${Math.round(distance)}</td>
            <td>${cable.landing_point_1.location || `${cable.landing_point_1.latitude.toFixed(1)}°, ${cable.landing_point_1.longitude.toFixed(1)}°`}</td>
            <td>${cable.landing_point_2.location || `${cable.landing_point_2.latitude.toFixed(1)}°, ${cable.landing_point_2.longitude.toFixed(1)}°`}</td>
            <td class="status-${cable.status || 'active'}">${(cable.status || 'Active').toUpperCase()}</td>
            <td class="accuracy-${cable.data_accuracy === 'live' ? 'live' : 'estimated'}">${cable.data_accuracy === 'live' ? 'Live' : 'Estimated'}</td>
          `;
          tbody.appendChild(row);
        });
      }
    };
    
    // Show cable modal
    cableTableToggle?.addEventListener('click', () => {
      if (listViewModal) {
        listViewModal.classList.remove('hidden');
        populateTable();
      }
    });
    
    // Close modal
    listViewClose?.addEventListener('click', () => {
      if (listViewModal) {
        listViewModal.classList.add('hidden');
      }
    });
    
    // Close on background click
    listViewModal?.addEventListener('click', (e) => {
      if (e.target === listViewModal) {
        listViewModal.classList.add('hidden');
      }
    });
    
    // Export functionality
    exportBtn?.addEventListener('click', () => {
      const cables = getFilteredCables();
      const csv = this.exportToCSV(cables);
      this.downloadCSV(csv, 'submarine_cables_export.csv');
    });
    
    // Table sorting
    const sortableHeaders = document.querySelectorAll('#cable-table th.sortable');
    sortableHeaders.forEach(header => {
      header.addEventListener('click', () => {
        const sortBy = header.dataset.sort;
        // Simple sorting implementation (can be enhanced)
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a, b) => {
          const aVal = a.children[header.cellIndex].textContent;
          const bVal = b.children[header.cellIndex].textContent;
          return aVal.localeCompare(bVal, undefined, { numeric: true });
        });
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
      });
    });

    // Data Center table functionality
    const datacenterTableToggle = document.getElementById('datacenter-table-toggle');
    const datacenterModal = document.getElementById('datacenter-list-modal');
    const datacenterClose = document.getElementById('datacenter-list-close');
    const datacenterExportBtn = document.getElementById('datacenter-export-csv');
    const datacenterTbody = document.getElementById('datacenter-tbody');
    const datacenterFilteredCount = document.getElementById('datacenter-filtered-count');
    const datacenterTotalCount = document.getElementById('datacenter-total-count');
    
    // Function to populate data center table
    const populateDatacenterTable = () => {
      if (!datacenterTbody || !this.allDatacenters) return;
      
      // Clear existing rows
      datacenterTbody.innerHTML = '';
      
      // Get current filter from control panel
      const tierFilter = document.getElementById('datacenter-filter')?.value || 'all';
      
      // Filter datacenters
      let filtered = [...this.allDatacenters];
      if (tierFilter !== 'all') {
        // Extract the tier number from the filter value (e.g., "tier1" -> 1)
        const tierNum = parseInt(tierFilter.replace('tier', ''));
        filtered = filtered.filter(dc => dc.tier === tierNum);
      }
      
      // Update counts
      if (datacenterFilteredCount) datacenterFilteredCount.textContent = filtered.length;
      if (datacenterTotalCount) datacenterTotalCount.textContent = this.allDatacenters.length;
      
      // Create rows
      filtered.forEach(dc => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${dc.city || 'Unknown'}</td>
          <td>${dc.country || 'Unknown'}</td>
          <td><span class="tier-badge tier${dc.tier}">Tier ${dc.tier}</span></td>
          <td>${dc.provider || 'N/A'}</td>
          <td>${dc.latitude?.toFixed(4)}, ${dc.longitude?.toFixed(4)}</td>
          <td>${dc.name || 'DC'}</td>
          <td><span class="status-active">Active</span></td>
        `;
        datacenterTbody.appendChild(row);
      });
    };
    
    // Show data center modal
    datacenterTableToggle?.addEventListener('click', () => {
      if (datacenterModal) {
        datacenterModal.classList.remove('hidden');
        populateDatacenterTable();
      }
    });
    
    // Close data center modal
    datacenterClose?.addEventListener('click', () => {
      if (datacenterModal) {
        datacenterModal.classList.add('hidden');
      }
    });
    
    // Update table when filter changes (if modal is open)
    document.getElementById('datacenter-filter')?.addEventListener('change', () => {
      if (datacenterModal && !datacenterModal.classList.contains('hidden')) {
        populateDatacenterTable();
      }
    });
    
    // Export data centers to CSV
    datacenterExportBtn?.addEventListener('click', () => {
      // Get current filter
      const tierFilter = document.getElementById('datacenter-filter')?.value || 'all';
      let dataToExport = [...this.allDatacenters];
      
      // Apply filter
      if (tierFilter !== 'all') {
        const tierNum = parseInt(tierFilter.replace('tier', ''));
        dataToExport = dataToExport.filter(dc => dc.tier === tierNum);
      }
      
      const headers = ['City', 'Country', 'Tier', 'Provider', 'Latitude', 'Longitude', 'Name'];
      const rows = dataToExport.map(dc => [
        dc.city || 'Unknown',
        dc.country || 'Unknown',
        `Tier ${dc.tier}`,
        dc.provider || 'N/A',
        dc.latitude,
        dc.longitude,
        dc.name || 'DC'
      ]);
      
      let csv = headers.join(',') + '\n';
      rows.forEach(row => {
        csv += row.map(cell => `"${cell}"`).join(',') + '\n';
      });
      
      this.downloadCSV(csv, 'data_centers.csv');
    });

    // Panel collapse/expand functionality
    const panelToggle = document.getElementById('panel-toggle');
    const controlPanel = document.querySelector('.control-panel');
    
    panelToggle?.addEventListener('click', () => {
      if (controlPanel) {
        controlPanel.classList.toggle('collapsed');
        // Update tooltip text based on state
        if (controlPanel.classList.contains('collapsed')) {
          panelToggle.title = 'Show Panel';
        } else {
          panelToggle.title = 'Hide Panel';
        }
      }
    });
  }
  
  exportToCSV(cables) {
    const headers = ['Name', 'Capacity (Tbps)', 'Distance (km)', 'From', 'To', 'Status', 'Data Accuracy'];
    const rows = cables.map(cable => {
      const distance = this.calculateDistance(
        cable.landing_point_1.latitude,
        cable.landing_point_1.longitude,
        cable.landing_point_2.latitude,
        cable.landing_point_2.longitude
      );
      
      return [
        cable.name || 'Unknown',
        cable.capacity_tbps || 'N/A',
        Math.round(distance),
        cable.landing_point_1.location || `${cable.landing_point_1.latitude.toFixed(1)}°, ${cable.landing_point_1.longitude.toFixed(1)}°`,
        cable.landing_point_2.location || `${cable.landing_point_2.latitude.toFixed(1)}°, ${cable.landing_point_2.longitude.toFixed(1)}°`,
        cable.status || 'Active',
        cable.data_accuracy === 'live' ? 'Live' : 'Estimated'
      ];
    });
    
    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    
    return csvContent;
  }
  
  downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  
  setupMinimalControls() {
    // Data Tables functionality
    this.setupDataTables();
    
    // Setup info tooltips
    this.setupInfoTooltips();
    
    // Pause/Play rotation button
    const rotationToggle = document.getElementById('rotation-toggle');
    const playIcon = rotationToggle?.querySelector('.play-icon');
    const pauseIcon = rotationToggle?.querySelector('.pause-icon');
    
    rotationToggle?.addEventListener('click', () => {
      const controls = this.globe.controls();
      controls.autoRotate = !controls.autoRotate;
      
      // Force update to ensure rotation works
      controls.update();
      
      // Toggle icons
      if (controls.autoRotate) {
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
      } else {
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
      }
    });
    
    // Get current filters function
    const getCurrentFilters = () => ({
      accuracy: document.getElementById('cable-filter')?.value || 'all',
      region: document.getElementById('region-filter')?.value || 'all',
      capacity: document.getElementById('capacity-filter')?.value || 'all',
      majorOnly: document.getElementById('show-major-only')?.checked || false
    });
    
    // Apply filters function
    const applyFilters = () => {
      const filters = getCurrentFilters();
      console.log('Applying filters:', filters);
      this.renderCleanCables(this.allCables, filters);
      
      // Update stats
      const statsElement = document.getElementById('cable-count');
      if (statsElement) {
        const count = this.originalData.cables.length;
        const totalCables = this.allCables.length;
        statsElement.textContent = `${count}/${totalCables}`;
      }
    };
    
    // Cable filter controls
    document.getElementById('cable-filter')?.addEventListener('change', applyFilters);
    document.getElementById('region-filter')?.addEventListener('change', applyFilters);
    document.getElementById('capacity-filter')?.addEventListener('change', applyFilters);
    document.getElementById('show-major-only')?.addEventListener('change', applyFilters);
    
    // Only essential controls
    document.getElementById('toggle-cables')?.addEventListener('change', (e) => {
      if (e.target.checked) {
        console.log('Toggling cables ON, total cables:', this.allCables.length);
        // Respect current filters when toggling back on
        const filters = getCurrentFilters();
        this.renderCleanCables(this.allCables, filters);
      } else {
        console.log('Toggling cables OFF');
        // Clear arcs but preserve the data
        this.globe.arcsData([]);
        // Also update the stats to show 0
        const statsElement = document.getElementById('cable-count');
        if (statsElement) {
          statsElement.textContent = `0/${this.allCables.length}`;
        }
      }
    });
    
    // Data center controls
    const applyDatacenterFilter = () => {
      const isEnabled = document.getElementById('toggle-datacenters')?.checked;
      if (isEnabled) {
        const tierFilter = document.getElementById('datacenter-filter')?.value || 'all';
        this.renderMinimalDataCenters(this.allDatacenters, tierFilter);
      } else {
        this.globe.pointsData([]);
      }
    };
    
    document.getElementById('toggle-datacenters')?.addEventListener('change', applyDatacenterFilter);
    document.getElementById('datacenter-filter')?.addEventListener('change', applyDatacenterFilter);
    
    document.getElementById('toggle-atmosphere')?.addEventListener('change', (e) => {
      this.globe.showAtmosphere(e.target.checked);
    });
    
    
    const cableGlow = document.getElementById('cable-glow');
    if (cableGlow?.parentElement?.parentElement) cableGlow.parentElement.parentElement.style.display = 'none';
    
    const flowSpeed = document.getElementById('flow-speed');
    if (flowSpeed?.parentElement?.parentElement) flowSpeed.parentElement.parentElement.style.display = 'none';
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'r' || e.key === 'R') {
        this.globe.pointOfView({ lat: 20, lng: -40, altitude: 2.8 }, 1000);
      }
    });
    
    // Window resize
    window.addEventListener('resize', () => {
      this.globe.width(window.innerWidth);
      this.globe.height(window.innerHeight);
    });
  }
  
  updateLoadingStatus(message) {
    const status = document.querySelector('.loading-status');
    if (status) status.textContent = message;
  }
  
  hideLoadingScreen() {
    const screen = document.getElementById('loading-screen');
    if (screen) {
      setTimeout(() => {
        screen.style.opacity = '0';
        screen.style.transition = 'opacity 1s ease';
        setTimeout(() => {
          screen.style.display = 'none';
        }, 1000);
      }, 500);
    }
  }
  
  updateStats() {
    document.getElementById('cable-count').textContent = this.stats.cables;
    document.getElementById('datacenter-count').textContent = this.stats.datacenters;
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new CleanInfrastructureMap();
});

export default CleanInfrastructureMap;