// State
let hand = [];
let diceThrow = [];
let currentFocus = "hand"; // 'hand' or 'throw'
let chartInstance = null;
let simulationHistory = []; // Local history tracking
let simulationStartTime = 0;
let api;
const COLORS = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
];
const placeholders = {};

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  api = new SimulationAPI();
  // Cache placeholders
  placeholders["hand"] = document.getElementById("hand-placeholder");
  placeholders["throw"] = document.getElementById("throw-placeholder");
  updateUI();
});

// Dice Management
function setFocus(focus) {
  currentFocus = focus;
  // Visual feedback could be added here to show which pool is active
  document
    .querySelectorAll(".dice-pool")
    .forEach((el) => (el.style.borderColor = "rgba(255,255,255,0.1)"));
  document.getElementById(`${focus}-pool`).style.borderColor = "var(--accent)";
}

function addDieToFocus(value) {
  if (currentFocus === "hand") {
    if (hand.length + diceThrow.length >= 8) return shakePool("hand");
    hand.push(value);
  } else {
    if (hand.length + diceThrow.length >= 8) return shakePool("throw");
    diceThrow.push(value);
  }
  updateUI();
}

function removeDie(pool, index) {
  if (pool === "hand") {
    hand.splice(index, 1);
  } else {
    diceThrow.splice(index, 1);
  }
  updateUI();
}

function clearPool(pool) {
  if (pool === "hand") hand = [];
  else diceThrow = [];
  updateUI();
}

// UI Rendering
function updateUI() {
  renderPool("hand", hand);
  renderPool("throw", diceThrow);
  validateState();

  // Update hidden inputs for form submission if needed,
  // though we handle submission via JS
  document.getElementById("hand").value = hand.join(",");
}

function renderPool(poolName, diceArray) {
  const poolEl = document.getElementById(`${poolName}-pool`);
  const countEl = document.getElementById(`${poolName}-count`);
  const placeholder = placeholders[poolName];

  poolEl.innerHTML = ""; // Clear current

  // Always append placeholder (it handles its own display state via CSS class or style)
  if (placeholder) {
    poolEl.appendChild(placeholder);
  }

  if (diceArray.length === 0) {
    if (placeholder) placeholder.style.display = "block";
  } else {
    if (placeholder) placeholder.style.display = "none";

    diceArray.forEach((value, index) => {
      const dieDiv = document.createElement("div");
      dieDiv.className = "die-btn die-in-pool";
      dieDiv.onclick = (e) => {
        e.stopPropagation();
        removeDie(poolName, index);
      };
      dieDiv.title = "Click to remove";

      if (value === 6) {
        dieDiv.innerHTML = '<div class="worm-face">🪱</div>';
      } else {
        dieDiv.innerHTML = createDots(value);
      }
      poolEl.appendChild(dieDiv);
    });
  }

  // Update Count
  const totalDice = hand.length + diceThrow.length;
  countEl.textContent = `${diceArray.length}`;

  // Highlight active focus
  setFocus(currentFocus);
}

function createDots(value) {
  let dotsHtml = '<div class="die-face">';
  const positions = {
    1: ["2,2"],
    2: ["3,1", "1,3"],
    3: ["3,1", "2,2", "1,3"],
    4: ["1,1", "1,3", "3,1", "3,3"],
    5: ["1,1", "1,3", "2,2", "3,1", "3,3"],
  };

  (positions[value] || []).forEach((pos) => {
    const [row, col] = pos.split(",");
    dotsHtml += `<div class="dot" style="grid-column: ${col}; grid-row: ${row};"></div>`;
  });

  dotsHtml += "</div>";
  return dotsHtml;
}

function shakePool(poolName) {
  const pool = document.getElementById(`${poolName}-pool`);
  pool.animate(
    [
      { transform: "translateX(0)" },
      { transform: "translateX(-5px)" },
      { transform: "translateX(5px)" },
      { transform: "translateX(0)" },
    ],
    { duration: 200 },
  );
}

// Validation
function validateState() {
  const errorEl = document.getElementById("validation-error");
  const submitBtn = document.getElementById("submit-btn");
  const totalDice = hand.length + diceThrow.length;

  let error = "";

  // Basic Rule: Max 8 dice
  // (This is prevented by addDieToFocus, but good to check)
  if (totalDice > 8) {
    error = "Too many dice! Maximum 8 allowed.";
  }
  // Strict Rule: If throwing, total must be 8
  else if (diceThrow.length > 0 && totalDice !== 8) {
    error = `Invalid state: You have ${diceThrow.length} dice in throw and ${hand.length} in hand (Total: ${totalDice}). Total must be 8 when dice are thrown.`;
  }

  if (error) {
    errorEl.textContent = error;
    submitBtn.disabled = true;
    return false;
  } else {
    errorEl.textContent = "";
    submitBtn.disabled = false;
    return true;
  }
}

// Thinking Time Slider
document
  .getElementById("thinking-time")
  .addEventListener("input", function (e) {
    document.getElementById("time-value").textContent = e.target.value;
  });

// Form Submission
document.getElementById("game-form").addEventListener("submit", function (e) {
  e.preventDefault();
  if (!validateState()) return;

  const thinking_time = Number(document.getElementById("thinking-time").value);

  // Show Loading State
  const submitBtn = document.getElementById("submit-btn");
  const cancelBtn = document.getElementById("cancel-btn");
  const originalText = submitBtn.textContent;

  submitBtn.textContent = "Running Simulation...";
  submitBtn.disabled = true;
  cancelBtn.style.display = "block";

  simulationHistory = [];
  simulationStartTime = Date.now();
  document.getElementById("results").style.display = "block";

  api.start(
    { hand, dice_throw: diceThrow.length ? diceThrow : null, thinking_time },
    {
      onProgress: (actions) => {
        // Track history locally
        const timestamp = (Date.now() - simulationStartTime) / 1000;
        simulationHistory.push({ time: timestamp, actions });
        renderResults(actions);
      },
      onComplete: (actions) => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        cancelBtn.style.display = "none";
        renderResults(actions);
      },
      onError: (message) => {
        alert("Error: " + message);
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        cancelBtn.style.display = "none";
      },
    },
  );
});

document.getElementById("cancel-btn").addEventListener("click", () => {
  api.cancel();
});

function renderResults(actions) {
  const tbody = document.querySelector("#results-table tbody");
  tbody.innerHTML = "";

  // Sort actions by expected_score descending
  actions.sort((a, b) => b.expected_score - a.expected_score);

  actions.forEach((action, index) => {
    // Table row
    const tr = document.createElement("tr");
    const score =
      typeof action.expected_score === "number"
        ? action.expected_score.toFixed(3)
        : action.expected_score;
    tr.innerHTML = `<td>${action.action}</td><td>${score}</td><td>${action.visit_count}</td>`;
    tbody.appendChild(tr);
  });

  // Prepare datasets for chart from local history
  const datasets = [];
  const actionNames = actions.map((a) => a.action);

  actionNames.forEach((name, index) => {
    const data = simulationHistory
      .map((h) => {
        const actionData = h.actions.find((a) => a.action === name);
        return { x: h.time, y: actionData ? actionData.expected_score : null };
      })
      .filter((d) => d.y !== null);

    if (data.length > 0) {
      datasets.push({
        label: name,
        data: data,
        borderColor: COLORS[index % COLORS.length],
        fill: false,
        tension: 0.1,
        pointRadius: 0, // Performance optimization for live updates
      });
    }
  });

  renderChart(datasets);
}

function renderChart(datasets) {
  const ctx = document.getElementById("convergence-chart").getContext("2d");

  // Dark theme for chart
  Chart.defaults.color = "#e0e0e0";
  Chart.defaults.borderColor = "rgba(255, 255, 255, 0.1)";

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      scales: {
        x: {
          type: "linear",
          title: {
            display: true,
            text: "Time (s)",
            color: "#aaaaaa",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.05)",
          },
        },
        y: {
          title: {
            display: true,
            text: "Expected Score",
            color: "#aaaaaa",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.05)",
          },
        },
      },
      plugins: {
        title: {
          display: true,
          text: "Action Score Convergence",
          color: "#e0e0e0",
          font: {
            size: 16,
          },
        },
        legend: {
          labels: {
            color: "#e0e0e0",
          },
        },
      },
    },
  });
}
