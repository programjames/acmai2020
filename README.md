# Placement (1st)

# Strategy
1. I make a qtable with a score for every location on the map. I update each of these scores hundreds of time according to the formula:
score = energium at this location + 0.9 * max(neighbor's scores)
2. Once a unit stops moving (i.e. it has found a local maxima), then it turns the energium at its location to -50 (the cost if a unit were to run into it).
3. If the "best move" a unit can do will kill it, choose a different "best move" (well, sort of... just change the score for that move to be -50).
4. Dodging. If an enemy is neighboring the unit and can kill it, move back to the base. It needs to be able to refresh itself and come back and kill the enemy unit.
5. Bases build units if they think that the unit will net a positive for the base.
For part 5, I don't take into account any units currently on the map or else if 4 units are surrounding the base then it won't build more units.


# External links:
This is the competition website:
https://ai.acmucsd.com/competitions/energium/ranks

Here's the link to the official repository in case you want to download it yourself:
https://github.com/acmucsd/energium-ai-2020

And here are some docs I made:
https://github.com/programjames/acmai2020docs/blob/gh-pages/index.md

And here's the final match in the tournament:
https://youtu.be/F58PdHZrR4w?t=1748
