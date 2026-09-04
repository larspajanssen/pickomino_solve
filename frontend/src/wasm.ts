import init, { solve as solveWasm } from "../../wasm/pkg/pickomino_wasm";
import type { SolveRequest, SolveResult } from "./types";

let initialized: Promise<unknown> | undefined;
export async function solve(request: SolveRequest): Promise<SolveResult> {
  initialized ??= init();
  await initialized;
  return solveWasm(request) as SolveResult;
}
