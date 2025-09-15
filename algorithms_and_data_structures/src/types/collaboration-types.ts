// Collaboration Space Types
export interface CollaborationSession {
  id: string;
  participants: string[];
  algorithm: string;
  status: 'active' | 'paused' | 'completed';
  createdAt: Date;
  messages: CollaborationMessage[];
  sharedCode?: string;
  whiteboard?: SharedWhiteboard;
  videoEnabled?: boolean;
  permissions?: SessionPermissions;
}

export interface CollaborationMessage {
  id: string;
  userId: string;
  content: string;
  type: 'text' | 'code' | 'annotation' | 'system';
  timestamp: Date;
  metadata?: {
    codeLanguage?: string;
    annotationTarget?: string;
    systemEventType?: string;
  };
}

export interface SharedWhiteboard {
  elements: WhiteboardElement[];
  version: number;
  collaborators: string[];
}

export interface WhiteboardElement {
  id: string;
  type: 'line' | 'rectangle' | 'circle' | 'text' | 'arrow' | 'shape';
  position: { x: number; y: number };
  properties: {
    color?: string;
    strokeWidth?: number;
    fontSize?: number;
    text?: string;
    width?: number;
    height?: number;
  };
  userId: string;
  timestamp: Date;
}

export interface SessionPermissions {
  canEdit: string[];
  canView: string[];
  canInvite: string[];
  isPublic: boolean;
}

export interface ParticipantCursor {
  userId: string;
  position: { x: number; y: number };
  selection?: {
    start: { line: number; column: number };
    end: { line: number; column: number };
  };
  timestamp: Date;
}