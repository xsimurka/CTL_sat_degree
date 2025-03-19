from src.satisfaction_degree import weighted_signed_distance


def test_signed_weighted_distance():
    dov = [
        [0, 1, 4, 5],      # Holes between 1-4
        [2, 3, 4],         # Continuous 2-4
        [1, 3, 7, 8, 9]    # Holes: 1-3 (gap 1), 3-7 (gap 3)
    ]
    weights = [0.5, 0.3, 0.2]
    maxes = [5, 5, 9]

    # --- INSIDE TEST CASES ---
    # Fully inside, at an admissible point, far from boundaries
    state = (4, 3, 7)
    print(f"Test 1 - Inside, at boundary: {weighted_signed_distance(dov, state, maxes)} (Expected: 0)")

    # Inside, but at boundary (hole starts after in dim 0)
    state = (1, 3, 3)
    # Closest boundary in dim 0: hole starts after 1 (to 4), distance 4-1-1=2 (weighted 1)
    # Closest boundary in dim 2: hole starts after 3 (to 7), distance 7-3-1=3 (weighted 0.6)
    # Min weighted distance is 1 (dim 0)
    print(f"Test 2 - Inside, at boundary: {weighted_signed_distance(dov, state, maxes)} (Expected: 0)")

    # Inside, but "trapped" between holes
    state = (5, 3, 8)
    # dim 0: 5 → hole next? no → after 5 no values → upper_gap=inf, lower_gap=4 (distance 5-4-1=0)
    # dim 1: 3 → fully continuous → 0
    # dim 2: 8 → hole before: 7-8-1=-2 (invalid), hole after: 9-8-1=0
    # nearest hole is 0 → weighted min distance is 0
    print(f"Test 3 - Inside at upper edge: {weighted_signed_distance(dov, state, maxes)} (Expected: 0)")

    # Inside, in middle, close to no boundary
    state = (0, 3, 1)
    # dim 0: 0 → lower boundary → no values below → upper_gap=1-0-1=0
    # dim 2: 1 → hole after: 3-1-1=1 → weighted 0.2
    # min is 0
    print(f"Test 4 - Inside at lower edge: {weighted_signed_distance(dov, state, maxes)} (Expected: 0)")

    # --- OUTSIDE TEST CASES ---
    # Outside in dim 1 and dim 2
    state = (4, 5, 6)
    # dim 1: 5 → beyond max (4) → dist = 5-4=1 → weighted 0.3
    # dim 2: 6 → between 3 and 7 → min(6-3=3, 7-6=1) → weighted 0.2
    # dim 0: inside
    # sum = 0.3 + 0.2 = 0.5 → expected -0.5
    print(f"Test 5 - Outside dim 1 and dim 2: {weighted_signed_distance(dov, state, maxes)} (Expected: -0.5)")

    # Outside in dim 0 and dim 2
    state = (3, 3, 6)
    # dim 0: 3 → between 1 and 4 → min(3-1=2, 4-3=1) → weighted 0.5
    # dim 2: 6 → between 3 and 7 → min(6-3=3, 7-6=1) → weighted 0.2
    # dim 1: inside
    # sum = 0.5 + 0.2 = 0.7 → expected -0.7
    print(f"Test 6 - Outside dim 0 and dim 2: {weighted_signed_distance(dov, state, maxes)} (Expected: -0.7)")

    # Completely outside all dimensions
    state = (6, 1, 0)
    # dim 0: 6 > 5 → min(6-5=1) → weighted 0.5
    # dim 1: 1 < 2 → min(2-1=1) → weighted 0.3
    # dim 2: 0 < 1 → min(1-0=1) → weighted 0.2
    # sum = 0.5 + 0.3 + 0.2 = 1.0 → expected -1.0
    print(f"Test 7 - Outside all dimensions: {weighted_signed_distance(dov, state, maxes)} (Expected: -1.0)")

    # On the exact boundary, last admissible value in dim 0
    state = (5, 3, 7)
    # dim 0: 5 → no hole after → upper_gap=inf, lower_gap=5-4-1=0 → min 0
    # dim 1: inside
    # dim 2: inside
    # min = 0 → expected 0
    print(f"Test 8 - Inside, at boundary edge: {weighted_signed_distance(dov, state, maxes)} (Expected: 0)")

    # In a hole between admissible values
    state = (2, 3, 4)
    # dim 0: 2 between 1 and 4 → min(2-1=1, 4-2=2) → weighted 0.5
    # dim 1: inside
    # dim 2: 4 → between 3 and 7 → min(4-3=1, 7-4=3) → weighted 0.2
    # sum = 0.5 + 0.2 = 0.7 → expected -0.7
    print(f"Test 9 - In hole dim 0, inside elsewhere: {weighted_signed_distance(dov, state, maxes)} (Expected: -0.7)")

    # Inside but exactly between two points in dim 2 that create a hole
    state = (1, 5, 0)
    # dim 0: 0 → inside, next hole is 1-0-1=0 → weighted 0.5*0=0
    # dim 1: 2 → inside, continuous → weighted 0.3*0=0
    # dim 2: 5 is between 3 and 7 → hole, outside → min(5-3=2, 7-5=2) → weighted 0.2*2=0.4
    # sum = 0.4 → expected -0.4
    print(f"Test 10 - Outside in dim 2 hole: {weighted_signed_distance(dov, state, maxes)} (Expected: -0.4)")

test_signed_weighted_distance()