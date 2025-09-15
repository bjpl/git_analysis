import React, { useState, useCallback, useRef } from 'react';
import { DataStructureNode } from '../types/learning-types';
import { DragDropProvider, useDrag, useDrop } from '../utils/drag-drop';
import { NodeRenderer } from './NodeRenderer';
import { ToolPalette } from './ToolPalette';

interface DataStructureBuilderProps {
  type: 'tree' | 'graph' | 'list' | 'stack' | 'queue';
  onStructureChange?: (structure: DataStructureNode[]) => void;
  onValidate?: (structure: DataStructureNode[]) => boolean;
}

export const DataStructureBuilder: React.FC<DataStructureBuilderProps> = ({
  type,
  onStructureChange,
  onValidate
}) => {
  const [nodes, setNodes] = useState<DataStructureNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [mode, setMode] = useState<'build' | 'connect' | 'edit'>('build');
  const [draggedNode, setDraggedNode] = useState<DataStructureNode | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  const handleAddNode = useCallback((nodeType: string, value: any) => {
    const newNode: DataStructureNode = {
      id: `node-${Date.now()}`,
      value,
      type: 'node',
      position: { x: 100 + nodes.length * 80, y: 200 },
      children: [],
      metadata: { nodeType }
    };

    setNodes(prev => {
      const updated = [...prev, newNode];
      onStructureChange?.(updated);
      return updated;
    });
  }, [nodes.length, onStructureChange]);

  const handleNodeDrag = useCallback((nodeId: string, position: { x: number; y: number }) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId ? { ...node, position } : node
    ));
  }, []);

  const handleNodeConnect = useCallback((sourceId: string, targetId: string) => {
    if (mode !== 'connect') return;

    setNodes(prev => prev.map(node => {
      if (node.id === sourceId) {
        const targetExists = node.children?.some(child => child.id === targetId);
        if (!targetExists) {
          const targetNode = prev.find(n => n.id === targetId);
          if (targetNode) {
            return {
              ...node,
              children: [...(node.children || []), targetNode]
            };
          }
        }
      }
      return node;
    }));
  }, [mode]);

  const handleNodeDelete = useCallback((nodeId: string) => {
    setNodes(prev => {
      const updated = prev.filter(node => node.id !== nodeId)
        .map(node => ({
          ...node,
          children: node.children?.filter(child => child.id !== nodeId) || []
        }));
      onStructureChange?.(updated);
      return updated;
    });
  }, [onStructureChange]);

  const handleValidateStructure = useCallback(() => {
    const isValid = onValidate?.(nodes) ?? true;
    if (isValid) {
      alert('Structure is valid!');
    } else {
      alert('Structure has validation errors. Please check the connections.');
    }
  }, [nodes, onValidate]);

  const handleClearStructure = useCallback(() => {
    setNodes([]);
    setSelectedNode(null);
    onStructureChange?.([]);
  }, [onStructureChange]);

  const handleNodeSelect = useCallback((nodeId: string) => {
    setSelectedNode(selectedNode === nodeId ? null : nodeId);
  }, [selectedNode]);

  const handleCanvasDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    if (draggedNode && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const position = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      };

      const newNode: DataStructureNode = {
        ...draggedNode,
        id: `node-${Date.now()}`,
        position
      };

      setNodes(prev => {
        const updated = [...prev, newNode];
        onStructureChange?.(updated);
        return updated;
      });
      setDraggedNode(null);
    }
  }, [draggedNode, onStructureChange]);

  const handleCanvasDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
  }, []);

  const renderConnections = () => {
    const connections: JSX.Element[] = [];
    
    nodes.forEach(node => {
      node.children?.forEach(child => {
        const childNode = nodes.find(n => n.id === child.id);
        if (childNode) {
          const key = `connection-${node.id}-${child.id}`;
          connections.push(
            <svg key={key} className="connection-line">
              <line
                x1={node.position.x + 25}
                y1={node.position.y + 25}
                x2={childNode.position.x + 25}
                y2={childNode.position.y + 25}
                stroke="#666"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon
                    points="0 0, 10 3.5, 0 7"
                    fill="#666"
                  />
                </marker>
              </defs>
            </svg>
          );
        }
      });
    });
    
    return connections;
  };

  return (
    <DragDropProvider>
      <div className="data-structure-builder">
        <div className="builder-header">
          <h2>Build a {type.charAt(0).toUpperCase() + type.slice(1)}</h2>
          <div className="mode-selector">
            <button 
              className={mode === 'build' ? 'active' : ''}
              onClick={() => setMode('build')}
            >
              Build
            </button>
            <button 
              className={mode === 'connect' ? 'active' : ''}
              onClick={() => setMode('connect')}
            >
              Connect
            </button>
            <button 
              className={mode === 'edit' ? 'active' : ''}
              onClick={() => setMode('edit')}
            >
              Edit
            </button>
          </div>
          <div className="actions">
            <button onClick={handleValidateStructure}>Validate</button>
            <button onClick={handleClearStructure}>Clear</button>
          </div>
        </div>

        <div className="builder-content">
          <ToolPalette
            type={type}
            onNodeDragStart={setDraggedNode}
            onAddNode={handleAddNode}
          />

          <div 
            className="canvas"
            ref={canvasRef}
            onDrop={handleCanvasDrop}
            onDragOver={handleCanvasDragOver}
          >
            {renderConnections()}
            
            {nodes.map(node => (
              <NodeRenderer
                key={node.id}
                node={node}
                selected={selectedNode === node.id}
                mode={mode}
                onDrag={handleNodeDrag}
                onSelect={handleNodeSelect}
                onConnect={handleNodeConnect}
                onDelete={handleNodeDelete}
              />
            ))}

            {nodes.length === 0 && (
              <div className="empty-canvas">
                <p>Drag nodes from the palette to start building your {type}</p>
              </div>
            )}
          </div>

          {selectedNode && (
            <div className="property-panel">
              <h3>Node Properties</h3>
              <NodePropertyEditor
                node={nodes.find(n => n.id === selectedNode)!}
                onChange={(updatedNode) => {
                  setNodes(prev => prev.map(n => 
                    n.id === selectedNode ? updatedNode : n
                  ));
                }}
              />
            </div>
          )}
        </div>

        <div className="structure-info">
          <h3>Structure Statistics</h3>
          <div className="stats">
            <div className="stat">
              <span className="label">Nodes:</span>
              <span className="value">{nodes.length}</span>
            </div>
            <div className="stat">
              <span className="label">Connections:</span>
              <span className="value">
                {nodes.reduce((total, node) => total + (node.children?.length || 0), 0)}
              </span>
            </div>
            <div className="stat">
              <span className="label">Max Depth:</span>
              <span className="value">{calculateMaxDepth(nodes)}</span>
            </div>
          </div>
        </div>
      </div>
    </DragDropProvider>
  );
};

interface NodePropertyEditorProps {
  node: DataStructureNode;
  onChange: (node: DataStructureNode) => void;
}

const NodePropertyEditor: React.FC<NodePropertyEditorProps> = ({ node, onChange }) => {
  return (
    <div className="property-editor">
      <div className="property-group">
        <label>Value:</label>
        <input
          type="text"
          value={node.value}
          onChange={(e) => onChange({ ...node, value: e.target.value })}
        />
      </div>
      
      <div className="property-group">
        <label>Position X:</label>
        <input
          type="number"
          value={node.position.x}
          onChange={(e) => onChange({ 
            ...node, 
            position: { ...node.position, x: parseInt(e.target.value) }
          })}
        />
      </div>
      
      <div className="property-group">
        <label>Position Y:</label>
        <input
          type="number"
          value={node.position.y}
          onChange={(e) => onChange({ 
            ...node, 
            position: { ...node.position, y: parseInt(e.target.value) }
          })}
        />
      </div>
    </div>
  );
};

function calculateMaxDepth(nodes: DataStructureNode[]): number {
  if (nodes.length === 0) return 0;
  
  const getDepth = (node: DataStructureNode, visited = new Set<string>()): number => {
    if (visited.has(node.id)) return 0;
    visited.add(node.id);
    
    if (!node.children || node.children.length === 0) return 1;
    
    return 1 + Math.max(...node.children.map(child => getDepth(child, visited)));
  };
  
  return Math.max(...nodes.map(node => getDepth(node)));
}