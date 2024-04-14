use serde_json::{Result, Value};
use std::env;
use std::time::Instant;

#[derive(Default)]
struct BitSet {
    data: [u64; 3],
}

impl BitSet {
    fn new() -> Self {
        BitSet { data: [0; 3] }
    }

    fn array_size(&self) -> usize {
        self.data.len()
    }

    fn element_bit_size(&self) -> usize {
        8 * std::mem::size_of_val(&self.data[0])
    }

    fn check_bounds(&self, offset: usize) {
        if offset >= self.array_size() * self.element_bit_size() {
            panic!("Offset is too big. Consider resizing BitSet!")
        }
    }

    unsafe fn set_unchecked(&mut self, offset: usize) {
        let mask = 1 << (offset % self.element_bit_size());
        let index = offset / self.element_bit_size();
        self.data[index] |= mask;
    }

    unsafe fn reset_unchecked(&mut self, offset: usize) {
        let mask = 1 << (offset % self.element_bit_size());
        let index = offset / self.element_bit_size();
        self.data[index] &= !mask;
    }

    fn set(&mut self, offset: usize) {
        self.check_bounds(offset);
        unsafe {
            self.set_unchecked(offset);
        }
    }

    fn difference(&self, other: &BitSet) -> BitSet {
        let mut difference = BitSet::new();
        for index in 0..self.array_size() {
            difference.data[index] = self.data[index] & !other.data[index]
        }
        difference
    }

    fn intersection(&self, other: &BitSet) -> BitSet {
        let mut intersection = BitSet::new();
        for index in 0..self.array_size() {
            intersection.data[index] = self.data[index] & other.data[index]
        }
        intersection
    }

    fn union(&self, other: &BitSet) -> BitSet {
        let mut union = BitSet::new();
        for index in 0..self.array_size() {
            union.data[index] = self.data[index] | other.data[index]
        }
        union
    }

    fn count_ones(&self) -> usize {
        self.data
            .iter()
            .map(|item| item.count_ones() as usize)
            .sum()
    }

    fn any(&self) -> bool {
        for item in self.data.iter() {
            if *item != 0 {
                return true;
            }
        }
        false
    }

    fn iter_ones(&self) -> BitSetIterator {
        BitSetIterator {
            bitset: self,
            word_index: 0,
            bit_index: 0,
        }
    }
}

pub struct BitSetIterator<'a> {
    bitset: &'a BitSet,
    word_index: usize,
    bit_index: usize,
}

impl<'a> Iterator for BitSetIterator<'a> {
    type Item = usize;

    fn next(&mut self) -> Option<Self::Item> {
        while self.word_index < self.bitset.data.len() {
            let word = self.bitset.data[self.word_index];
            while self.bit_index < self.bitset.element_bit_size() {
                if word & (1 << self.bit_index) != 0 {
                    let index = self.word_index * self.bitset.element_bit_size() + self.bit_index;
                    self.bit_index += 1;
                    return Some(index);
                }
                self.bit_index += 1;
            }
            self.word_index += 1;
            self.bit_index = 0;
        }
        None
    }
}
struct Graph {
    // node id -> set of neighbour node ids
    neighbours: Vec<BitSet>,

    // color id -> set of node ids with that color
    colors: Vec<BitSet>,
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
        for node in unflooded_color_set.iter_ones() {
            if self.graph.neighbours[node].intersection(flooded).any() {
                unsafe {
                    newly_flooded.set_unchecked(node);
                }
            }
        }
        newly_flooded
    }

    fn count_unflooded_colors(&self, flooded_bitset: &BitSet) -> usize {
        let mut unflooded_colors = 0;
        for color_set in &self.graph.colors {
            if color_set.difference(flooded_bitset).count_ones() > 0 {
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
            initial_flooded.set(self.start_node_id);

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

        let mut valid_moves = BitSet::new();
        for node in 0..self.graph.color_count() {
            unsafe {
                valid_moves.set_unchecked(node);
            }
        }
        if let Some(&last_move) = self.moves.last() {
            unsafe {
                valid_moves.reset_unchecked(last_move);
            }
        }

        let mut move_tuples: Vec<(usize, usize, BitSet)> = vec![];

        for mov in valid_moves.iter_ones() {
            let newly_flooded = self.get_newly_flooded(flooded, mov);
            let heuristic = newly_flooded.count_ones();

            if newly_flooded.any() {
                let move_tuple = (mov, heuristic, newly_flooded);
                move_tuples.push(move_tuple);
            }
        }

        move_tuples.sort_by(|a, b| b.1.cmp(&a.1));

        for (mov, _, newly_flooded) in move_tuples {
            let child_flooded = flooded.union(&newly_flooded);
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

    let neighbours = object
        .get_key_value("neighbours")
        .unwrap()
        .1
        .as_array()
        .unwrap()
        .iter()
        .map(|l| {
            let mut bitset = BitSet::new();
            l.as_array().unwrap().iter().for_each(|i| {
                let offset = i.as_u64().unwrap() as usize;
                if offset >= bitset.array_size() * bitset.element_bit_size() {
                    panic!("Offset too big, consider resizing BitSet.")
                }
                bitset.set(offset);
            });
            bitset
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
        let mut bitset = BitSet::new();
        for (i, &node_color) in node_colors.iter().enumerate() {
            if node_color == color {
                bitset.set(i);
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
