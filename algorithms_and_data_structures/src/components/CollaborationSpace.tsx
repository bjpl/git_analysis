import React, { useState, useEffect, useCallback, useRef } from 'react';
import { CollaborationSession, CollaborationMessage, SharedWhiteboard } from '../types/collaboration-types';
import { VideoChat } from './VideoChat';
import { SharedCodeEditor } from './SharedCodeEditor';
import { WhiteboardCanvas } from './WhiteboardCanvas';
import { ParticipantsList } from './ParticipantsList';
import { SessionControls } from './SessionControls';

interface CollaborationSpaceProps {
  sessionId?: string;
  userId: string;
  userName: string;
  onSessionCreate?: (session: CollaborationSession) => void;
  onSessionJoin?: (sessionId: string) => void;
  onSessionLeave?: () => void;
}

export const CollaborationSpace: React.FC<CollaborationSpaceProps> = ({
  sessionId,
  userId,
  userName,
  onSessionCreate,
  onSessionJoin,
  onSessionLeave
}) => {
  const [currentSession, setCurrentSession] = useState<CollaborationSession | null>(null);
  const [messages, setMessages] = useState<CollaborationMessage[]>([]);
  const [activeMode, setActiveMode] = useState<'code' | 'whiteboard' | 'video'>('code');
  const [isConnected, setIsConnected] = useState(false);
  const [participants, setParticipants] = useState<SessionParticipant[]>([]);
  const [sharedCode, setSharedCode] = useState('');
  const [whiteboardState, setWhiteboardState] = useState<SharedWhiteboard | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  
  const wsRef = useRef<WebSocket | null>(null);
  const messageInputRef = useRef<HTMLInputElement>(null);

  // Initialize collaboration session
  useEffect(() => {
    if (sessionId) {
      joinSession(sessionId);
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId]);

  // WebSocket connection management
  const connectToSession = useCallback((sessionId: string) => {
    const wsUrl = `ws://localhost:8080/collaboration/${sessionId}`;
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      setConnectionStatus('connected');
      setIsConnected(true);
      
      // Send join message
      sendMessage({
        type: 'user_joined',
        userId,
        userName,
        timestamp: new Date()
      });
    };
    
    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleIncomingMessage(message);
    };
    
    wsRef.current.onclose = () => {
      setConnectionStatus('disconnected');
      setIsConnected(false);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('disconnected');
    };
  }, [userId, userName]);

  // Handle incoming WebSocket messages
  const handleIncomingMessage = useCallback((message: any) => {
    switch (message.type) {
      case 'chat_message':
        setMessages(prev => [...prev, message]);
        break;
      case 'code_update':
        setSharedCode(message.code);
        break;
      case 'whiteboard_update':
        setWhiteboardState(message.whiteboardState);
        break;
      case 'user_joined':
        setParticipants(prev => [...prev, {
          id: message.userId,
          name: message.userName,
          joinedAt: new Date(message.timestamp),
          isActive: true,
          cursor: null
        }]);
        break;
      case 'user_left':
        setParticipants(prev => prev.filter(p => p.id !== message.userId));
        break;
      case 'cursor_update':
        updateParticipantCursor(message.userId, message.cursor);
        break;
      case 'session_update':
        setCurrentSession(message.session);
        break;
    }
  }, []);

  // Send message through WebSocket
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Create new collaboration session
  const createSession = useCallback(async () => {
    const newSession: CollaborationSession = {
      id: `session-${Date.now()}`,
      participants: [userId],
      algorithm: '',
      status: 'active',
      createdAt: new Date(),
      messages: [],
      sharedCode: '',
      whiteboard: {
        elements: [],
        version: 0
      }
    };
    
    setCurrentSession(newSession);
    connectToSession(newSession.id);
    onSessionCreate?.(newSession);
  }, [userId, connectToSession, onSessionCreate]);

  // Join existing session
  const joinSession = useCallback(async (sessionId: string) => {
    try {
      // In a real app, this would fetch session details from API
      const session = await fetchSessionDetails(sessionId);
      setCurrentSession(session);
      connectToSession(sessionId);
      onSessionJoin?.(sessionId);
    } catch (error) {
      console.error('Failed to join session:', error);
    }
  }, [connectToSession, onSessionJoin]);

  // Leave current session
  const leaveSession = useCallback(() => {
    if (wsRef.current) {
      sendMessage({
        type: 'user_left',
        userId,
        timestamp: new Date()
      });
      wsRef.current.close();
    }
    
    setCurrentSession(null);
    setIsConnected(false);
    setMessages([]);
    setParticipants([]);
    onSessionLeave?.();
  }, [userId, sendMessage, onSessionLeave]);

  // Handle chat message
  const handleChatMessage = useCallback((content: string) => {
    const message: CollaborationMessage = {
      id: `msg-${Date.now()}`,
      userId,
      content,
      type: 'text',
      timestamp: new Date()
    };
    
    sendMessage({
      type: 'chat_message',
      ...message
    });
    
    setMessages(prev => [...prev, message]);
  }, [userId, sendMessage]);

  // Handle code changes
  const handleCodeChange = useCallback((code: string) => {
    setSharedCode(code);
    
    sendMessage({
      type: 'code_update',
      code,
      userId,
      timestamp: new Date()
    });
  }, [userId, sendMessage]);

  // Handle whiteboard changes
  const handleWhiteboardChange = useCallback((whiteboardState: SharedWhiteboard) => {
    setWhiteboardState(whiteboardState);
    
    sendMessage({
      type: 'whiteboard_update',
      whiteboardState,
      userId,
      timestamp: new Date()
    });
  }, [userId, sendMessage]);

  // Update participant cursor position
  const updateParticipantCursor = useCallback((participantId: string, cursor: any) => {
    setParticipants(prev => prev.map(p => 
      p.id === participantId ? { ...p, cursor } : p
    ));
  }, []);

  // Handle cursor movement for real-time collaboration
  const handleCursorMove = useCallback((position: { x: number; y: number }) => {
    sendMessage({
      type: 'cursor_update',
      userId,
      cursor: position,
      timestamp: new Date()
    });
  }, [userId, sendMessage]);

  // Render session creation/joining interface
  if (!currentSession) {
    return (
      <div className="collaboration-space-setup">
        <div className="setup-header">
          <h2>Collaboration Space</h2>
          <p>Work together on algorithms and data structures</p>
        </div>

        <div className="setup-options">
          <div className="create-session">
            <h3>Create New Session</h3>
            <p>Start a new collaborative learning session</p>
            <button onClick={createSession} className="primary-button">
              Create Session
            </button>
          </div>

          <div className="join-session">
            <h3>Join Existing Session</h3>
            <div className="join-form">
              <input
                type="text"
                placeholder="Enter session ID"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    const sessionId = (e.target as HTMLInputElement).value;
                    if (sessionId) {
                      joinSession(sessionId);
                    }
                  }
                }}
              />
              <button onClick={() => {
                const input = document.querySelector('.join-form input') as HTMLInputElement;
                if (input.value) {
                  joinSession(input.value);
                }
              }}>
                Join Session
              </button>
            </div>
          </div>
        </div>

        <div className="recent-sessions">
          <h3>Recent Sessions</h3>
          <RecentSessionsList
            userId={userId}
            onSessionSelect={joinSession}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="collaboration-space">
      <div className="collaboration-header">
        <div className="session-info">
          <h2>Session: {currentSession.id}</h2>
          <div className="connection-status">
            <span className={`status-indicator ${connectionStatus}`} />
            <span className="status-text">{connectionStatus}</span>
          </div>
        </div>

        <div className="session-actions">
          <button onClick={() => navigator.clipboard.writeText(currentSession.id)}>
            Share Session ID
          </button>
          <button onClick={leaveSession} className="danger-button">
            Leave Session
          </button>
        </div>
      </div>

      <div className="collaboration-content">
        <div className="main-workspace">
          <div className="workspace-tabs">
            <button
              className={activeMode === 'code' ? 'active' : ''}
              onClick={() => setActiveMode('code')}
            >
              Code Editor
            </button>
            <button
              className={activeMode === 'whiteboard' ? 'active' : ''}
              onClick={() => setActiveMode('whiteboard')}
            >
              Whiteboard
            </button>
            <button
              className={activeMode === 'video' ? 'active' : ''}
              onClick={() => setActiveMode('video')}
            >
              Video Chat
            </button>
          </div>

          <div className="workspace-content">
            {activeMode === 'code' && (
              <SharedCodeEditor
                code={sharedCode}
                language="javascript"
                participants={participants}
                onChange={handleCodeChange}
                onCursorMove={handleCursorMove}
                readOnly={!isConnected}
              />
            )}

            {activeMode === 'whiteboard' && (
              <WhiteboardCanvas
                whiteboardState={whiteboardState}
                participants={participants}
                onChange={handleWhiteboardChange}
                onCursorMove={handleCursorMove}
                readOnly={!isConnected}
              />
            )}

            {activeMode === 'video' && (
              <VideoChat
                sessionId={currentSession.id}
                participants={participants}
                userId={userId}
              />
            )}
          </div>
        </div>

        <div className="collaboration-sidebar">
          <div className="participants-section">
            <h3>Participants ({participants.length})</h3>
            <ParticipantsList
              participants={participants}
              currentUserId={userId}
            />
          </div>

          <div className="chat-section">
            <h3>Chat</h3>
            <div className="chat-messages">
              {messages.map(message => (
                <div key={message.id} className="chat-message">
                  <div className="message-header">
                    <span className="sender">
                      {participants.find(p => p.id === message.userId)?.name || 'Unknown'}
                    </span>
                    <span className="timestamp">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-content">
                    {message.type === 'text' ? (
                      message.content
                    ) : message.type === 'code' ? (
                      <pre><code>{message.content}</code></pre>
                    ) : (
                      <div className="annotation">
                        {message.content}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="chat-input">
              <input
                ref={messageInputRef}
                type="text"
                placeholder="Type a message..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    const content = (e.target as HTMLInputElement).value;
                    if (content.trim()) {
                      handleChatMessage(content);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }
                }}
              />
              <button onClick={() => {
                if (messageInputRef.current) {
                  const content = messageInputRef.current.value;
                  if (content.trim()) {
                    handleChatMessage(content);
                    messageInputRef.current.value = '';
                  }
                }
              }}>
                Send
              </button>
            </div>
          </div>

          <div className="session-controls">
            <SessionControls
              session={currentSession}
              isHost={currentSession.participants[0] === userId}
              onAlgorithmChange={(algorithm) => {
                sendMessage({
                  type: 'session_update',
                  session: { ...currentSession, algorithm }
                });
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Supporting Components
interface RecentSessionsListProps {
  userId: string;
  onSessionSelect: (sessionId: string) => void;
}

const RecentSessionsList: React.FC<RecentSessionsListProps> = ({
  userId,
  onSessionSelect
}) => {
  const [recentSessions, setRecentSessions] = useState([]);

  useEffect(() => {
    loadRecentSessions(userId).then(setRecentSessions);
  }, [userId]);

  return (
    <div className="recent-sessions-list">
      {recentSessions.map((session: any) => (
        <div
          key={session.id}
          className="recent-session-item"
          onClick={() => onSessionSelect(session.id)}
        >
          <div className="session-info">
            <span className="session-name">{session.algorithm || 'Untitled Session'}</span>
            <span className="session-date">{session.lastActive}</span>
          </div>
          <div className="session-participants">
            {session.participantCount} participant{session.participantCount !== 1 ? 's' : ''}
          </div>
        </div>
      ))}
      
      {recentSessions.length === 0 && (
        <div className="no-recent-sessions">
          <p>No recent sessions found</p>
          <p>Create a new session to start collaborating</p>
        </div>
      )}
    </div>
  );
};

// Types
interface SessionParticipant {
  id: string;
  name: string;
  joinedAt: Date;
  isActive: boolean;
  cursor: { x: number; y: number } | null;
}

// Helper functions
async function fetchSessionDetails(sessionId: string): Promise<CollaborationSession> {
  // Mock implementation - would fetch from real API
  return {
    id: sessionId,
    participants: [],
    algorithm: '',
    status: 'active',
    createdAt: new Date(),
    messages: []
  };
}

async function loadRecentSessions(userId: string) {
  // Mock implementation
  return [
    {
      id: 'session-1',
      algorithm: 'Quick Sort',
      lastActive: '2 hours ago',
      participantCount: 3
    },
    {
      id: 'session-2',
      algorithm: 'Binary Search Tree',
      lastActive: '1 day ago',
      participantCount: 2
    }
  ];
}

// Additional type definitions that would be in collaboration-types.ts
interface SharedWhiteboard {
  elements: WhiteboardElement[];
  version: number;
}

interface WhiteboardElement {
  id: string;
  type: 'line' | 'rectangle' | 'circle' | 'text';
  position: { x: number; y: number };
  properties: any;
  userId: string;
  timestamp: Date;
}