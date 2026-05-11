#!/usr/bin/env bash

pass_str="Program ok"

output=$(python3 run.py tests/ok-attrivutes.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-attrivutes"
else
    echo "Failed ok-attrivutes"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-comparisons.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-comparisons"
else
    echo "Failed ok-comparisons"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-count-digits.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-count-digits"
else
    echo "Failed ok-count-digits"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-counter.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-counter"
else
    echo "Failed ok-counter"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-extra-real-scoping.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-extra-real-scoping"
else
    echo "Failed ok-extra-real-scoping"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-factorial.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-factorial"
else
    echo "Failed ok-factorial"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-fibonacci.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-fibonacci"
else
    echo "Failed ok-fibonacci"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-func-defined-after-use.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-func-defined-after-use"
else
    echo "Failed ok-func-defined-after-use"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-number-game.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-number-game"
else
    echo "Failed ok-number-game"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-sum-iterative.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-sum-iterative"
else
    echo "Failed ok-sum-iterative"
    printf '%s\n' "$output"
fi

output=$(python3 run.py tests/ok-types.vec)
if [[ "$output" == *"$pass_str"* ]]; then
    echo "Passed ok-types"
else
    echo "Failed ok-types"
    printf '%s\n' "$output"
fi
