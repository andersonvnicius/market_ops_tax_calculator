import subprocess
import textwrap
import json
import pytest


# Helper to run main.py with stdin
def run_cli_input(input_data: str) -> list:
    result = subprocess.run(
        ["python", "main.py"],
        input=input_data.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output_lines = result.stdout.decode().strip().splitlines()
    return [json.loads(line) for line in output_lines]


# Parametrize each case
@pytest.mark.parametrize(
    "input_text, expected",
    [
        # CASE 1
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 100}, '
            '{"operation":"sell", "unit-cost":15.00, "quantity": 50}, '
            '{"operation":"sell", "unit-cost":15.00, "quantity": 50}]',
            [[{"tax": "0.00"}, {"tax": "0.00"}, {"tax": "0.00"}]],
        ),
        # CASE 2
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":20.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":5.00, "quantity": 5000}]',
            [[{"tax": "0.00"}, {"tax": "10000.00"}, {"tax": "0.00"}]],
        ),
        # CASE 3
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":5.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":20.00, "quantity": 3000}]',
            [[{"tax": "0.00"}, {"tax": "0.00"}, {"tax": "1000.00"}]],
        ),
        # CASE 4
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"buy", "unit-cost":25.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":15.00, "quantity": 10000}]',
            [[{"tax": "0.00"}, {"tax": "0.00"}, {"tax": "0.00"}]],
        ),
        # CASE 5
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"buy", "unit-cost":25.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":15.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":25.00, "quantity": 5000}]',
            [[{"tax": "0.00"}, {"tax": "0.00"}, {"tax": "0.00"}, {"tax": "10000.00"}]],
        ),
        # CASE 6
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":2.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
            '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
            '{"operation":"sell", "unit-cost":25.00, "quantity": 1000}]',
            [
                [
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "3000.00"},
                ]
            ],
        ),
        # CASE 7
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":2.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
            '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
            '{"operation":"sell", "unit-cost":25.00, "quantity": 1000}, '
            '{"operation":"buy", "unit-cost":20.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":15.00, "quantity": 5000}, '
            '{"operation":"sell", "unit-cost":30.00, "quantity": 4350}, '
            '{"operation":"sell", "unit-cost":30.00, "quantity": 650}]',
            [
                [
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "3000.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "3700.00"},
                    {"tax": "0.00"},
                ]
            ],
        ),
        # CASE 8
        (
            '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":50.00, "quantity": 10000}, '
            '{"operation":"buy", "unit-cost":20.00, "quantity": 10000}, '
            '{"operation":"sell", "unit-cost":50.00, "quantity": 10000}]',
            [
                [
                    {"tax": "0.00"},
                    {"tax": "80000.00"},
                    {"tax": "0.00"},
                    {"tax": "60000.00"},
                ]
            ],
        ),
        # CASE 9
        (
            '[{"operation": "buy", "unit-cost": 5000.00, "quantity": 10}, '
            '{"operation": "sell", "unit-cost": 4000.00, "quantity": 5}, '
            '{"operation": "buy", "unit-cost": 15000.00, "quantity": 5}, '
            '{"operation": "buy", "unit-cost": 4000.00, "quantity": 2}, '
            '{"operation": "buy", "unit-cost": 23000.00, "quantity": 2}, '
            '{"operation": "sell", "unit-cost": 20000.00, "quantity": 1}, '
            '{"operation": "sell", "unit-cost": 12000.00, "quantity": 10}, '
            '{"operation": "sell", "unit-cost": 15000.00, "quantity": 3}]',
            [
                [
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "0.00"},
                    {"tax": "1000.00"},
                    {"tax": "2400.00"},
                ]
            ],
        ),
        # CASE 10
        (
            '[{"operation": "buy", "unit-cost": 10000.00, "quantity": 10}, '
            '{"operation": "sell", "unit-cost": 11000.00, "quantity": 20}] ',
            [
                [
                    {"tax": "0.00"},
                    {"error": "Can't sell more stocks than you have"},
                ]
            ],
        ),
    ],
)
def test_integration_cases(input_text, expected):
    outputs = run_cli_input(input_text)
    assert outputs == expected
