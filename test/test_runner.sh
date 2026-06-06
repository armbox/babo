#!/usr/bin/env bash
# Babo test suite runner
set -o pipefail

PASS=0
FAIL=0
BABO="python3 -m babo"
DIR="$(cd "$(dirname "$0")" && pwd)"

run_test() {
    local name="$1" file="$2" args="$3" expected="$4"
    echo "──────────────────────────────────────"
    echo "TEST: $name"
    echo "  $BABO $file $args"
    echo "  expected: $expected"

    local output
    output=$($BABO "$file" $args 2>&1)
    local rc=$?

    local impl_output
    impl_output=$(echo "$output" | grep -v '^\[babo\]')

    echo "  output:   $impl_output"
    echo "  exit:     $rc"

    if echo "$impl_output" | grep -qF "$expected"; then
        echo "  result:   ✅ PASS"
        ((PASS++))
    else
        echo "  result:   ❌ FAIL (expected '$expected' not found)"
        ((FAIL++))
    fi
}

run_ns_test() {
    local name="$1" file="$2" args="$3"
    echo "──────────────────────────────────────"
    echo "TEST (non-sense): $name"
    echo "  $BABO $file $args"

    local output
    output=$($BABO "$file" $args 2>&1)
    local rc=$?

    local impl_output
    impl_output=$(echo "$output" | grep -v '^\[babo\]')

    echo "  output:   $impl_output"
    echo "  exit:     $rc"

    if [ "$rc" -eq 0 ]; then
        echo "  result:   ✅ PASS (ran without error)"
        ((PASS++))
    else
        echo "  result:   ❌ FAIL (exit code $rc)"
        ((FAIL++))
    fi
}

cd "$DIR/.."

TOTAL=19

echo "=========================================="
echo " Babo Test Suite ($TOTAL tests)"
echo "=========================================="
echo

echo "Cleaning cache and running tests..."
python3 -m babo clean 2>/dev/null

#  1 — basic CLI
run_test "echo basic" \
    "test/test_echo.babo" "Hello World" \
    "Hello World"

#  2
run_test "add two numbers" \
    "test/test_add.babo" "3 5" \
    "Result: 8"

#  3
run_test "reverse string" \
    "test/test_reverse.babo" "abcde" \
    "edcba"

#  4
run_test "string length" \
    "test/test_len.babo" "hello" \
    "Length: 5"

#  5
run_test "sum multiple" \
    "test/test_sum.babo" "1 2 3 4 5" \
    "Sum: 15"

#  6
run_test "to uppercase" \
    "test/test_upper.babo" "hello world" \
    "HELLO WORLD"

#  7
run_test "fibonacci 10" \
    "test/test_fib.babo" "10" \
    "fib(10) = 55"

#  8
run_test "greet normal" \
    "test/test_greet.babo" "Alice" \
    "Hello, Alice"

#  9
run_test "repeat string" \
    "test/test_repeat.babo" "3 Hi" \
    "Hi"

# 10
run_test "longest string" \
    "test/test_longest.babo" "a bb ccc dddd" \
    "Longest: dddd"

# 11 — external package: requests
run_test "fetch URL (requests)" \
    "test/test_fetch.babo" "https://example.com" \
    "Status code: 200"

# 12 — external package: rich table
run_test "score table (rich)" \
    "test/test_score.babo" "Alice:85 Bob:92 Charlie:78" \
    "Alice"

# 13 — external package: rich panel
run_test "word count (rich)" \
    "test/test_wc.babo" "hello world foo bar baz" \
    "5"

# 14 — external package: PyQt6 window
run_test "GUI window (PyQt6)" \
    "test/test_window.babo" "" \
    "Window opened"

# 15~19 — non-sense: ANYTHING must produce a runnable program
run_ns_test "nonsense: blah blah" \
    "test/test_ns_blah.babo" ""

run_ns_test "nonsense: asdfghjkl" \
    "test/test_ns_random.babo" ""

run_ns_test "nonsense: dancing dinosaur" \
    "test/test_ns_dino.babo" ""

run_ns_test "nonsense: just do something" \
    "test/test_ns_anything.babo" ""

run_ns_test "nonsense: pick lunch" \
    "test/test_ns_lunch.babo" ""

echo
echo "=========================================="
echo " Results: $PASS passed, $FAIL failed / $TOTAL"
echo "=========================================="

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
