// State
let hand = [];
let diceThrow = [];
let currentFocus = "hand"; // 'hand' or 'throw'
let availableTiles = new Set(Array.from({ length: 16 }, (_, i) => i + 21));
let api;
const placeholders = {};

/**
 * Converts raw die face values (1-6) into a fixed-length frequency vector.
 * Index 0 stores count of face 1, index 5 stores count of face 6.
 *
 * Backend contract:
 * - `hand` must be a list of length 6
 * - `dice_throw` must be null or a list of length 6
 */
function toFrequencyVector(diceArray) {
  const frequency = [0, 0, 0, 0, 0, 0];
  for (const value of diceArray) {
    if (value >= 1 && value <= 6) {
      frequency[value - 1] += 1;
    }
  }
  return frequency;
}

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  api = new SimulationAPI();
  // Cache placeholders
  placeholders["hand"] = document.getElementById("hand-placeholder");
  placeholders["throw"] = document.getElementById("throw-placeholder");
  updateUI();
  renderTiles();
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

// Form Submission
document
  .getElementById("game-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!validateState()) return;

    // Show Loading State
    const submitBtn = document.getElementById("submit-btn");
    const originalText = submitBtn.textContent;

    submitBtn.textContent = "Running Simulation...";
    submitBtn.disabled = true;
    document.getElementById("results").style.display = "block";

    try {
      const response = await api.run({
        hand: toFrequencyVector(hand),
        dice_throw: diceThrow.length ? toFrequencyVector(diceThrow) : null,
        tiles: Array.from(availableTiles).sort((a, b) => a - b),
      });
      renderResults(response.actions ?? []);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      alert("Error: " + message);
    } finally {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  });

function renderResults(actions) {
  const tbody = document.querySelector("#results-table tbody");
  tbody.innerHTML = "";

  // Sort actions by expected_value descending
  actions.sort((a, b) => b.expected_value - a.expected_value);

  actions.forEach((action) => {
    const tr = document.createElement("tr");
    const score =
      typeof action.expected_value === "number"
        ? action.expected_value.toFixed(3)
        : action.expected_value;
    tr.innerHTML = `<td>${action.action}</td><td>${score}</td>`;
    tbody.appendChild(tr);
  });
}

// Tiles rendering and management
function renderTiles() {
  const poolEl = document.getElementById("tiles-pool");
  if (!poolEl) return;
  poolEl.innerHTML = "";

  for (let i = 21; i <= 36; i++) {
    const tileDiv = document.createElement("button");
    tileDiv.type = "button";
    const isActive = availableTiles.has(i);
    tileDiv.className = `tile ${isActive ? "active" : "turned-over"}`;
    tileDiv.onclick = () => toggleTile(i);
    tileDiv.title = `Click to toggle availability of tile ${i}`;

    let wormCount = 1;
    if (i >= 25 && i <= 28) wormCount = 2;
    else if (i >= 29 && i <= 32) wormCount = 3;
    else if (i >= 33 && i <= 36) wormCount = 4;

    const wormsStr = "🪱".repeat(wormCount);

    tileDiv.innerHTML = `
      <div class="tile-number">${i}</div>
      <div class="tile-divider"></div>
      <div class="tile-worms">${wormsStr}</div>
    `;
    poolEl.appendChild(tileDiv);
  }
}

function toggleTile(value) {
  if (availableTiles.has(value)) {
    availableTiles.delete(value);
  } else {
    availableTiles.add(value);
  }
  renderTiles();
}

function toggleAllTiles(allActive) {
  if (allActive) {
    for (let i = 21; i <= 36; i++) {
      availableTiles.add(i);
    }
  } else {
    availableTiles.clear();
  }
  renderTiles();
}
