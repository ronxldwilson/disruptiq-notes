const socket = new WebSocket('wss://socket.example.com');

socket.onopen = () => {
  console.log('WebSocket connection established');
};
