#!/usr/bin/env bash

error_str="Error"

output=$(python3 run.py tests/not-ok-sem-attributes.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-attributes"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-attributes"
fi

output=$(python3 run.py tests/not-ok-sem-comparisons.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-comparisons"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-comparisons"
fi

output=$(python3 run.py tests/not-ok-sem-comparisons1.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-comparisons1"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-comparisons1"
fi

output=$(python3 run.py tests/not-ok-sem-direct-recursion.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-direct-recursion"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-direct-recursion"
fi

output=$(python3 run.py tests/not-ok-sem-double-def1.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-double-def1"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-double-def1"
fi

output=$(python3 run.py tests/not-ok-sem-double-def2.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-double-def2"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-double-def2"
fi

output=$(python3 run.py tests/not-ok-sem-double-def3.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-double-def3"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-double-def3"
fi

output=$(python3 run.py tests/not-ok-sem-double-def4.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-double-def4"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-double-def4"
fi

output=$(python3 run.py tests/not-ok-sem-func_not-defined.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-func_not-defined"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-func_not-defined"
fi


output=$(python3 run.py tests/not-ok-sem-proc-call1.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-proc-call1"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-proc-call1"
fi

output=$(python3 run.py tests/not-ok-sem-proc-call2.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-proc-call2"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-proc-call2"
fi

output=$(python3 run.py tests/not-ok-sem-proc-not-defined.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-proc-not-defined"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-proc-not-defined"
fi

output=$(python3 run.py tests/not-ok-sem-scoping.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-scoping"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-scoping"
fi

output=$(python3 run.py tests/not-ok-sem-types1.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-types1"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-types1"
fi

output=$(python3 run.py tests/not-ok-sem-types2.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-types2"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-types2"
fi

output=$(python3 run.py tests/not-ok-sem-types3.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-types3"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-types3"
fi

output=$(python3 run.py tests/not-ok-sem-types4.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-types4"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-types4"
fi

output=$(python3 run.py tests/not-ok-sem-use-before-def.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-use-before-def"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-use-before-def"
fi

output=$(python3 run.py tests/not-ok-sem-wrong-parameter-num.vec)
if [[ "$output" == *"$error_str"* ]]; then
    echo "Passed not-ok-sem-wrong-parameter-num"
else
    printf '%s\n' "$output"
    echo "Failed not-ok-sem-wrong-parameter-num"
fi
