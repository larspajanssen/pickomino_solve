use std::hint::black_box;
use std::time::Instant;

use pickomino_solver::{SolveRequest, solve};

fn main() {
    let request = SolveRequest {
        hand: [0, 1, 1, 1, 1, 3],
        dice_throw: None,
        tiles: (21..=36).collect(),
    };
    let started = Instant::now();
    for _ in 0..10 {
        black_box(solve(request.clone()).expect("benchmark request is valid"));
    }
    let elapsed = started.elapsed();
    println!("10 solves: {elapsed:?}; average: {:?}", elapsed / 10);
}
