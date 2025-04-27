"use client";

import React, { useEffect, useState, useRef, Suspense } from 'react';
import axios from 'axios';
// Remove direct import of ForceGraph2D
// import ForceGraph2D from 'react-force-graph-2d';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph2D with no SSR
const ForceGraph2D = dynamic(
  () => import('react-force-graph-2d'),
  { ssr: false }
);

interface Node {
  id: string;
  name: string;
  val: number;
  type: string;
  color?: string;
  properties?: Record<string, any>;
}

interface Link {
  source: string;
  target: string;
  value: number;
  label: string;
  properties?: Record<string, any>;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function GraphPage() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [responseDebug, setResponseDebug] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // Function to fetch graph data from Neo4j
  const fetchGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      setResponseDebug(null);
      
      // Create a simpler query that's more likely to work with any Neo4j database
      const response = await axios.post('/api/neo4j', {
        query: `
          // Limit to first 100 nodes for performance
          MATCH (n) 
          WITH n LIMIT 100
          OPTIONAL MATCH (n)-[r]->(m)
          RETURN n, r, m
        `
      });
      
      console.log("API Response:", response.data);
      
      if (response.data && Array.isArray(response.data.nodes)) {
        setGraphData(response.data);
        setResponseDebug(`Found ${response.data.nodes.length} nodes and ${response.data.links.length} relationships`);
      } else {
        setError("Unexpected response format from API");
        setResponseDebug(JSON.stringify(response.data, null, 2));
        
        // Fallback to mock data if API doesn't return expected format
        const mockData = {
          nodes: [
            { id: "user-1", name: "Daniel Kim", val: 20, type: "User", color: "#4285F4" },
            { id: "PR-1", name: "Add OAuth2 integration", val: 15, type: "PullRequest", color: "#EA4335" },
            { id: "PR-2", name: "Fix authentication bug", val: 15, type: "PullRequest", color: "#EA4335" },
            { id: "user-2", name: "Alex Smith", val: 20, type: "User", color: "#4285F4" },
            { id: "PR-3", name: "Add user profile page", val: 15, type: "PullRequest", color: "#EA4335" },
            { id: "Issue-1", name: "Login not working", val: 10, type: "Issue", color: "#FBBC05" },
            { id: "Issue-2", name: "Add dark mode", val: 10, type: "Issue", color: "#FBBC05" },
            { id: "Message-1", name: "Weekly update", val: 5, type: "Message", color: "#34A853" },
          ],
          links: [
            { source: "user-1", target: "PR-1", value: 1, label: "authored" },
            { source: "user-1", target: "PR-2", value: 1, label: "authored" },
            { source: "user-2", target: "PR-3", value: 1, label: "authored" },
            { source: "user-2", target: "Issue-1", value: 1, label: "opened" },
            { source: "user-1", target: "Issue-2", value: 1, label: "opened" },
            { source: "user-1", target: "Message-1", value: 1, label: "sent" },
            { source: "PR-1", target: "Issue-1", value: 1, label: "resolves" },
          ]
        };
        
        setGraphData(mockData);
      }
    } catch (error: any) {
      console.error("Error fetching graph data:", error);
      setError(`Failed to load graph data: ${error.message}`);
      setResponseDebug(error.response?.data ? JSON.stringify(error.response.data, null, 2) : null);
      
      // Fallback to minimal mock data on error
      const mockData = {
        nodes: [
          { id: "user-1", name: "Daniel Kim", val: 20, type: "User", color: "#4285F4" },
          { id: "PR-1", name: "Add OAuth2 integration", val: 15, type: "PullRequest", color: "#EA4335" }
        ],
        links: [
          { source: "user-1", target: "PR-1", value: 1, label: "authored" }
        ]
      };
      
      setGraphData(mockData);
    } finally {
      setLoading(false);
    }
  };

  // Set dimensions on mount and window resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: window.innerHeight - 70 // Full height minus some space for padding
        });
      }
    };

    // Only attach event listener on client side
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', updateDimensions);
      updateDimensions();
      
      return () => window.removeEventListener('resize', updateDimensions);
    }
  }, []);

  // Fetch data on mount
  useEffect(() => {
    fetchGraphData();
  }, []);

  // Node custom rendering
  const nodeCanvasObject = (node: any, ctx: any, globalScale: number) => {
    const label = node.name || node.id;
    const fontSize = 16/globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    const textWidth = ctx.measureText(label).width;
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.8);

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.val || 10, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color || getNodeColor(node.type || 'Unknown');
    ctx.fill();

    // Draw text background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillRect(
      node.x - bckgDimensions[0] / 2,
      node.y + (node.val || 10) + 2,
      bckgDimensions[0],
      bckgDimensions[1]
    );

    // Draw text
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#000';
    ctx.fillText(
      label,
      node.x,
      node.y + (node.val || 10) + 2 + bckgDimensions[1] / 2
    );
  };

  // Get color based on node type
  const getNodeColor = (type: string): string => {
    const typeColorMap: Record<string, string> = {
      'User': '#4285F4',
      'PullRequest': '#EA4335',
      'Issue': '#FBBC05',
      'Message': '#34A853',
      'Commit': '#DB4437',
      'Repository': '#0F9D58'
    };
    
    return typeColorMap[type] || '#666666';
  };

  return (
    <div className="w-full" ref={containerRef}>
      <h1 className="text-2xl font-bold p-4 text-center text-[#000D3D]">Code Repository Graph Visualization</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mx-4 mb-4">
          <p>{error}</p>
        </div>
      )}
      
     
      
      <div className="px-4 mb-4">
        <p className="text-sm text-gray-600">
          Connected to Neo4j at: localhost:7474 (HTTP) / 7687 (Bolt)
        </p>
        <button 
          onClick={fetchGraphData}
          className="mt-2 bg-[#000D3D] text-white px-4 py-2 rounded hover:bg-opacity-90"
        >
          Refresh Data
        </button>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-[70vh]">
          <div 
            className="animate-pulse"
            style={{
              borderRadius: "100px",
              background: "#EFEFEF",
              width: "300px",
              height: "10px",
              flexShrink: 0
            }}
          ></div>
        </div>
      ) : (
        <div className="graph-container" style={{ height: dimensions.height || 600, width: '100%' }}>
          <Suspense fallback={<div>Loading graph visualization...</div>}>
            <ForceGraph2D
              graphData={graphData}
              nodeCanvasObject={nodeCanvasObject}
              linkDirectionalArrowLength={3.5}
              linkDirectionalArrowRelPos={1}
              linkCurvature={0.25}
              linkLabel="label"
              nodeRelSize={6}
              nodeId="id"
              width={dimensions.width || 800}
              height={dimensions.height || 600}
              cooldownTime={2000}
              backgroundColor="#ffffff"
              onNodeClick={(node) => {
                console.log('Node clicked:', node);
                // Could add a modal or sidebar to show node details
              }}
            />
          </Suspense>
        </div>
      )}
    </div>
  );
} 