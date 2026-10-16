"""
Exercise 2 - Merge intervals

Given a list of valid (start, end) intervals, merge every pair of overlapping
intervals. Intervals that merely touch must also be merged. Return the merged
intervals in ascending order of their start values.

Examples:
    [(1, 3), (2, 6), (8, 10), (10, 12)] -> [(1, 6), (8, 12)]
    [(5, 7), (1, 2), (2, 4)]            -> [(1, 4), (5, 7)]
    []                                   -> []

Assumption:
    Every interval is valid, meaning start <= end.

Interview remarks:
- Sort by start value so that the last merged interval is the only interval
  that the current interval can overlap.
- Use <= in the overlap check because touching intervals must be merged.
- list.sort() mutates its list, while sorted(...) returns a new list. Using
  sorted(...) here keeps the caller's input unchanged.
- Assignment does not copy a list: copy = original makes both names refer to
  the same object. Use sorted(...), original.copy(), or list(original) when a
  separate list is required.
- Sorting costs O(n log n); the merge scan costs O(n). Overall time is
  O(n log n), and space is O(n) for the sorted copy and result.
"""


def merge_intervals(
    intervals: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return merged intervals without modifying the input list."""
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda interval: interval[0])
    merged = [sorted_intervals[0]]

    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]

        if current_start <= last_end:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))

    return merged


def run_tests() -> None:
    cases = [
        (
            [(1, 3), (2, 6), (8, 10), (10, 12)],
            [(1, 6), (8, 12)],
        ),
        (
            [(5, 7), (1, 2), (2, 4)],
            [(1, 4), (5, 7)],
        ),
        ([], []),
        ([(1, 5)], [(1, 5)]),
        ([(1, 10), (2, 3), (4, 8)], [(1, 10)]),
        ([(1, 2), (3, 4)], [(1, 2), (3, 4)]),
    ]

    for intervals, expected in cases:
        original = intervals.copy()
        actual = merge_intervals(intervals)
        assert actual == expected, (intervals, actual, expected)
        assert intervals == original, "merge_intervals modified its input"


if __name__ == "__main__":
    run_tests()
    print("All merge-interval tests passed.")
