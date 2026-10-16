"""
Exercise 1 - Longest unique window

Part A:
Return the length of the longest contiguous subarray containing no duplicate
values. Aim for O(n) time.

Part B (follow-up):
Return the actual longest contiguous subarray. If several windows have the
same maximum length, return the earliest one.

Examples:
    [1, 2, 3, 2, 4, 5] -> length 4 and window [3, 2, 4, 5]
    [7, 7, 7]          -> length 1 and window [7]
    []                 -> length 0 and window []

Interview remarks:
- Maintain a sliding window [left, right] whose values are all unique.
- The set stores the individual values in the current window, not the window
  list itself.
- When values[right] is already present, move left forward and remove values
  until the duplicate is gone.
- The scan is O(n), even though it contains a nested while loop: every value
  enters the set once and leaves it at most once.
- Updating the best window only when its length is strictly greater preserves
  the earliest window when there is a tie.
- Returning the slice in Part B takes O(k) time and space, where k is the
  length of the returned window.
"""


def longest_unique_window_length(values: list[int]) -> int:
    """Return the length of the longest contiguous all-unique window."""
    seen: set[int] = set()
    left = 0
    best_length = 0

    for right, value in enumerate(values):
        while value in seen:
            seen.remove(values[left])
            left += 1

        seen.add(value)
        current_length = right - left + 1
        best_length = max(best_length, current_length)

    return best_length


def longest_unique_window(values: list[int]) -> list[int]:
    """Return the earliest longest contiguous all-unique window."""
    seen: set[int] = set()
    left = 0
    best_start = 0
    best_length = 0

    for right, value in enumerate(values):
        while value in seen:
            seen.remove(values[left])
            left += 1

        seen.add(value)
        current_length = right - left + 1

        if current_length > best_length:
            best_start = left
            best_length = current_length

    return values[best_start : best_start + best_length]


def run_tests() -> None:
    length_cases = [
        ([1, 2, 3, 2, 4, 5], 4),
        ([7, 7, 7], 1),
        ([], 0),
        ([1, 2, 3, 4], 4),
        ([1, 2, 1, 3], 3),
    ]

    for values, expected in length_cases:
        actual = longest_unique_window_length(values)
        assert actual == expected, (values, actual, expected)

    window_cases = [
        ([1, 2, 3, 2, 4, 5], [3, 2, 4, 5]),
        ([7, 7, 7], [7]),
        ([], []),
        ([1, 2, 3, 4], [1, 2, 3, 4]),
        ([1, 2, 1, 3], [2, 1, 3]),
        ([1, 2, 1, 2], [1, 2]),  # Earliest maximum window in a tie.
    ]

    for values, expected in window_cases:
        actual = longest_unique_window(values)
        assert actual == expected, (values, actual, expected)


if __name__ == "__main__":
    run_tests()
    print("All longest-unique-window tests passed.")
