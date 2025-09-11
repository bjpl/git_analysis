import * as THREE from 'three';

export class CableRenderer {
  constructor(globe) {
    this.globe = globe;
    this.cableGroup = new THREE.Group();
    this.cableGroup.name = 'submarine-cables';
  }

  renderCables(cables) {
    // Clear existing cables
    this.clear();
    
    // Get the globe radius (globe.gl uses 100 by default)
    const globeRadius = 100;
    
    cables.forEach(cable => {
      const material = new THREE.LineBasicMaterial({
        color: this.getColorForCable(cable),
        linewidth: 1,
        opacity: 0.8,
        transparent: true
      });

      // Create a curve that follows the surface of the sphere
      const curve = this.createSurfaceCurve(
        cable.landing_point_1.latitude,
        cable.landing_point_1.longitude,
        cable.landing_point_2.latitude,
        cable.landing_point_2.longitude,
        globeRadius
      );

      // Use more points for longer cables to ensure smooth curves
      const distance = this.calculateDistance(
        cable.landing_point_1.latitude,
        cable.landing_point_1.longitude,
        cable.landing_point_2.latitude,
        cable.landing_point_2.longitude
      );
      const numPoints = distance > 10000 ? 100 : distance > 5000 ? 75 : 50;
      const points = curve.getPoints(numPoints);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, material);
      
      // Store cable data for interaction
      line.userData = cable;
      
      this.cableGroup.add(line);
    });

    // Add to scene
    this.globe.scene().add(this.cableGroup);
  }

  createSurfaceCurve(lat1, lng1, lat2, lng2, radius) {
    // Globe.gl coordinate system: Y-up, with equator on XZ plane
    // Longitude 0 is on the -Z axis, increasing eastward (counterclockwise from above)
    const phi1 = (90 - lat1) * Math.PI / 180; // Colatitude for point 1
    const lambda1 = lng1 * Math.PI / 180; // Longitude for point 1
    const phi2 = (90 - lat2) * Math.PI / 180; // Colatitude for point 2
    const lambda2 = lng2 * Math.PI / 180; // Longitude for point 2

    // Standard spherical to cartesian conversion (Y-up)
    const start = new THREE.Vector3(
      radius * Math.sin(phi1) * Math.sin(lambda1),  // X
      radius * Math.cos(phi1),                       // Y (up)
      -radius * Math.sin(phi1) * Math.cos(lambda1)   // Z
    );

    const end = new THREE.Vector3(
      radius * Math.sin(phi2) * Math.sin(lambda2),  // X
      radius * Math.cos(phi2),                       // Y (up)
      -radius * Math.sin(phi2) * Math.cos(lambda2)   // Z
    );

    // Calculate great circle distance to determine arc height
    const distance = this.calculateDistance(lat1, lng1, lat2, lng2);
    
    // Create a curve that follows the surface with elevation for long cables
    // We'll use a custom curve that interpolates along the great circle with altitude
    class GreatCircleArcCurve extends THREE.Curve {
      constructor(v1, v2, radius, distance) {
        super();
        this.v1 = v1.normalize();
        this.v2 = v2.normalize();
        this.radius = radius;
        this.distance = distance;
        
        // Calculate the angle between vectors
        this.angle = Math.acos(Math.min(1, Math.max(-1, this.v1.dot(this.v2))));
        
        // Calculate arc height based on distance for better visibility
        if (distance > 15000) {
          this.arcHeight = radius * 0.5; // 50% of radius for ultra-long cables
        } else if (distance > 10000) {
          this.arcHeight = radius * 0.35;
        } else if (distance > 5000) {
          this.arcHeight = radius * 0.25;
        } else if (distance > 2000) {
          this.arcHeight = radius * 0.15;
        } else {
          this.arcHeight = radius * 0.08;
        }
      }

      getPoint(t) {
        // Spherical interpolation (slerp) with arc elevation
        const sinAngle = Math.sin(this.angle);
        
        if (sinAngle < 0.001) {
          // Vectors are too close, use linear interpolation
          return this.v1.clone().multiplyScalar(this.radius);
        }
        
        const a = Math.sin((1 - t) * this.angle) / sinAngle;
        const b = Math.sin(t * this.angle) / sinAngle;
        
        const result = new THREE.Vector3();
        result.x = a * this.v1.x + b * this.v2.x;
        result.y = a * this.v1.y + b * this.v2.y;
        result.z = a * this.v1.z + b * this.v2.z;
        
        // Normalize and apply radius
        result.normalize();
        
        // Add arc elevation based on position along the curve
        // Maximum elevation at the midpoint (t = 0.5)
        const elevationFactor = Math.sin(t * Math.PI); // Creates a smooth arc
        const currentRadius = this.radius + (this.arcHeight * elevationFactor);
        
        return result.multiplyScalar(currentRadius);
      }
    }

    return new GreatCircleArcCurve(start, end, radius, distance);
  }
  
  calculateDistance(lat1, lng1, lat2, lng2) {
    // Haversine formula for great circle distance
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  getColorForCable(cable) {
    const capacity = cable.capacity_tbps || 50;
    
    if (capacity > 150) {
      return 0x00ffcc; // Cyan
    } else if (capacity >= 50) {
      return 0xffcc00; // Gold
    } else {
      return 0xff00ff; // Magenta
    }
  }

  clear() {
    // Remove from scene
    if (this.cableGroup.parent) {
      this.cableGroup.parent.remove(this.cableGroup);
    }
    
    // Clear the group
    while (this.cableGroup.children.length > 0) {
      const child = this.cableGroup.children[0];
      if (child.geometry) child.geometry.dispose();
      if (child.material) child.material.dispose();
      this.cableGroup.remove(child);
    }
  }
}