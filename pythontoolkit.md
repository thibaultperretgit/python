# Python toolkit for quant coding interviews

Use this as a reference while practising, not as a list to memorize line by line. The **Must know** sections should become automatic. The later sections are common in data and market-making interviews. Examples assume Python 3.11+.

## 1. The Python mental model — must know

Variables are **names bound to objects**. Assignment does not copy an object.

```python
a = [1, 2]
b = a                 # Both names refer to the same list.
b.append(3)
assert a == [1, 2, 3]

c = a.copy()          # New outer list (shallow copy).
c.append(4)
assert a == [1, 2, 3]
```

Lists, dictionaries, and sets are mutable. Integers, strings, and tuples are immutable. A tuple can still *contain* a mutable object. A shallow copy duplicates only the outer container; use `copy.deepcopy(x)` when nested mutable objects must be independent.

```python
bad = [[0] * 3] * 3            # Three references to ONE inner list.
good = [[0] * 3 for _ in range(3)]  # Three independent inner lists.
```

Use `==` for equal **values** and `is` for the **same object**. The usual identity test is `x is None`, not `x == None`. In Python, `bool` is a subclass of `int`: `True == 1` is true, so validate strictly with `type(x) is int` if booleans must be rejected.

## 2. Everyday syntax and built-ins — must know

| Code | Meaning / important detail |
| --- | --- |
| `x = 7`, `x += 1` | Bind a name; update it using an augmented operation. |
| `a, b = b, a` | Swap two names without a temporary variable. |
| `if condition: ... elif ... else: ...` | Conditional branches. |
| `for x in items:` | Iterate over values directly. |
| `for i in range(n):` | Iterate over integers `0` through `n - 1`. |
| `for i, x in enumerate(items):` | Iterate with index and value. |
| `for a, b in zip(xs, ys):` | Pair values; stops at the shorter iterable by default. |
| `break` / `continue` | Leave a loop / skip to the next iteration. |
| `len(xs)`, `sum(xs)` | Length / arithmetic sum. `sum([]) == 0`. |
| `min(xs)`, `max(xs)` | Minimum / maximum; raise `ValueError` on an empty iterable unless `default=` is supplied. |
| `any(flags)`, `all(flags)` | At least one true / every item true. `all([])` is true. |
| `abs(x)`, `divmod(a, b)` | Absolute value / `(a // b, a % b)`. |
| `isinstance(x, int)` | Type check; also accepts `bool` as an integer. |
| `print(f"price={price:.2f}")` | Formatted string, two decimal places. Formatting does not change the underlying number. |

```python
if not values:                 # Empty list, dict, set, or string is false.
    return 0

for index, value in enumerate(values):
    print(index, value)
```

Truthiness is convenient, but distinguish `0`, `False`, `None`, and empty containers when they have different meanings. `and` and `or` short-circuit and return an operand, not necessarily a Boolean:

```python
name = supplied_name or "unknown"  # Also substitutes for an intentionally empty string.
```

## 3. Lists, tuples, strings, sets, dictionaries — must know

### Lists: ordered, mutable sequences

```python
xs = [10, 20, 30]
xs[0]                 # 10; indexing is O(1).
xs[-1]                # 30; last element.
xs[1:3]               # [20, 30]; stop index excluded, creates a new list.
xs[::-1]              # Reversed copy.
xs.append(40)         # Add one item at end; amortized O(1).
last = xs.pop()       # Remove last; O(1).
xs.sort()             # Sort this list in place; returns None.
copy_sorted = sorted(xs)  # New sorted list; original unchanged.
```

`xs.pop(0)` and `xs.insert(0, value)` are O(n) because elements shift. Use `collections.deque` for efficient operations at both ends. Slicing `xs[a:b]` costs O(b - a) time and space.

### Tuples: ordered, immutable containers

```python
point = (3, 5)
x, y = point
pair = ("AAPL", 100.0)  # Often useful as a dictionary key if each item is hashable.
```

### Strings: immutable text

```python
text = "  AAPL,MSFT  "
parts = text.strip().split(",")     # ["AAPL", "MSFT"]
joined = ",".join(parts)              # "AAPL,MSFT"
text.startswith("  AAPL")
```

For many concatenations, accumulate fragments in a list and use `"".join(fragments)`; repeatedly adding to a string can copy its contents many times.

### Sets: unique, hashable members

```python
seen = set()
seen.add(5)
5 in seen              # Average O(1).
seen.remove(5)         # Raises KeyError if absent.
seen.discard(5)        # Safe if absent.
```

A list cannot be a set member or dictionary key because it is mutable and unhashable. Do not rely on set iteration order for interview output.

### Dictionaries: key → value mappings

```python
volume_by_price = {}
volume_by_price[101] = volume_by_price.get(101, 0) + 5
volume_by_price.get(999, 0)       # 0 if key missing; does not insert it.

for price, volume in volume_by_price.items():
    print(price, volume)
```

Dictionary lookup, insertion, and set membership are O(1) **on average**, not guaranteed for every individual operation. Keys must be hashable. Modern Python preserves dictionary insertion order, but sort explicitly when numeric/key order is required. Do not change a dictionary's size while iterating over it; iterate over `list(d)` if you need to delete keys.

## 4. Comprehensions, generators, and functions — must know

```python
squares = [x * x for x in range(5)]
evens = [x for x in values if x % 2 == 0]
counts = {x: values.count(x) for x in set(values)}  # Clear but O(n²) in general.
unique = {x for x in values}
total = sum(x * x for x in values)  # Generator expression; no intermediate list.
```

Use a normal loop when a comprehension becomes hard to read. `sum(x * x for x in values)` still takes O(n) time; a generator only avoids the extra list.

```python
def spread(bid: float, ask: float) -> float:
    """Return the quoted spread; reject a crossed market."""
    if bid <= 0 or ask < bid:
        raise ValueError("invalid quote")
    return ask - bid
```

Type hints document intent but are not enforced automatically at runtime. `return` exits a function; falling off the end returns `None`. A docstring explains the contract, especially units, side conventions, and invalid inputs.

Avoid mutable default arguments:

```python
def add_trade(trade, history=None):
    if history is None:
        history = []
    history.append(trade)
    return history
```

`def add_trade(trade, history=[])` creates the list once, so later calls share it. For a dataclass field, use `field(default_factory=list)`.

`*args` collects positional arguments; `**kwargs` collects keyword arguments. A small `lambda x: x[0]` is useful as a sorting key. A closure captures names, not frozen values: lambdas built in a loop often all see the final loop value unless you bind it with a default argument.

### Exceptions and files

```python
from pathlib import Path

try:
    number = int("12")
except ValueError as exc:
    raise ValueError("expected an integer") from exc

with Path("notes.txt").open(encoding="utf-8") as file:
    text = file.read()
```

Catch the specific error you expect; a broad `except Exception:` can hide bugs. `with` closes the file even if an error occurs. A `while condition:` loop is useful when the number of repetitions is unknown; ensure some state changes toward termination. Recursion can express tree traversal, but Python's recursion depth is limited, so an explicit stack is often safer for deep inputs.

## 5. Sorting and complexity — must know

```python
intervals = [(5, 7), (1, 2), (2, 4)]
ordered = sorted(intervals, key=lambda interval: interval[0])
ordered_desc = sorted(intervals, key=lambda interval: interval[0], reverse=True)
```

Python sorting is stable: records with equal keys keep their original relative order. `sorted(...)` makes a new list; `list.sort()` mutates its list and returns `None`. Sorting takes O(n log n) time in the general/worst case; an already ordered input can be handled in O(n).

| Operation | Typical time | Extra space / note |
| --- | --- | --- |
| `xs[i]`, `xs.append(x)`, `xs.pop()` | O(1) amortized for append | `pop()` removes the end. |
| `xs[a:b]`, `x in xs` | O(k), O(n) | Slice copies `k` items; list search scans. |
| `x in seen`, `d[key]` | O(1) average | Hash table operations. |
| `sorted(xs)`, `xs.sort()` | O(n log n) worst case | `sorted` allocates a list; sorting may use more temporary memory. |
| `sum(xs)`, `max(xs)` | O(n) | One pass. |
| `deque.appendleft(x)`, `deque.popleft()` | O(1) | Efficient queue/deque ends. |
| `heapq.heappush/pop` | O(log n) | Min-heap. |
| `bisect_left(sorted_xs, x)` | O(log n) | Finding index only; inserting into a list is O(n). |

A nested `while` loop does not automatically imply O(n²): in a sliding window, each element may enter and leave the window once, giving O(n) total work. Always count sorting, copies, slicing, and returned output in your analysis.

## 6. Standard-library tools worth knowing

```python
from collections import Counter, defaultdict, deque
from bisect import bisect_left
import heapq

freq = Counter(["A", "B", "A"])      # {'A': 2, 'B': 1}
groups = defaultdict(list)
groups["A"].append(10)

queue = deque([1, 2])
queue.append(3)
first = queue.popleft()              # 1

heap = []
heapq.heappush(heap, (101.5, "AAPL"))
smallest = heapq.heappop(heap)

index = bisect_left([1, 3, 3, 7], 3)  # 1: first possible position.
```

Also useful: `itertools.accumulate` for prefix sums, `itertools.combinations` for pairs, `math.isclose` for approximate float comparison, `math.inf` for a sentinel, and `pathlib.Path` for files. `Counter` and `defaultdict` avoid repetitive initialization code; they do not remove the need to understand dictionary operations.

## 7. Interview patterns — must know

The goal is to recognize the invariant, then justify its complexity.

| Pattern | When to try it | Key idea |
| --- | --- | --- |
| Hash map / set | Fast lookup, frequencies, duplicates, two-sum | Store previously seen values; average O(1) lookup. |
| Two pointers | Sorted array, pair search, in-place partition | Move one boundary based on the comparison. |
| Sliding window | Contiguous range with a maintainable condition | Keep `[left, right]` valid; shrink from left when invalid. |
| Prefix sums | Sum of a contiguous range, including negatives | `sum(values[i:j]) = prefix[j] - prefix[i]`. |
| Sort then scan | Intervals, scheduling, grouping | Sorting reveals local relationships. |
| Binary search | Monotone condition or sorted data | Maintain a true/false boundary; halve the search space. |
| Heap | Repeated smallest/largest, top-k, event ordering | O(log n) insertion/removal. |
| BFS / DFS | Graph reachability, connected components | Queue for breadth first; stack/recursion for depth first. |

For target-sum subarrays, a sliding window does **not** work reliably when negative values are allowed. Prefix sums still work: a subarray ending now has sum `target` whenever an earlier prefix equals `current_prefix - target`. Think about how many times each earlier prefix occurred.

For merge intervals, sort by start and compare each interval with the last merged one. Touching intervals merge when `current_start <= last_end`.

For a unique-value window, a set can track the current window. When the next value is already inside, move the left boundary until the duplicate is removed. Save the best start and length if you need the actual subarray.

## 8. Classes and state — useful for market-making exercises

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Quote:
    ticker: str
    bid: float
    ask: float

@dataclass
class Book:
    inventory: dict[str, int] = field(default_factory=dict)
    quotes: list[Quote] = field(default_factory=list)

    def add_quote(self, quote: Quote) -> None:
        self.quotes.append(quote)
```

`self` is the current instance. An instance attribute belongs to one object; a class attribute can be shared across objects. `@dataclass` generates an initializer and representation; `frozen=True` prevents normal attribute reassignment. Keep invariants explicit: a quote should have `0 < bid <= ask`, and a filled trade should update cash, inventory, and history together.

## 9. NumPy and pandas — must know for dataset assessments

```python
from pathlib import Path
import market_simulator
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)       # Reproducible random generator.
samples = rng.normal(0, 1, size=100)
array = np.array([1.0, 2.0, 3.0])
array.mean()
array.std(ddof=1)                     # Sample standard deviation.
```

NumPy operations usually work elementwise over arrays. Avoid accidental broadcasting: check array shapes. `np.std` defaults to `ddof=0` (population convention); pandas `Series.std()` defaults to `ddof=1` (sample convention).

```python
data_dir = Path(market_simulator.__file__).resolve().parents[1] / "data"
df = pd.read_csv(data_dir / "market_prices.csv", parse_dates=["timestamp"])
df.head()
df.info()
df.isna().sum()                       # Missing values per column.
df.duplicated(["timestamp", "ticker"]).sum()

alfa = df.loc[df["ticker"] == "ALFA"].sort_values("timestamp")
returns = alfa["mid"].pct_change().dropna()
step_vol = returns.std()              # These synthetic observations are one minute apart.
# For DAILY returns only: annual_vol = returns.std() * np.sqrt(252)
```

Use `.loc[rows, columns]` for label-based selection and `.iloc[rows, columns]` for integer positions. `.copy()` after filtering when you intend to modify the result. `df.sort_values(...)` returns a new DataFrame unless `inplace=True`. `pct_change()` means `P_t / P_(t-1) - 1`; the first result is missing. `shift(1)` accesses the prior row after sorting. With timestamps, align time zones and dtypes before joining.

Given `requests`, `prices`, and `trades` DataFrames with the named columns:

```python
enriched = requests.merge(
    prices[["timestamp", "ticker", "mid"]],
    on=["timestamp", "ticker"],
    how="left",
    validate="many_to_one",
)
if enriched["mid"].isna().any():
    raise ValueError("some requests have no matching price")

volume_by_ticker = trades.groupby("ticker")["quantity"].sum()
rolling_mean = prices.sort_values("timestamp")["mid"].rolling(20).mean()
```

`validate="many_to_one"` catches duplicate price keys. A `left` join preserves requests and exposes missing matches; an `inner` join silently drops unmatched requests. `groupby` is useful for per-ticker aggregation. Do not use a future price when computing a decision at an earlier timestamp: that is look-ahead bias.

## 10. Financial calculations and direction conventions

For a maker, **buy** means buying from the client at the bid; **sell** means selling to the client at the ask. With quantity `q > 0`, execution price `p`, and transaction fee `fee`:

```python
delta = q if maker_action == "buy" else -q
inventory += delta
cash -= delta * p + fee

equity = cash + inventory * current_mid
total_pnl = equity - initial_cash
spread = ask - bid
quote_mid = (bid + ask) / 2  # Can differ from the market reference mid after skew.
```

Example: start with cash 1,000 and no shares; maker buys 2 at 99 with no fee. Cash becomes 802, inventory 2. At a mark of 100, equity is 1,002 and P&L is 2. Cash alone is **not** P&L when inventory is open.

Signed dollar exposure is `inventory * mid`; gross exposure is the sum of absolute position values. A long inventory can be encouraged to unwind by shifting both bid and ask **down**; a short inventory by shifting them **up**. Beta against a benchmark is `cov(asset_returns, benchmark_returns) / var(benchmark_returns)` after aligning dates and removing missing observations. It measures co-movement, not guaranteed hedge performance.

## 11. Testing, validation, and common traps

```python
assert spread(99, 101) == 2

import pytest
with pytest.raises(ValueError):
    spread(102, 101)
```

For interview code, test empty input, one element, duplicates, negative numbers, ties, already sorted input, invalid values, and large input where relevant. `assert` is useful in tests; do not rely on it for runtime input validation because Python can disable assertions with optimization.

- **Floating point:** `0.1 + 0.2 == 0.3` can be false. Use `math.isclose(...)` for approximate comparison; for production money calculations, integer ticks/cents or `decimal.Decimal` may be preferable.
- **NaN:** `float("nan") != float("nan")`; use `math.isnan` or `pd.isna`, not equality.
- **Mutation:** `a = b` aliases; `b.sort()` changes `b`; `sorted(b)` makes a new list; a shallow copy still shares nested objects.
- **Views vs copies:** pandas chained assignment can be ambiguous. Prefer `df.loc[mask, "column"] = value` or work on `df.loc[mask].copy()`.
- **Complexity:** `x in list` is O(n); `x in set` is O(1) average. A loop containing `list.count` can become O(n²).
- **Off-by-one:** Python slices exclude the stop index. An inclusive window `[left, right]` has length `right - left + 1`.
- **Output contract:** Decide whether ties require the earliest result, whether the function may mutate input, and what empty input should return.

## 12. A 60-second interview checklist

1. Restate the input, output, constraints, and any ambiguous tie or mutation rule.
2. Give a small example and an edge case before coding.
3. State the invariant or data structure: what does each variable mean at every step?
4. Write the simplest correct implementation, then test it on paper.
5. Explain time **and** space complexity, including sorting and copies.
6. If you discover a bug, say what failed and correct it openly.

The strongest preparation is to reproduce these patterns without looking, then explain *why* each one works. Keep the [exercise files](exercises/) and the [market-making notebooks](millennium-market-making-prep/notebooks/exercises/) as practice problems rather than just reading this guide.
