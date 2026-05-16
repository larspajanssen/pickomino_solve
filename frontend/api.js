class SimulationAPI {
  constructor(url = "/api/run") {
    this.url = url;
  }

  /**
   * Sends a single REST request to the solver backend.
   *
   * Expected payload shape:
   * - `hand`: number[6] frequency vector for die faces 1..6
   * - `dice_throw`: null or number[6] frequency vector for die faces 1..6
   */
  async run(params) {
    let response;
    try {
      response = await fetch(this.url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });
    } catch {
      throw new Error("Network error while contacting backend");
    }

    let payload;
    try {
      payload = await response.json();
    } catch {
      throw new Error("Backend returned invalid JSON");
    }

    if (!response.ok) {
      const message =
        payload && typeof payload.detail === "string"
          ? payload.detail
          : "Backend request failed";
      throw new Error(message);
    }

    return payload;
  }
}

// Export for use in app.js
window.SimulationAPI = SimulationAPI;
