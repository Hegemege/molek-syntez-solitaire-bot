# About

Solver/bot for solitaire in MOLEK-SYNTEZ.

See it in action: https://www.youtube.com/watch?v=ZMZlUCtzZ9o

I primed this repo from my [Shenzhen I/O solitaire bot](https://github.com/Hegemege/shenzhen-solitaire-bot) and it took me only some 3.5h to convert that solver to this. I had to rewrite the rules and do some upkeep, but the basic idea is the same.

The solver uses a simple heuristic to solve, since the search space explodes due to the cheating moves and when empty stacks are formed. This is because there are many combinations of 2-3 moves that are possible in those circumstances that don't necessarily advance the game any further.

The bot simply executes the first solution it finds and does not try to find the shortest solution.


# Requirements

Requires Python 3 and a couple of packages

-   PIL (aka Pillow, Python Imaging Library)
-   pynput

Recommended to install them via pip (if you use Python for other development, please set up a new virtual env to avoid version conflicts, since some dependencies are forced to a specific version).

First, navigate to the directory where you cloned this repository to with the command `cd` (or on Windows, if you have installed Git Bash, you can right click to "Open Git Bash here", or Shift+Right click to open the command line in the directory with `solver.py`) and run

```
pip install -r requirements.txt
```

# Usage

1. Open up the game on your main monitor
    - Working resolutions (multimonitor should work)
        - Fullscreen 1080p, 1440p
        - Windowed 1080p (centered)
    - You might need to tweak some of the screen coordinates if you are using other resolutions, see `solver.py`
2. Open the Solitaire minigame (you must beat a couple of levels before you unlock it) and leave it in the background. Make sure the New Game button is visible
3. Open a terminal window in the cloned directory or navigate there otherwise (see [Requirements](#requirements) or Google)
4. Run `python solver.py` and Alt+Tab back into the game

The script runs 100 games by default whether it finds a solution or not, so you might need to run it again to reach 100 wins needed for the achievement. Or just tweak the parameter `RUN_COUNT` in `solver.py`.

You can also toggle the cheats off, so the bot won't attempt to make any cheating moves. Some of the game configurations may be unsolvable without cheating, so you might have to try again.

Best time to interrupt the script is during the new game shuffle, so just alt-tab back to your terminal and hit `Ctrl-C`.

Have fun!

P.S.
I would have distributed a binary .exe, but most of the python-to-exe conversions are flagged as trojans/malware, so I didn't bother.

# License

See LICENSE
