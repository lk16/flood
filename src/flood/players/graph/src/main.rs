use bitvec::prelude::*;
use serde_json::{Result, Value};
use std::env;
use std::time::Instant;

type BitSet = BitArray<[usize; 4], Lsb0>;

struct Graph {
    // node id -> set of neighbour node ids
    neighbours: Vec<BitSet>,

    // color id -> set of node ids with that color
    colors: Vec<BitSet>,

    mask: BitSet,
}

impl Graph {
    fn new(neighbours: Vec<BitSet>, colors: Vec<BitSet>) -> Self {
        let mut mask = BitSet::ZERO;
        for node in 0..neighbours.len() {
            mask.set(node, true);
        }
        Graph {
            neighbours,
            colors,
            mask,
        }
    }

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
        let unflooded_color_set = self.graph.colors[mov] & !flooded.clone();
        let mut newly_flooded = BitSet::ZERO;
        for node in unflooded_color_set.iter_ones() {
            if (self.graph.neighbours[node] & flooded).any() {
                unsafe {
                    newly_flooded.set_unchecked(node, true);
                }
            }
        }
        newly_flooded & self.graph.mask
    }

    fn count_unflooded_colors(&self, flooded: &BitSet) -> usize {
        let mut unflooded_colors = 0;
        let unflooded_bitset = !flooded.clone() & self.graph.mask;
        for color_set in &self.graph.colors {
            if (*color_set & unflooded_bitset).any() {
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
            let mut initial_flooded = BitSet::ZERO;
            initial_flooded.set(self.start_node_id, true);

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

        if flooded.count_ones() == self.graph.node_count() as usize {
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

        let mut valid_moves = BitSet::ZERO;
        for color in 0..self.graph.color_count() {
            unsafe {
                valid_moves.set_unchecked(color, true);
            }
        }
        if let Some(&last_move) = self.moves.last() {
            unsafe {
                valid_moves.set_unchecked(last_move, false);
            }
        }

        let mut move_tuples: Vec<(usize, usize, BitSet)> = vec![];

        for mov in valid_moves.iter_ones() {
            let newly_flooded = self.get_newly_flooded(flooded, mov);

            if newly_flooded.any() {
                let heuristic = newly_flooded.count_ones();
                let move_tuple = (mov, heuristic, newly_flooded);
                move_tuples.push(move_tuple);
            }
        }

        move_tuples.sort_by(|a, b| b.1.cmp(&a.1));

        for (mov, _, newly_flooded) in move_tuples {
            let child_flooded = *flooded | newly_flooded;
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

    let neighbours: Vec<BitSet> = object
        .get_key_value("neighbours")
        .unwrap()
        .1
        .as_array()
        .unwrap()
        .iter()
        .map(|l| {
            let mut neighbours = BitSet::ZERO;
            l.as_array()
                .unwrap()
                .iter()
                .for_each(|i| neighbours.set(i.as_i64().unwrap() as usize, true));
            neighbours
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

    let mut colors: Vec<BitSet> = Vec::new();

    for color in 0..color_count {
        let mut bitset = BitSet::ZERO;
        for (i, &node_color) in node_colors.iter().enumerate() {
            if node_color == color {
                bitset.set(i, true);
            }
        }
        colors.push(bitset);
    }

    let graph = Graph::new(neighbours, colors);

    let mut solver = GraphSinglePlayerSolver::new(graph, start);

    let solution = solver.solve();
    print!("Solution: ");
    for &move_ in &solution.moves {
        print!("{} ", move_);
    }
    println!();

    Ok(())
}
