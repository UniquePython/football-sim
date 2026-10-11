from __future__ import annotations

from collections.abc import Sequence


def min_cost_assignment(cost: Sequence[Sequence[float]]) -> list[int]:
    rows = len(cost)
    if rows == 0:
        raise ValueError("Cost table must have at least one row")

    columns = len(cost[0])
    if any(len(row) != columns for row in cost):
        raise ValueError("Every row of the cost table must have the same length")
    if columns < rows:
        raise ValueError(f"Need at least as many columns as rows: {columns} < {rows}")

    # Index 0 is a sentinel in every array below, so rows and columns are 1-based.
    row_price = [0.0] * (rows + 1)
    column_price = [0.0] * (columns + 1)
    row_of_column = [0] * (columns + 1)  # 0 means the column is still free
    previous_column = [0] * (columns + 1)

    for row in range(1, rows + 1):
        row_of_column[0] = row
        column = 0
        slack = [float("inf")] * (columns + 1)
        visited = [False] * (columns + 1)

        # Grow a tree of alternating paths until it reaches a free column.
        while True:
            visited[column] = True
            current_row = row_of_column[column]
            step = float("inf")
            next_column = 0

            for candidate in range(1, columns + 1):
                if visited[candidate]:
                    continue

                reduced = (
                    cost[current_row - 1][candidate - 1]
                    - row_price[current_row]
                    - column_price[candidate]
                )
                if reduced < slack[candidate]:
                    slack[candidate] = reduced
                    previous_column[candidate] = column
                if slack[candidate] < step:
                    step = slack[candidate]
                    next_column = candidate

            # Adjust prices so that at least one new zero appears.
            for c in range(columns + 1):
                if visited[c]:
                    row_price[row_of_column[c]] += step
                    column_price[c] -= step
                else:
                    slack[c] -= step

            column = next_column
            if row_of_column[column] == 0:
                break

        # Flip the matching along the path that was found.
        while column != 0:
            earlier = previous_column[column]
            row_of_column[column] = row_of_column[earlier]
            column = earlier

    chosen = [0] * rows
    for column in range(1, columns + 1):
        if row_of_column[column] != 0:
            chosen[row_of_column[column] - 1] = column - 1

    return chosen
