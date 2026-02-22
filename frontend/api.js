class SimulationAPI {
  constructor(url = `ws://${window.location.host}/ws/simulation`) {
    this.url = url;
    this.socket = null;
    this.onProgress = null;
    this.onComplete = null;
    this.onError = null;
  }

  start(params, { onProgress, onComplete, onError }) {
    if (this.socket) {
      this.socket.close();
    }

    this.onProgress = onProgress;
    this.onComplete = onComplete;
    this.onError = onError;

    // Determine protocol based on current window location
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/simulation`;

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log("WebSocket Connected");
      this.socket.send(JSON.stringify(params));
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "progress":
          if (this.onProgress) this.onProgress(data.actions);
          break;
        case "complete":
          if (this.onComplete) this.onComplete(data.actions);
          this.socket.close();
          this.socket = null;
          break;
        case "error":
          if (this.onError) this.onError(data.message);
          this.socket.close();
          this.socket = null;
          break;
      }
    };

    this.socket.onerror = (error) => {
      if (this.onError) this.onError("WebSocket Connection Error");
      this.socket = null;
    };

    this.socket.onclose = () => {
      console.log("WebSocket Disconnected");
      this.socket = null;
    };
  }

  cancel() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type: "cancel" }));
    }
  }
}

// Export for use in app.js
window.SimulationAPI = SimulationAPI;
