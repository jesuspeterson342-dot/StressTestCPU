#!/usr/bin/env python3
import re
import time
import subprocess
from pathlib import Path

CMD = [
    "stress-ng", "--cpu", "0", "--cpu-method", "all",
    "--cache", "0",
    "--matrix", "0",
    "--verify",
    "--metrics-brief",
    "-t", "120",
]


def parse_temp(line: str):
    m = re.search(r'([+-]?\d+(?:\.\d+)?)°C', line)
    return float(m.group(1)) if m else None


def temp_from_sensors():
    try:
        out = subprocess.check_output(
            ["sensors"], text=True, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    for key in ("Package id", "Tctl", "Tdie"):
        for line in out.splitlines():
            if key in line:
                t = parse_temp(line)
                if t is not None:
                    return t
    return None


def temp_from_sysfs():
    for zone in Path("/sys/class/thermal").glob("thermal_zone*"):
        try:
            ztype = (zone / "type").read_text().strip().lower()
            raw = (zone / "temp").read_text().strip()
        except OSError:
            continue

        if any(x in ztype for x in ("x86_pkg_temp", "cpu", "package", "tctl", "tdie")):
            try:
                t = float(raw)
                return t / 1000 if t > 1000 else t
            except ValueError:
                continue
    return None


def get_cpu_temp():
    t = temp_from_sensors()
    if t is not None:
        return t
    return temp_from_sysfs()


def main():
    temps = []
    start = time.time()

    try:
        proc = subprocess.Popen(CMD)
    except FileNotFoundError:
        print("Error: stress-ng was not found.")
        return

    while True:
        t = get_cpu_temp()
        if t is not None:
            temps.append(t)

        if proc.poll() is not None:
            break

        time.sleep(1)

    duration = time.time() - start
    return_code = proc.wait()

    if temps:
        print(f"Samples: {len(temps)}")
        print(f"Min: {min(temps):.1f}°C")
        print(f"Max: {max(temps):.1f}°C")
        print(f"Avg: {sum(temps) / len(temps):.1f}°C")
    else:
        print("Error: CPU temperature was not found.")
        print("Check sensors, lm-sensors, or /sys/class/thermal.")

    print(f"Time: {duration:.1f}s")
    print(f"Exit code: {return_code}")


if __name__ == "__main__":
    main()
