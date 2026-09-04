import { useState } from "react";
import { solve } from "./wasm";
import type { ActionResult, Pool } from "./types";

const faces = [1, 2, 3, 4, 5, 6];
const allTiles = Array.from({ length: 16 }, (_, i) => i + 21);
const counts = (dice: number[]) =>
  faces.map((face) => dice.filter((value) => value === face).length);

function Die({
  value,
  onClick,
  label,
}: {
  value: number;
  onClick: () => void;
  label: string;
}) {
  return (
    <button type="button" className="die" onClick={onClick} aria-label={label}>
      {value === 6 ? (
        "🪱"
      ) : (
        <span className={`pips pips-${value}`}>
          {Array.from({ length: value }, (_, i) => (
            <i key={i} />
          ))}
        </span>
      )}
    </button>
  );
}

export default function App() {
  const [hand, setHand] = useState<number[]>([]);
  const [throwDice, setThrowDice] = useState<number[]>([]);
  const [focus, setFocus] = useState<Pool>("hand");
  const [tiles, setTiles] = useState(new Set(allTiles));
  const [results, setResults] = useState<ActionResult[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function addDie(value: number) {
    if (hand.length + throwDice.length >= 8) return;
    (focus === "hand" ? setHand : setThrowDice)((current) => [
      ...current,
      value,
    ]);
  }
  function remove(pool: Pool, index: number) {
    (pool === "hand" ? setHand : setThrowDice)((current) =>
      current.filter((_, i) => i !== index),
    );
  }
  function toggleTile(tile: number) {
    setTiles((current) => {
      const next = new Set(current);
      next.has(tile) ? next.delete(tile) : next.add(tile);
      return next;
    });
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (throwDice.length > 0 && hand.length + throwDice.length !== 8) {
      setError(
        "A throw must contain all remaining dice, for a total of eight.",
      );
      return;
    }
    if (tiles.size === 0) {
      setError("Select at least one available tile.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await solve({
        hand: counts(hand),
        dice_throw: throwDice.length ? counts(throwDice) : null,
        tiles: [...tiles].sort((a, b) => a - b),
      });
      setResults(
        [...result.actions].sort((a, b) => b.expected_value - a.expected_value),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="container">
      <header>
        <h1>
          Pickomino
          <br />
          <em>Solver</em>
        </h1>
      </header>
      <form onSubmit={submit}>
        <section className="section dice-section">
          <h2>Add dice</h2>
          <div className="dice-controls">
            {faces.map((face) => (
              <Die
                key={face}
                value={face}
                onClick={() => addDie(face)}
                label={face === 6 ? "Add worm" : `Add ${face}`}
              />
            ))}
          </div>
        </section>
        <section className="section">
          <div className="section-heading">
            <h2>Available tiles</h2>
            <div>
              <button
                type="button"
                className="text-button"
                onClick={() => setTiles(new Set(allTiles))}
              >
                Select all
              </button>
              <button
                type="button"
                className="text-button"
                onClick={() => setTiles(new Set())}
              >
                Clear
              </button>
            </div>
          </div>
          <div className="tiles">
            {allTiles.map((tile) => (
              <button
                type="button"
                key={tile}
                className={`tile ${tiles.has(tile) ? "active" : "off"}`}
                onClick={() => toggleTile(tile)}
              >
                <strong>{tile}</strong>
                <span>
                  {"🪱".repeat(
                    tile < 25 ? 1 : tile < 29 ? 2 : tile < 33 ? 3 : 4,
                  )}
                </span>
              </button>
            ))}
          </div>
        </section>
        {(["hand", "throw"] as Pool[]).map((pool) => {
          const dice = pool === "hand" ? hand : throwDice;
          return (
            <section className="section" key={pool}>
              <div className="section-heading">
                <h2>{pool === "hand" ? "Current hand" : "Current throw"}</h2>
                <span className="count">{dice.length} / 8</span>
              </div>
              <div
                className={`pool ${focus === pool ? "focused" : ""}`}
                onClick={() => setFocus(pool)}
              >
                {dice.length === 0 && (
                  <span className="placeholder">
                    Click a die above to add it here
                  </span>
                )}
                {dice.map((value, index) => (
                  <Die
                    key={`${value}-${index}`}
                    value={value}
                    onClick={() => remove(pool, index)}
                    label="Remove die"
                  />
                ))}
              </div>
              <button
                type="button"
                className="text-button"
                onClick={() =>
                  pool === "hand" ? setHand([]) : setThrowDice([])
                }
              >
                Clear {pool}
              </button>
            </section>
          );
        })}
        {error && <p className="error">{error}</p>}
        <button className="solve" disabled={busy}>
          {busy ? "Solving..." : "Compute best action"}
        </button>
      </form>
      {results.length > 0 && (
        <section className="section results">
          <div className="section-heading">
            <h2>Recommended actions</h2>
            <span className="badge">Expected scores</span>
          </div>
          {results.map((result) => (
            <div className="result" key={result.action}>
              <span>{result.action}</span>
              <strong>{result.expected_value.toFixed(3)}</strong>
            </div>
          ))}
        </section>
      )}
    </main>
  );
}
