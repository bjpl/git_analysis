/**
 * Graphs: Social Networks or City Maps
 * 
 * Just like social networks where people are connected to friends,
 * or city maps where locations are connected by roads, graphs represent
 * relationships between entities.
 */

class Person {
  constructor(name, interests = [], location = '') {
    this.name = name;
    this.interests = interests;
    this.location = location;
    this.friends = new Set(); // Adjacent nodes
    this.id = Math.random().toString(36).substr(2, 9);
  }

  /**
   * Add a friend (create edge)
   */
  addFriend(person) {
    this.friends.add(person);
    person.friends.add(this); // Undirected graph
    console.log(`🤝 ${this.name} and ${person.name} are now friends!`);
  }

  /**
   * Remove friendship (remove edge)
   */
  removeFriend(person) {
    this.friends.delete(person);
    person.friends.delete(this);
    console.log(`😔 ${this.name} and ${person.name} are no longer friends`);
  }

  /**
   * Check if two people are friends
   */
  isFriendWith(person) {
    return this.friends.has(person);
  }

  /**
   * Get number of friends (vertex degree)
   */
  getFriendCount() {
    return this.friends.size;
  }

  /**
   * Get mutual friends
   */
  getMutualFriends(person) {
    const mutual = [];
    for (const friend of this.friends) {
      if (person.friends.has(friend)) {
        mutual.push(friend);
      }
    }
    return mutual;
  }

  toString() {
    return `${this.name} (${this.interests.join(', ')})`;
  }
}

class SocialNetworkGraph {
  constructor(networkName = 'FriendBook') {
    this.people = new Map(); // Adjacency list representation
    this.networkName = networkName;
    this.totalConnections = 0;
  }

  /**
   * Add person to network (add vertex)
   * Time Complexity: O(1)
   */
  addPerson(name, interests = [], location = '') {
    if (this.people.has(name)) {
      console.log(`${name} is already in the network`);
      return false;
    }
    
    const person = new Person(name, interests, location);
    this.people.set(name, person);
    console.log(`👤 ${name} joined ${this.networkName}`);
    return true;
  }

  /**
   * Create friendship (add edge)
   * Time Complexity: O(1)
   */
  createFriendship(name1, name2) {
    const person1 = this.people.get(name1);
    const person2 = this.people.get(name2);
    
    if (!person1 || !person2) {
      console.log('One or both people not found in network');
      return false;
    }
    
    if (person1.isFriendWith(person2)) {
      console.log(`${name1} and ${name2} are already friends`);
      return false;
    }
    
    person1.addFriend(person2);
    this.totalConnections++;
    return true;
  }

  /**
   * Find shortest path between two people (BFS)
   * Time Complexity: O(V + E) where V = vertices, E = edges
   */
  findShortestPath(startName, endName) {
    const start = this.people.get(startName);
    const end = this.people.get(endName);
    
    if (!start || !end) {
      console.log('Person not found in network');
      return null;
    }
    
    if (start === end) {
      console.log(`${startName} is looking for themselves!`);
      return [start];
    }
    
    console.log(`🔍 Finding shortest path from ${startName} to ${endName}...`);
    
    const queue = [{ person: start, path: [start] }];
    const visited = new Set([start]);
    
    while (queue.length > 0) {
      const { person, path } = queue.shift();
      
      // Check each friend
      for (const friend of person.friends) {
        if (friend === end) {
          const completePath = [...path, friend];
          this.displayPath(completePath);
          return completePath;
        }
        
        if (!visited.has(friend)) {
          visited.add(friend);
          queue.push({ person: friend, path: [...path, friend] });
        }
      }
    }
    
    console.log(`❌ No connection found between ${startName} and ${endName}`);
    return null;
  }

  /**
   * Find all people within N degrees of separation
   * Time Complexity: O(V + E)
   */
  findPeopleWithinDegrees(personName, degrees) {
    const person = this.people.get(personName);
    if (!person) {
      console.log('Person not found');
      return [];
    }
    
    console.log(`🔍 Finding people within ${degrees} degrees of ${personName}:`);
    
    const result = [];
    const visited = new Set();
    const queue = [{ person, degree: 0 }];
    visited.add(person);
    
    while (queue.length > 0) {
      const { person: currentPerson, degree } = queue.shift();
      
      if (degree > 0) {
        result.push({ person: currentPerson, degree });
        console.log(`  ${degree}°: ${currentPerson.name}`);
      }
      
      if (degree < degrees) {
        for (const friend of currentPerson.friends) {
          if (!visited.has(friend)) {
            visited.add(friend);
            queue.push({ person: friend, degree: degree + 1 });
          }
        }
      }
    }
    
    console.log(`Found ${result.length} people within ${degrees} degrees`);
    return result;
  }

  /**
   * Find mutual friends between two people
   */
  findMutualFriends(name1, name2) {
    const person1 = this.people.get(name1);
    const person2 = this.people.get(name2);
    
    if (!person1 || !person2) {
      console.log('Person not found');
      return [];
    }
    
    const mutual = person1.getMutualFriends(person2);
    console.log(`🤝 Mutual friends between ${name1} and ${name2}:`);
    
    if (mutual.length === 0) {
      console.log('  No mutual friends found');
    } else {
      mutual.forEach(friend => {
        console.log(`  - ${friend.name}`);
      });
    }
    
    return mutual;
  }

  /**
   * Suggest friends based on mutual connections
   * Time Complexity: O(V * E)
   */
  suggestFriends(personName, maxSuggestions = 5) {
    const person = this.people.get(personName);
    if (!person) {
      console.log('Person not found');
      return [];
    }
    
    console.log(`👥 Friend suggestions for ${personName}:`);
    
    const suggestions = new Map(); // person -> mutual friend count
    
    // Check friends of friends
    for (const friend of person.friends) {
      for (const friendOfFriend of friend.friends) {
        if (friendOfFriend !== person && !person.isFriendWith(friendOfFriend)) {
          const count = suggestions.get(friendOfFriend) || 0;
          suggestions.set(friendOfFriend, count + 1);
        }
      }
    }
    
    // Sort by mutual friend count
    const sortedSuggestions = Array.from(suggestions.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxSuggestions);
    
    sortedSuggestions.forEach(([suggestedPerson, mutualCount]) => {
      const sharedInterests = person.interests.filter(interest => 
        suggestedPerson.interests.includes(interest)
      );
      
      console.log(`  👤 ${suggestedPerson.name} (${mutualCount} mutual friends)`);
      if (sharedInterests.length > 0) {
        console.log(`    Shared interests: ${sharedInterests.join(', ')}`);
      }
    });
    
    return sortedSuggestions.map(([person]) => person);
  }

  /**
   * Find influencers (people with most connections)
   */
  findInfluencers(topN = 3) {
    console.log(`🌟 Top ${topN} influencers in ${this.networkName}:`);
    
    const influencers = Array.from(this.people.values())
      .sort((a, b) => b.getFriendCount() - a.getFriendCount())
      .slice(0, topN);
    
    influencers.forEach((person, index) => {
      const medal = ['🥇', '🥈', '🥉'][index] || '🏅';
      console.log(`${medal} ${person.name}: ${person.getFriendCount()} friends`);
    });
    
    return influencers;
  }

  /**
   * Detect communities using DFS
   * Time Complexity: O(V + E)
   */
  findCommunities() {
    console.log(`🏠 Finding communities in ${this.networkName}:`);
    
    const visited = new Set();
    const communities = [];
    
    for (const person of this.people.values()) {
      if (!visited.has(person)) {
        const community = [];
        this.dfsExplore(person, visited, community);
        communities.push(community);
      }
    }
    
    communities.forEach((community, index) => {
      console.log(`\n  Community ${index + 1} (${community.length} people):`);
      community.forEach(person => {
        console.log(`    - ${person.name} (${person.getFriendCount()} friends)`);
      });
    });
    
    return communities;
  }

  /**
   * DFS helper for community detection
   */
  dfsExplore(person, visited, community) {
    visited.add(person);
    community.push(person);
    
    for (const friend of person.friends) {
      if (!visited.has(friend)) {
        this.dfsExplore(friend, visited, community);
      }
    }
  }

  /**
   * Display network statistics
   */
  displayNetworkStats() {
    console.log(`\n📊 ${this.networkName} Network Statistics:`);
    console.log(`Total people: ${this.people.size}`);
    console.log(`Total friendships: ${this.totalConnections}`);
    
    if (this.people.size > 0) {
      const avgConnections = (this.totalConnections * 2) / this.people.size;
      console.log(`Average friends per person: ${avgConnections.toFixed(1)}`);
      
      // Calculate network density
      const maxPossibleConnections = (this.people.size * (this.people.size - 1)) / 2;
      const density = (this.totalConnections / maxPossibleConnections * 100).toFixed(1);
      console.log(`Network density: ${density}%`);
    }
  }

  /**
   * Display visual representation of the network
   */
  displayNetwork() {
    console.log(`\n🌐 ${this.networkName} Social Network:`);
    
    for (const person of this.people.values()) {
      const friendNames = Array.from(person.friends).map(f => f.name);
      console.log(`${person.name}: [👥 ${friendNames.join(', ')}] (${person.getFriendCount()} friends)`);
    }
  }

  /**
   * Helper method to display path
   */
  displayPath(path) {
    console.log('\n🛵️  Path found:');
    const pathString = path.map((person, index) => {
      const arrow = index < path.length - 1 ? ' → ' : '';
      return person.name + arrow;
    }).join('');
    
    console.log(`  ${pathString}`);
    console.log(`  Path length: ${path.length - 1} degrees of separation`);
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Graphs:\n\n` +
      `1. 🗺️  GPS Navigation: Roads and intersections\n` +
      `2. 🌐 Internet: Web pages and hyperlinks\n` +
      `3. 📶 Network Topology: Routers and connections\n` +
      `4. 🧬 DNA Analysis: Genetic relationships\n` +
      `5. 🎨 Dependency Graphs: Software modules\n` +
      `6. 💰 Financial Networks: Transaction flows\n` +
      `7. 🎥 Recommendation Systems: User preferences\n`);
  }
}

/**
 * City Map Graph: Weighted Directed Graph
 */
class CityMapGraph {
  constructor(cityName = 'Metro City') {
    this.locations = new Map();
    this.cityName = cityName;
  }

  /**
   * Add location to map
   */
  addLocation(name, type = 'general') {
    if (this.locations.has(name)) {
      console.log(`${name} already exists on the map`);
      return false;
    }
    
    this.locations.set(name, {
      name,
      type,
      connections: new Map() // destination -> { distance, time, traffic }
    });
    
    console.log(`📍 Added ${name} (${type}) to ${this.cityName} map`);
    return true;
  }

  /**
   * Add road between locations (weighted edge)
   */
  addRoad(from, to, distance, time, traffic = 'normal') {
    const fromLocation = this.locations.get(from);
    const toLocation = this.locations.get(to);
    
    if (!fromLocation || !toLocation) {
      console.log('Location not found on map');
      return false;
    }
    
    fromLocation.connections.set(to, { distance, time, traffic });
    console.log(`🛵️  Added road from ${from} to ${to} (${distance}km, ${time}min)`);
    return true;
  }

  /**
   * Find shortest route using Dijkstra's algorithm
   * Time Complexity: O((V + E) log V) with priority queue
   */
  findShortestRoute(start, destination, metric = 'distance') {
    console.log(`🗺️  Finding shortest route from ${start} to ${destination} by ${metric}:`);
    
    if (!this.locations.has(start) || !this.locations.has(destination)) {
      console.log('Location not found');
      return null;
    }
    
    const distances = new Map();
    const previous = new Map();
    const unvisited = new Set();
    
    // Initialize distances
    for (const location of this.locations.keys()) {
      distances.set(location, location === start ? 0 : Infinity);
      unvisited.add(location);
    }
    
    while (unvisited.size > 0) {
      // Find unvisited location with minimum distance
      let current = null;
      let minDistance = Infinity;
      
      for (const location of unvisited) {
        if (distances.get(location) < minDistance) {
          minDistance = distances.get(location);
          current = location;
        }
      }
      
      if (current === null || minDistance === Infinity) {
        break; // No more reachable locations
      }
      
      unvisited.delete(current);
      
      if (current === destination) {
        break; // Found shortest path to destination
      }
      
      // Update distances to neighbors
      const currentLocation = this.locations.get(current);
      for (const [neighbor, road] of currentLocation.connections) {
        if (unvisited.has(neighbor)) {
          const weight = metric === 'time' ? road.time : road.distance;
          const newDistance = distances.get(current) + weight;
          
          if (newDistance < distances.get(neighbor)) {
            distances.set(neighbor, newDistance);
            previous.set(neighbor, current);
          }
        }
      }
    }
    
    // Reconstruct path
    const path = [];
    let current = destination;
    
    while (current !== undefined) {
      path.unshift(current);
      current = previous.get(current);
    }
    
    if (path[0] !== start) {
      console.log(`No route found from ${start} to ${destination}`);
      return null;
    }
    
    const totalDistance = distances.get(destination);
    console.log(`\n✅ Route found:`);
    console.log(`  Path: ${path.join(' → ')}`);
    console.log(`  Total ${metric}: ${totalDistance}${metric === 'time' ? ' minutes' : ' km'}`);
    
    return { path, totalDistance, metric };
  }

  /**
   * Find all routes within a certain distance/time
   */
  findRoutesWithin(start, maxLimit, metric = 'distance') {
    console.log(`🔍 Finding all locations within ${maxLimit}${metric === 'time' ? ' minutes' : ' km'} of ${start}:`);
    
    const reachable = new Map();
    const queue = [{ location: start, totalCost: 0, path: [start] }];
    const visited = new Set();
    
    while (queue.length > 0) {
      const { location, totalCost, path } = queue.shift();
      
      if (visited.has(location)) continue;
      visited.add(location);
      
      if (location !== start) {
        reachable.set(location, { cost: totalCost, path });
        console.log(`  ${location}: ${totalCost}${metric === 'time' ? 'min' : 'km'} via ${path.join(' → ')}`);
      }
      
      const currentLocation = this.locations.get(location);
      for (const [neighbor, road] of currentLocation.connections) {
        const weight = metric === 'time' ? road.time : road.distance;
        const newCost = totalCost + weight;
        
        if (newCost <= maxLimit && !visited.has(neighbor)) {
          queue.push({
            location: neighbor,
            totalCost: newCost,
            path: [...path, neighbor]
          });
        }
      }
    }
    
    console.log(`Found ${reachable.size} reachable locations`);
    return reachable;
  }

  /**
   * Display city map
   */
  displayMap() {
    console.log(`\n🏢 ${this.cityName} Map:`);
    
    for (const [name, location] of this.locations) {
      console.log(`\n📍 ${name} (${location.type}):`);
      
      if (location.connections.size === 0) {
        console.log('  No outgoing roads');
      } else {
        for (const [destination, road] of location.connections) {
          const trafficEmoji = road.traffic === 'heavy' ? '🔴' : 
                              road.traffic === 'moderate' ? '🟡' : '🟢';
          console.log(`  → ${destination}: ${road.distance}km, ${road.time}min ${trafficEmoji}`);
        }
      }
    }
  }
}

/**
 * Graph Practice Problems
 */
class GraphPracticeProblems {
  /**
   * Problem 1: Detect cycle in social network
   * Check if there's a cycle in friendships
   */
  static detectCycle(graph) {
    console.log('🔄 Detecting cycles in social network...');
    
    const visited = new Set();
    const recursionStack = new Set();
    
    const dfs = (person, parent) => {
      visited.add(person);
      recursionStack.add(person);
      
      for (const friend of person.friends) {
        if (friend === parent) continue; // Skip parent in undirected graph
        
        if (recursionStack.has(friend)) {
          console.log(`✅ Cycle detected involving ${person.name} and ${friend.name}`);
          return true;
        }
        
        if (!visited.has(friend) && dfs(friend, person)) {
          return true;
        }
      }
      
      recursionStack.delete(person);
      return false;
    };
    
    for (const person of graph.people.values()) {
      if (!visited.has(person)) {
        if (dfs(person, null)) {
          return true;
        }
      }
    }
    
    console.log('❌ No cycles detected');
    return false;
  }

  /**
   * Problem 2: Find articulation points (critical connections)
   * People whose removal would disconnect the network
   */
  static findArticulationPoints(graph) {
    console.log('🔍 Finding critical people in network...');
    
    const visited = new Set();
    const articulationPoints = new Set();
    const discovery = new Map();
    const low = new Map();
    const parent = new Map();
    let time = 0;
    
    const dfs = (person) => {
      let children = 0;
      visited.add(person);
      discovery.set(person, time);
      low.set(person, time);
      time++;
      
      for (const friend of person.friends) {
        if (!visited.has(friend)) {
          children++;
          parent.set(friend, person);
          dfs(friend);
          
          low.set(person, Math.min(low.get(person), low.get(friend)));
          
          // Check articulation point conditions
          if (!parent.has(person) && children > 1) {
            articulationPoints.add(person);
          }
          
          if (parent.has(person) && low.get(friend) >= discovery.get(person)) {
            articulationPoints.add(person);
          }
        } else if (friend !== parent.get(person)) {
          low.set(person, Math.min(low.get(person), discovery.get(friend)));
        }
      }
    };
    
    for (const person of graph.people.values()) {
      if (!visited.has(person)) {
        dfs(person);
      }
    }
    
    console.log('Critical people (articulation points):');
    if (articulationPoints.size === 0) {
      console.log('  None found - network is well connected');
    } else {
      for (const person of articulationPoints) {
        console.log(`  ⚠️  ${person.name} - removing would disconnect parts of the network`);
      }
    }
    
    return Array.from(articulationPoints);
  }

  /**
   * Problem 3: Graph coloring (schedule meetings without conflicts)
   * Color vertices so no adjacent vertices have same color
   */
  static colorGraph(graph, colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple']) {
    console.log('🎨 Coloring social network (scheduling non-conflicting meetings)...');
    
    const coloring = new Map();
    const people = Array.from(graph.people.values());
    
    // Sort by degree (most connected first) - greedy approach
    people.sort((a, b) => b.getFriendCount() - a.getFriendCount());
    
    for (const person of people) {
      const usedColors = new Set();
      
      // Find colors used by friends
      for (const friend of person.friends) {
        if (coloring.has(friend)) {
          usedColors.add(coloring.get(friend));
        }
      }
      
      // Assign first available color
      for (const color of colors) {
        if (!usedColors.has(color)) {
          coloring.set(person, color);
          console.log(`  ${person.name}: ${color}`);
          break;
        }
      }
    }
    
    const colorsUsed = new Set(coloring.values()).size;
    console.log(`\nUsed ${colorsUsed} colors (time slots) for ${people.length} people`);
    
    return coloring;
  }

  /**
   * Problem 4: Find bridges (critical connections)
   * Friendships whose removal would increase connected components
   */
  static findBridges(graph) {
    console.log('🌉 Finding bridge connections in network...');
    
    const visited = new Set();
    const bridges = [];
    const discovery = new Map();
    const low = new Map();
    const parent = new Map();
    let time = 0;
    
    const dfs = (person) => {
      visited.add(person);
      discovery.set(person, time);
      low.set(person, time);
      time++;
      
      for (const friend of person.friends) {
        if (!visited.has(friend)) {
          parent.set(friend, person);
          dfs(friend);
          
          low.set(person, Math.min(low.get(person), low.get(friend)));
          
          // Check bridge condition
          if (low.get(friend) > discovery.get(person)) {
            bridges.push([person, friend]);
          }
        } else if (friend !== parent.get(person)) {
          low.set(person, Math.min(low.get(person), discovery.get(friend)));
        }
      }
    };
    
    for (const person of graph.people.values()) {
      if (!visited.has(person)) {
        dfs(person);
      }
    }
    
    console.log('Bridge connections (critical friendships):');
    if (bridges.length === 0) {
      console.log('  No bridges found - network has good redundancy');
    } else {
      bridges.forEach(([person1, person2]) => {
        console.log(`  🌉 ${person1.name} ↔ ${person2.name} - critical connection`);
      });
    }
    
    return bridges;
  }
}

// Export for use in other modules
export { 
  Person, 
  SocialNetworkGraph, 
  CityMapGraph, 
  GraphPracticeProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🌐 Welcome to the Social Network Graph Learning Module!\n');
  
  // Create social network
  const socialNetwork = new SocialNetworkGraph('TechConnect');
  
  // Add people to network
  console.log('👥 Building social network:');
  socialNetwork.addPerson('Alice', ['coding', 'gaming', 'music'], 'Seattle');
  socialNetwork.addPerson('Bob', ['gaming', 'sports', 'movies'], 'Portland');
  socialNetwork.addPerson('Charlie', ['music', 'art', 'travel'], 'San Francisco');
  socialNetwork.addPerson('Diana', ['coding', 'reading', 'hiking'], 'Seattle');
  socialNetwork.addPerson('Eve', ['art', 'photography', 'travel'], 'Los Angeles');
  socialNetwork.addPerson('Frank', ['sports', 'fitness', 'movies'], 'Portland');
  socialNetwork.addPerson('Grace', ['coding', 'music', 'hiking'], 'Seattle');
  
  // Create friendships
  console.log('\n🤝 Creating friendships:');
  socialNetwork.createFriendship('Alice', 'Bob');
  socialNetwork.createFriendship('Alice', 'Diana');
  socialNetwork.createFriendship('Bob', 'Charlie');
  socialNetwork.createFriendship('Charlie', 'Eve');
  socialNetwork.createFriendship('Diana', 'Grace');
  socialNetwork.createFriendship('Frank', 'Bob');
  socialNetwork.createFriendship('Grace', 'Alice');
  socialNetwork.createFriendship('Eve', 'Frank');
  
  // Display network
  socialNetwork.displayNetwork();
  socialNetwork.displayNetworkStats();
  
  // Find shortest path
  console.log('\n🔍 Path finding:');
  socialNetwork.findShortestPath('Alice', 'Eve');
  socialNetwork.findShortestPath('Diana', 'Frank');
  
  // Find people within degrees
  console.log('\n🌐 Degrees of separation:');
  socialNetwork.findPeopleWithinDegrees('Alice', 2);
  
  // Find mutual friends
  console.log('\n🤝 Mutual friends:');
  socialNetwork.findMutualFriends('Alice', 'Charlie');
  
  // Friend suggestions
  console.log('\n👥 Friend suggestions:');
  socialNetwork.suggestFriends('Alice');
  
  // Find influencers
  socialNetwork.findInfluencers();
  
  // Detect communities
  socialNetwork.findCommunities();
  
  // City map demonstration
  console.log('\n\n🗺️  City Map Graph Demo:');
  const cityMap = new CityMapGraph('Metro City');
  
  // Add locations
  cityMap.addLocation('Downtown', 'business');
  cityMap.addLocation('Airport', 'transport');
  cityMap.addLocation('University', 'education');
  cityMap.addLocation('Mall', 'shopping');
  cityMap.addLocation('Hospital', 'medical');
  cityMap.addLocation('Park', 'recreation');
  
  // Add roads
  cityMap.addRoad('Downtown', 'Airport', 15, 20, 'moderate');
  cityMap.addRoad('Downtown', 'University', 5, 8, 'normal');
  cityMap.addRoad('Downtown', 'Mall', 3, 5, 'normal');
  cityMap.addRoad('University', 'Park', 2, 3, 'normal');
  cityMap.addRoad('Mall', 'Hospital', 4, 7, 'normal');
  cityMap.addRoad('Airport', 'Hospital', 12, 18, 'heavy');
  cityMap.addRoad('Park', 'Mall', 6, 10, 'normal');
  
  cityMap.displayMap();
  
  // Find shortest routes
  console.log('\n🛵️  Route planning:');
  cityMap.findShortestRoute('University', 'Airport', 'distance');
  cityMap.findShortestRoute('University', 'Airport', 'time');
  
  // Find locations within range
  console.log('\n🔍 Nearby locations:');
  cityMap.findRoutesWithin('Downtown', 10, 'distance');
  
  // Show real-world applications
  SocialNetworkGraph.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Graph Practice Problems:');
  
  console.log('\n1. Cycle Detection:');
  GraphPracticeProblems.detectCycle(socialNetwork);
  
  console.log('\n2. Articulation Points:');
  GraphPracticeProblems.findArticulationPoints(socialNetwork);
  
  console.log('\n3. Graph Coloring:');
  GraphPracticeProblems.colorGraph(socialNetwork);
  
  console.log('\n4. Bridge Detection:');
  GraphPracticeProblems.findBridges(socialNetwork);
}