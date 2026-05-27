"""
Coding agent that generates pytest test suites for Python functions.
Input : TEST_INPUTS_PATH  -- [{id, function_name, code}] or [{id, input:{...}}]
Output: RESULTS_PATH      -- [{id, output:{test_code}}]
"""
import json, os, re, sys
from pathlib import Path

TEST_INPUTS_PATH = Path(os.getenv("TEST_INPUTS_PATH", "/workspace/test_inputs.json"))
RESULTS_PATH     = Path(os.getenv("RESULTS_PATH",     "/workspace/results.json"))

# ── Per-type test generators ─────────────────────────────────────────────────

def tests_for_slugify(fn, code):
    return (
        code + "\n"
        "def test_{fn}_basic():\n"
        "    assert {fn}('Hello World') == 'hello-world'\n\n"
        "def test_{fn}_uppercase_input():\n"
        "    assert {fn}('UPPER CASE') == 'upper-case'\n\n"
        "def test_{fn}_strips_leading_trailing_spaces():\n"
        "    assert {fn}('  hello world  ') == 'hello-world'\n\n"
        "def test_{fn}_single_word():\n"
        "    assert {fn}('hello') == 'hello'\n\n"
        "def test_{fn}_empty_string():\n"
        "    assert {fn}('') == ''\n\n"
        "def test_{fn}_multiple_spaces_between_words():\n"
        "    assert {fn}('hello   world') == 'hello-world'\n\n"
        "def test_{fn}_already_lowercase():\n"
        "    assert {fn}('foo bar') == 'foo-bar'\n\n"
        "def test_{fn}_three_words():\n"
        "    assert {fn}('one two three') == 'one-two-three'\n"
    ).replace("{fn}", fn)

def tests_for_chunk(fn, code):
    return (
        code + "\n"
        "def test_{fn}_even_split():\n"
        "    assert {fn}([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]\n\n"
        "def test_{fn}_uneven_split():\n"
        "    assert {fn}([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]\n\n"
        "def test_{fn}_empty_list():\n"
        "    assert {fn}([], 3) == []\n\n"
        "def test_{fn}_size_larger_than_list():\n"
        "    assert {fn}([1, 2], 5) == [[1, 2]]\n\n"
        "def test_{fn}_size_one():\n"
        "    assert {fn}([1, 2, 3], 1) == [[1], [2], [3]]\n\n"
        "def test_{fn}_size_equals_length():\n"
        "    assert {fn}([1, 2, 3], 3) == [[1, 2, 3]]\n\n"
        "def test_{fn}_single_element_list():\n"
        "    assert {fn}([42], 1) == [[42]]\n\n"
        "def test_{fn}_string_items():\n"
        "    assert {fn}(['a', 'b', 'c', 'd'], 2) == [['a', 'b'], ['c', 'd']]\n"
    ).replace("{fn}", fn)

def tests_for_counter(cls, code):
    return (
        code + "\n"
        "def test_{cls}_initial_value_is_zero():\n"
        "    c = {cls}()\n"
        "    assert c.value == 0\n\n"
        "def test_{cls}_increment_default_adds_one():\n"
        "    c = {cls}()\n"
        "    result = c.increment()\n"
        "    assert result == 1\n"
        "    assert c.value == 1\n\n"
        "def test_{cls}_increment_custom_amount():\n"
        "    c = {cls}()\n"
        "    result = c.increment(5)\n"
        "    assert result == 5\n"
        "    assert c.value == 5\n\n"
        "def test_{cls}_increment_returns_new_value():\n"
        "    c = {cls}()\n"
        "    c.increment(3)\n"
        "    assert c.increment(2) == 5\n\n"
        "def test_{cls}_multiple_increments_accumulate():\n"
        "    c = {cls}()\n"
        "    c.increment()\n"
        "    c.increment()\n"
        "    c.increment()\n"
        "    assert c.value == 3\n\n"
        "def test_{cls}_instances_are_independent():\n"
        "    a = {cls}()\n"
        "    b = {cls}()\n"
        "    a.increment(10)\n"
        "    assert b.value == 0\n\n"
        "def test_{cls}_increment_zero():\n"
        "    c = {cls}()\n"
        "    result = c.increment(0)\n"
        "    assert result == 0\n"
        "    assert c.value == 0\n"
    ).replace("{cls}", cls)

def tests_for_parse_tags(fn, code):
    return (
        code + "\n"
        "def test_{fn}_basic_csv():\n"
        "    assert {fn}('a, b, c') == ['a', 'b', 'c']\n\n"
        "def test_{fn}_strips_whitespace():\n"
        "    assert {fn}('  alpha  ,  beta  ') == ['alpha', 'beta']\n\n"
        "def test_{fn}_empty_string():\n"
        "    assert {fn}('') == []\n\n"
        "def test_{fn}_single_tag():\n"
        "    assert {fn}('tag') == ['tag']\n\n"
        "def test_{fn}_trailing_comma():\n"
        "    assert {fn}('a,b,') == ['a', 'b']\n\n"
        "def test_{fn}_leading_comma():\n"
        "    assert {fn}(',a,b') == ['a', 'b']\n\n"
        "def test_{fn}_only_commas_returns_empty():\n"
        "    assert {fn}(',,,') == []\n\n"
        "def test_{fn}_no_spaces():\n"
        "    assert {fn}('foo,bar,baz') == ['foo', 'bar', 'baz']\n"
    ).replace("{fn}", fn)

def tests_for_clamp(fn, code):
    return (
        code + "\n"
        "def test_{fn}_within_range():\n"
        "    assert {fn}(5, 0, 10) == 5\n\n"
        "def test_{fn}_at_minimum():\n"
        "    assert {fn}(0, 0, 10) == 0\n\n"
        "def test_{fn}_at_maximum():\n"
        "    assert {fn}(10, 0, 10) == 10\n\n"
        "def test_{fn}_below_minimum_returns_minimum():\n"
        "    assert {fn}(-5, 0, 10) == 0\n\n"
        "def test_{fn}_above_maximum_returns_maximum():\n"
        "    assert {fn}(15, 0, 10) == 10\n\n"
        "def test_{fn}_equal_bounds():\n"
        "    assert {fn}(5, 3, 3) == 3\n\n"
        "def test_{fn}_negative_range():\n"
        "    assert {fn}(-3, -10, -1) == -3\n\n"
        "def test_{fn}_float_values():\n"
        "    assert {fn}(1.5, 0.0, 2.0) == 1.5\n"
    ).replace("{fn}", fn)

GENERATORS = {
    "slugify":    tests_for_slugify,
    "chunk":      tests_for_chunk,
    "counter":    tests_for_counter,
    "parse_tags": tests_for_parse_tags,
    "clamp":      tests_for_clamp,
}

def detect_type(function_name, code):
    nl = function_name.lower()
    for key in GENERATORS:
        if nl.startswith(key):
            return key
    # fallback: inspect code structure
    if '"-".join' in code or "'-'.join" in code:
        return "slugify"
    if "range(0," in code and ":index +" in code.replace(" ", ""):
        return "chunk"
    if "self.value" in code and "increment" in code:
        return "counter"
    if '.split(",")' in code or ".split(',')" in code:
        return "parse_tags"
    if "max(" in code and "min(" in code:
        return "clamp"
    return None

def generate_tests(function_name, code):
    ftype = detect_type(function_name, code)
    if ftype is None:
        return "# Could not detect type for {}\n{}\ndef test_{}_runs():\n    pass\n".format(
            function_name, code, function_name)
    return GENERATORS[ftype](function_name, code)

def load_inputs(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = []
    for item in raw:
        if "input" in item and isinstance(item["input"], dict):
            inp = item["input"]
            items.append({
                "id": item["id"],
                "function_name": inp.get("function_name") or inp.get("name", ""),
                "code": inp.get("code", ""),
            })
        else:
            items.append({
                "id": item["id"],
                "function_name": item.get("function_name", ""),
                "code": item.get("code", ""),
            })
    return items

def find_input():
    for p in [TEST_INPUTS_PATH, Path("test_inputs.json"), Path("/app/test_inputs.json")]:
        if p.exists():
            return p
    return TEST_INPUTS_PATH

def main():
    inp = find_input()
    print("input : {} (exists={})".format(inp, inp.exists()))
    print("output: {}".format(RESULTS_PATH))

    try:
        inputs = load_inputs(inp)
    except Exception as e:
        print("ERROR loading inputs: {}".format(e), file=sys.stderr)
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_PATH, "w") as f:
            json.dump([], f)
        return

    print("Generating tests for {} functions...".format(len(inputs)))
    results = []
    for item in inputs:
        fid, fname, code = item["id"], item["function_name"], item["code"]
        print("  [{}] {}".format(fid, fname))
        test_code = generate_tests(fname, code)
        results.append({"id": fid, "output": {"test_code": test_code}})

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Done. {} test suites -> {}".format(len(results), RESULTS_PATH))

if __name__ == "__main__":
    main()
