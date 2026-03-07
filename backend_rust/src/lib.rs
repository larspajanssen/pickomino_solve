mod game;
mod tree;

struct ValuedAction;

pub fn run(hand: Vec<u8>, dice_throw: Option<Vec<u8>>, c: f64) -> Vec<ValuedAction> {
    let actions = crate::tree::run(hand, dice_throw, c);
    vec![ValuedAction]
}

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
