# Flood

Competition of bots to solve the Flood-it game.

### Game explanation
* The game starts with a grid of `w` by `h` that is separated into different regions with `c` colors.
* The player then needs to expand their region (usually starting in top left) by flooding it with different colors.
* The game ends when the region covers the entire grid.

You can play the game [here](https://flood-it.xyz/). There are also various other flash games and mobile apps implementing the this puzzle game.

---

### Single player game
- Try to find the shortest sequence of colors (also called moves) to flood the entire grid.
- A player cannot flood with their current color (no no-op moves)

### Two player game
- Players start their regions from two different points in the grid (usually opposing corners)
- The players take turns to flood
- A player cannot flood with the current color of of the opponent region
- A player cannot flood with their current color (no no-op moves)
- The game ends when the entire grid is flooded by the regions of the players
- The player whose region has the most cells wins.

### Rules applying to both
- If the game takes an excessive amount of moves to conclude, it will be ended.
- If the move takes an excessive amount of time to complete, it will be terminated. This will happen regardless of the `timeout` parameter of the `do_move()` function.
- We may add more rules here as loopholes get discovered by participants.
- See also the "rules for bots" section below"

---

### How to participate in bot competition
- If you're a contributor to this repo: clone this repo
- Otherwise: (ask to be a contributor) or fork this repo and clone it
- Create a branch of latest `main`
- Add your bot (see next section)
- Make a pull request on this repo

### How to add a bot
- Create a new file in `src/flood/players`
- Add a class that subclasses `BasePlayer` in `src/flood/players/base.py`
- Add your class to `PLAYER_TYPES` in `src/flood/main.py`
- Implement your own `def get_best_move()`, make sure to keep the same signature as in `BasePlayer`.
- If using a custom `__init__()`, make sure it takes no arguments, other than `self`.
- For some examples of implementations see other files in `src/flood/players`

### Rules for bots
- No stealing other people's code
-
