use bit_set::BitSet;
use serde_json::{Result, Value};
use std::env;
use std::time::Instant;

struct Graph {
    // node id -> set of neighbour node ids
    neighbours: Vec<BitSet<u32>>,

    // color id -> set of node ids with that color
    colors: Vec<BitSet<u32>>,
}

impl Graph {
    fn node_count(&self) -> usize {
        self.neighbours.len()
    }

    fn color_count(&self) -> usize {
        self.colors.len()
    }
}

struct GraphSinglePlayerSolver {
    graph: Graph,
    start_node_id: usize,
    max_moves: usize,
    solve_start: Instant,
    attempts: usize,
    moves: Vec<usize>,
}

struct Solution {
    moves: Vec<usize>,
}

impl GraphSinglePlayerSolver {
    fn new(graph: Graph, start_node_id: usize) -> Self {
        Self {
            graph,
            start_node_id,
            max_moves: 0,
            solve_start: Instant::now(),
            attempts: 0,
            moves: Vec::new(),
        }
    }

    fn get_newly_flooded(&self, flooded: &BitSet, mov: usize) -> BitSet {
        let unflooded_color_set = self.graph.colors[mov].difference(flooded);
        let mut newly_flooded = BitSet::new();
        for node in unflooded_color_set.into_iter() {
            if self.graph.neighbours[node].intersection(flooded).count() > 0 {
                newly_flooded.insert(node);
            }
        }
        newly_flooded
    }

    fn count_unflooded_colors(&self, flooded_bitset: &BitSet) -> usize {
        let mut unflooded_colors = 0;
        for color_set in &self.graph.colors {
            if color_set.difference(flooded_bitset).count() > 0 {
                unflooded_colors += 1;
            }
        }
        unflooded_colors
    }

    fn print_speed(&self) {
        let seconds = self.solve_start.elapsed().as_secs_f64();
        let speed = self.attempts as f64 / seconds;
        println!(
            "{:>10} attempts / {:7.2} sec = {:6.0} attempts / sec",
            self.attempts, seconds, speed
        );
    }

    fn solve(&mut self) -> Solution {
        self.solve_start = Instant::now();
        self.attempts = 0;

        let mut best_solution: Option<Solution> = None;
        self.max_moves = self.graph.node_count();

        loop {
            let mut initial_flooded = BitSet::new();
            initial_flooded.insert(self.start_node_id);

            match self._solve(&initial_flooded) {
                Some(solution) => {
                    self.print_speed();
                    print!("Found solution ({}): ", solution.moves.len());
                    for &move_ in &solution.moves {
                        print!("{} ", move_);
                    }
                    println!();
                    self.max_moves = solution.moves.len() - 1;
                    best_solution = Some(solution);
                }
                None => break,
            }
        }

        self.print_speed();
        best_solution.unwrap()
    }

    fn _solve(&mut self, flooded: &BitSet) -> Option<Solution> {
        if self.moves.len() > self.max_moves {
            return None;
        }

        if self.count_unflooded_colors(flooded) + self.moves.len() > self.max_moves {
            return None;
        }

        if flooded.len() == self.graph.node_count() as usize {
            let solution = Solution {
                moves: self.moves.clone(),
            };
            self.moves.clear();

            return Some(solution);
        }

        self.attempts += 1;
        if self.attempts % 100000 == 0 {
            self.print_speed();
        }

        let mut valid_moves = BitSet::<u32>::from_iter(0..self.graph.color_count());
        if let Some(&last_move) = self.moves.last() {
            valid_moves.remove(last_move);
        }

        let mut move_tuples: Vec<(usize, usize, BitSet)> = vec![];

        for mov in &valid_moves {
            let newly_flooded = self.get_newly_flooded(flooded, mov);
            let heuristic = newly_flooded.len();

            if newly_flooded.len() > 0 {
                let move_tuple = (mov, heuristic, newly_flooded);
                move_tuples.push(move_tuple);
            }
        }

        move_tuples.sort_by(|a, b| b.1.cmp(&a.1));

        for (mov, _, newly_flooded) in move_tuples {
            let mut child_flooded = flooded.clone();
            child_flooded.union_with(&newly_flooded);
            self.moves.push(mov);
            if let Some(solution) = self._solve(&child_flooded) {
                return Some(solution);
            }
            self.moves.pop();
        }

        None
    }
}

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        println!("Usage: {} <graph_json>", args[0]);
        return Ok(());
    }

    let json_value: Value = match serde_json::from_str(&args[1]) {
        Ok(value) => value,
        Err(_) => {
            println!("JSON parse error!");
            return Ok(());
        }
    };

    let object = json_value.as_object().unwrap();

    let start = object.get_key_value("start").unwrap().1.as_i64().unwrap() as usize;

    let neighbours: Vec<BitSet<u32>> = object
        .get_key_value("neighbours")
        .unwrap()
        .1
        .as_array()
        .unwrap()
        .iter()
        .map(|l| {
            BitSet::from_iter(
                l.as_array()
                    .unwrap()
                    .iter()
                    .map(|i| i.as_u64().unwrap() as usize),
            )
        })
        .collect::<Vec<_>>();

    let node_colors = object
        .get_key_value("colors")
        .unwrap()
        .1
        .as_array()
        .unwrap()
        .iter()
        .map(|c| c.as_u64().unwrap() as usize)
        .collect::<Vec<_>>();

    let color_count = node_colors.iter().max().unwrap().clone() + 1;

    let mut colors: Vec<BitSet<u32>> = Vec::new();

    for color in 0..color_count {
        let mut bitset = BitSet::new();
        for (i, &node_color) in node_colors.iter().enumerate() {
            if node_color == color {
                bitset.insert(i);
            }
        }
        colors.push(bitset);
    }

    let graph = Graph {
        colors: colors,
        neighbours: neighbours,
    };

    let mut solver = GraphSinglePlayerSolver::new(graph, start);

    let solution = solver.solve();
    print!("Solution: ");
    for &move_ in &solution.moves {
        print!("{} ", move_);
    }
    println!();

    Ok(())
}
