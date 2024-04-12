
# Graph Solver

### How to run with Rust?
* Install the Rust toolchain on your machine, [details here](https://www.rust-lang.org/tools/install).
* Compile the Rust solver, by running this from the repo root:
```sh
cargo build --manifest-path src/flood/players/graph/Cargo.toml --release
```
* Set this environment variable to enable the rust binary, for example:
```sh
FLOOD_GRAPH_PLAYER_USE_RUST=1 pdm run solve graph -d 0.5 -s 69 -w 14 -h 14 -c 6
```
* To run plain python code, don't set the env var:
```sh
pdm run solve graph -d 0.5 -s 69 -w 14 -h 14 -c 6
```
