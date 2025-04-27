import { NextRequest, NextResponse } from 'next/server';
import type { Driver, QueryResult } from 'neo4j-driver';
import neo4j from 'neo4j-driver';
import { NEO4J_CONFIG } from '@/lib/neo4j';

// Create a Neo4j driver instance
let driver: Driver | null = null;

try {
  driver = neo4j.driver(
    NEO4J_CONFIG.uri, 
    neo4j.auth.basic(NEO4J_CONFIG.user, NEO4J_CONFIG.password)
  );
} catch (error) {
  console.error('Error initializing Neo4j driver:', error);
}

export async function POST(request: NextRequest) {
  try {
    // Ensure driver is initialized
    if (!driver) {
      return NextResponse.json(
        { error: 'Neo4j driver not initialized' },
        { status: 500 }
      );
    }

    // Parse request body
    const body = await request.json();
    const { query } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // Open a session
    const session = driver.session();
    
    try {
      // Execute the Cypher query
      const result = await session.run(query);
      
      // Process the results into a format suitable for force-graph
      const graphData = processNeo4jResult(result);
      
      return NextResponse.json(graphData);
    } finally {
      // Close session
      await session.close();
    }
  } catch (error: any) {
    console.error('Error executing Neo4j query:', error);
    return NextResponse.json(
      { error: error.message || 'An error occurred while querying Neo4j' },
      { status: 500 }
    );
  }
}

// Process Neo4j result into a format suitable for force-graph
function processNeo4jResult(result: QueryResult) {
  const nodes = new Map();
  const links: any[] = [];
  
  result.records.forEach((record: any) => {
    // Process nodes
    if (record.has('n')) {
      const node = record.get('n');
      if (node && !nodes.has(node.elementId)) {
        // Get node properties
        const props = node.properties;
        
        // Determine node type from labels
        const nodeType = node.labels && node.labels.length > 0 ? node.labels[0] : 'Unknown';
        
        // Get node color based on type
        const nodeColor = getNodeColor(nodeType);
        
        // Add node to the map
        nodes.set(node.elementId, {
          id: node.elementId,
          name: props.name || props.title || props.id || `Node ${node.elementId}`,
          type: nodeType,
          color: nodeColor,
          val: getNodeSize(nodeType),
          properties: props
        });
      }
    }
    
    // Process target nodes
    if (record.has('m')) {
      const node = record.get('m');
      if (node && !nodes.has(node.elementId)) {
        // Get node properties
        const props = node.properties;
        
        // Determine node type from labels
        const nodeType = node.labels && node.labels.length > 0 ? node.labels[0] : 'Unknown';
        
        // Get node color based on type
        const nodeColor = getNodeColor(nodeType);
        
        // Add node to the map
        nodes.set(node.elementId, {
          id: node.elementId,
          name: props.name || props.title || props.id || `Node ${node.elementId}`,
          type: nodeType,
          color: nodeColor,
          val: getNodeSize(nodeType),
          properties: props
        });
      }
    }
    
    // Process relationships
    if (record.has('r')) {
      const rel = record.get('r');
      if (rel) {
        try {
          // Extract start and end node IDs - handle different Neo4j driver versions
          let sourceId, targetId;
          
          // Try different property names that might exist in different Neo4j driver versions
          if (rel.startNodeElementId !== undefined) {
            sourceId = rel.startNodeElementId;
            targetId = rel.endNodeElementId;
          } else if (rel.startNodeIdentity !== undefined) {
            sourceId = rel.startNodeIdentity.toString();
            targetId = rel.endNodeIdentity.toString();
          } else if (rel.start !== undefined) {
            sourceId = rel.start.toString();
            targetId = rel.end.toString();
          } else {
            console.log('Relationship structure:', rel);
            throw new Error('Could not determine relationship endpoints');
          }
          
          if (sourceId && targetId) {
            links.push({
              source: sourceId,
              target: targetId,
              label: rel.type,
              value: 1,
              properties: rel.properties
            });
          }
        } catch (err) {
          console.error('Error processing relationship:', err, rel);
        }
      }
    }
  });
  
  return {
    nodes: Array.from(nodes.values()),
    links: links
  };
}

// Get node color based on type
function getNodeColor(type: string): string {
  const typeColorMap: Record<string, string> = {
    'User': '#4285F4',
    'PullRequest': '#EA4335',
    'Issue': '#FBBC05',
    'Message': '#34A853',
    'Commit': '#DB4437',
    'Repository': '#0F9D58',
    'File': '#673AB7',
    'Person': '#2196F3',
    'Project': '#FF9800',
    'Task': '#795548'
  };
  
  return typeColorMap[type] || '#666666';
}

// Get node size based on type
function getNodeSize(type: string): number {
  const typeSizeMap: Record<string, number> = {
    'User': 20,
    'Person': 20,
    'PullRequest': 15,
    'Issue': 12,
    'Message': 10,
    'Commit': 8,
    'Repository': 25,
    'File': 10,
    'Project': 22,
    'Task': 15
  };
  
  return typeSizeMap[type] || 10;
} 