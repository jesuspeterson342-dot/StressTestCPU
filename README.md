# CPU Stress Temperature Monitor

A small Linux CLI tool that runs a CPU stress test with `stress-ng` and records CPU temperature during the test.

It prints:

- temperature samples count
- minimum CPU temperature
- maximum CPU temperature
- average CPU temperature
- test duration
- `stress-ng` exit code

## Requirements

Install dependencies:

```bash
sudo pacman -S stress-ng lm_sensors
```

For Debian/Ubuntu:

```bash
sudo apt install stress-ng lm-sensors
```

## Usage

Run:

```bash
python3 main.py
```

By default, the test runs for 120 seconds.

## How it works

The script starts `stress-ng`, reads CPU temperature once per second, then prints a short summary after the test finishes.

Temperature is read from:

1. `sensors`
2. `/sys/class/thermal`

## License

MIT
