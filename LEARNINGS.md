# What I Learned

1. I learned that 3D bin packing is much harder than it first appears because the search space grows quickly once you consider box dimensions, item rotations, and multiple items. Exact solutions become computationally expensive very quickly, so a heuristic approach is often the practical choice for this kind of assignment.
2. I had to balance correctness and simplicity. A greedy solver is easier to explain and test, but it can miss a valid packing even when one exists. I chose a transparent approach that is reliable enough for the assignment while keeping the implementation understandable.
3. The most challenging part was connecting the packing logic with Django’s model and API layers. The solver had to work naturally with the database models, generate persisted recommendations, and support both the dashboard and REST endpoints without creating inconsistent state.
4. Using AI helped me move faster by suggesting structure, boilerplate, and test ideas. It also required me to review each suggestion carefully, because some outputs were too generic or needed corrections before they were safe to use.
5. If I had more time, I would improve the packing algorithm to support more sophisticated placement heuristics and add richer validation for edge cases such as multi-box splitting and more complex order constraints.
