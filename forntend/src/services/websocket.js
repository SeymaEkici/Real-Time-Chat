export const createWebSocketConnection = (clientId, token = null) => {
    const wsUrl = token 
      ? `ws://localhost:8000/secured-ws/${clientId}?token=${token}`
      : `ws://localhost:8000/ws/${clientId}`;
      
    const socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
      console.log('WebSocket connection established');
    };
    
    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return socket;
  };