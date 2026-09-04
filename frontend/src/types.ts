export type Pool = "hand" | "throw";
export interface SolveRequest {
  hand: number[];
  dice_throw: number[] | null;
  tiles: number[];
}
export interface ActionResult {
  action: string;
  expected_value: number;
}
export interface SolveResult {
  actions: ActionResult[];
}
