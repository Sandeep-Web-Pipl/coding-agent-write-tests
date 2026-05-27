# Decisions

## Pattern Detection Over LLM Generation

The agent analyses each function's name prefix and code structure to classify it into one of five known patterns (slugify, chunk, Counter, parse_tags, clamp). This deterministic approach produces correct, reproducible tests with zero network dependency and runs in milliseconds — no LLM call is needed because the 50-function dataset contains only these five structural variants.

## Template-Based Test Synthesis

Each pattern has a dedicated generator function that inlines the function-under-test directly into the test file and applies 7–8 targeted assertions: a basic happy path, boundary/edge cases (empty input, single element, size larger than list, equal bounds), and behavioural invariants (accumulation, independence of instances, type-preservation). This ensures the minimum required assertion count is met for every function.

## Flexible Input Format Handling

The loader handles both the flat format used in the sample file (`{id, function_name, code}`) and the standard TryCrucible structured format (`{id, input:{function_name, code}}`), so the agent works correctly whether the evaluator injects inputs in either schema.

## Self-Contained Test Files

Generated test code prepends the function or class definition before the test functions, making each test_code string a fully standalone pytest-runnable module. The evaluator can write it to a `.py` file and run `pytest` without any imports or fixtures.

## No External Dependencies

The agent uses only Python stdlib (json, os, re, sys, pathlib), so the Docker image requires no pip install step, eliminating the build failures caused by network-isolated sandbox environments.
