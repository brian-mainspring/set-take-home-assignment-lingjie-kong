# Smart Garden Hub — Senior Software Engineer in Test Take Home

Spend **60–120 minutes** on this. We don't expect you to complete every task perfectly — we want to see how you think, how you prioritize, and how you handle a system you haven't seen before. Quality over quantity.

Most of your time will likely go toward Task 3. Partial coverage with good reasoning is better than exhaustive coverage with no explanation.

---

## The scenario

Your friend has trusted you with her ultra-rare vanilla bean orchid 🌱 while she travels for 20 days. This orchid only survives between **21–26 °C**. You've built a Smart Garden Hub to keep it alive — a miniature controller system with five peripheral devices, each responsible for a different part of the environment.

The hub exposes a **REST API** so you can observe and drive it. Your job is to understand the system, extend it, and — most importantly — test it.

---

## System architecture

The `GardenHub` (`garden_hub.py`) is the central controller. It coordinates five **peripheral controllers**, manages a shared **power budget**, and monitors the **orchid's health**.

### Peripheral controllers

| Code | Class | Role |
|------|-------|------|
| `tc` | `TemperatureController` | Heats or cools the enclosure (1 °C per step, 1 power unit per step) |
| `hc` | `HumidityController` | Misting and ventilation (misting: 2 units, ventilation: 1 unit) |
| `lc` | `LightController` | UV grow lights on a 16h-on / 8h-off cycle (3 units to switch on) |
| `sc` | `SoilController` | Read-only soil moisture and pH sensor (no actuation, no power) |
| `fm` | `FungiMonitor` | Passive spore tracker — growth logic is yours to implement |

All peripheral classes live in the `peripherals/` package and inherit from `peripherals.base.BasePeripheral`.

### Hub state machine

```
DORMANT → ACTIVE → FAULT
```

- **DORMANT**: initial state before peripherals connect.
- **ACTIVE**: normal operation; all peripherals connected and running.
- **FAULT**: battery depleted or orchid dead. No further cycles execute.

### REST API

The hub runs as a Flask server. All interaction (including tests) goes through HTTP.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/status` | Hub state, orchid alive, battery %, cycle number |
| `GET` | `/controllers` | List all five peripheral controllers |
| `GET` | `/controllers/<name>` | Detail for one controller |
| `GET` | `/controllers/<name>/version` | Firmware version (`UNKNOWN` if disconnected) |
| `GET` | `/telemetry` | Current telemetry snapshot from all peripherals |
| `GET` | `/orchid` | Orchid alive status |
| `POST` | `/cycle` | Advance one simulation cycle |
| `POST` | `/reset` | Reset hub to initial state (for test isolation) |

### Telemetry snapshot

`GET /telemetry` returns:

```json
{
  "cycle": 5,
  "signals": {
    "tc_heartbeat": 5,    "tc_temperature": 23.4,  "tc_power_used": 2.0,
    "hc_heartbeat": 5,    "hc_humidity": 62.1,     "hc_misting_active": 0,
    "lc_heartbeat": 5,    "lc_light_on": 1,         "lc_hour_of_day": 5,
    "sc_heartbeat": 5,    "sc_moisture": 0.631,     "sc_ph": 6.72,
    "fm_heartbeat": 5,    "fm_spore_count": 1
  }
}
```

---

## Setup

**Requirements:** Python 3.8+

```bash
pip install -r requirements.txt
```

---

## Running the simulation

```bash
python simulation.py
```

This starts the hub server, runs 20 days × 24 cycles through the REST API, and writes `telemetry.csv`. Inspect it to understand the system behaviour before writing tests.

---

## Running the tests

```bash
pytest tests/ -v
```

The test suite starts its own hub server instance (on port 5001) via a session-scoped fixture in `conftest.py`. You do not need to start the server manually before running tests.

---

## Tasks

### Task 1 — Critique the simulation (written)

Read the source code and answer the following questions **in this README below the task**.

1. What are the shortcomings of this simulation compared to a real smart garden? Where would it behave incorrectly or unrealistically?
2. The `TemperatureSensor` in the original code used to accumulate temperature like this:
   ```python
   self.temp += self.previous_day_temp + random.randint(-2, 2)
   ```
   The new `TemperatureController` uses a bounded random walk instead. Is this a better model? What's still wrong with it?
3. What assumptions does the system make that would not hold for real hardware?
4. Right now `simulation.py` and `pytest tests/` are both run manually. Describe how you would integrate both into a CI pipeline. What would need to change in the code or configuration to make this reliable and repeatable in automation?

**Your answers:**

> _Write your answers here._

---

### Task 2 — Complete the implementation (code)

Two components of the system have been left incomplete. Implement them, then run `python simulation.py` and verify the CSV reflects meaningful behaviour before moving on.

**`FungiMonitor.update()` (`peripherals/fungi_monitor.py`)**

- Each cycle, if the current temperature is within the growth range (`GROWTH_TEMP_MIN`–`GROWTH_TEMP_MAX`, 25–26 °C), the spore count doubles.
- When the spore count reaches or exceeds `LETHAL_SPORE_COUNT` (512), kill the orchid.

**`PowerManager.consume()` (`power_manager.py`)**

- If `remaining >= amount`, deduct `amount` from `remaining` and return `True`.
- Otherwise, return `False` without modifying `remaining`.

---

### Task 3 — Test the system (code)

Write a test suite for the GardenHub using the provided example fixture and test as a starting point.

How you structure your fixtures, what you choose to test, and how you organise your files is up to you. We want to see how you think about what matters — not a specific list of test cases.

`POST /reset` is available if you need it. The telemetry signal reference is in `tests/test_telemetry.py`.

---

### Task 4 — Test plan (written)

Write a test plan for the Smart Garden Hub as if it were a **real product** with real hardware — not a simulation. You are not implementing these tests, just describing them.

A complete test plan includes:

1. **Introduction** — what system is being tested and why.
2. **Goals** — what does the test plan aim to verify?
3. **Items to be tested** — which components and interfaces are in scope?
4. **Test scenarios / test cases** — describe specific scenarios, including prerequisites, steps, expected results, and pass/fail criteria.

**Your test plan:**

> _Write your test plan here._

---

### Bonus A — Parametrize

If any of your tests repeat the same logic across multiple controllers, refactor them using `pytest.mark.parametrize`.

---

### Bonus B — Containerise the test suite

Write a minimal `Dockerfile` that packages this test suite so it can run in CI without any local setup. The hub URL should be configurable via an environment variable so the same image can point at different targets.

Consider: what should be the container's entrypoint? What would the CI pipeline step look like?

---

### Bonus C — Add a CO2 peripheral controller

A stub class has been provided in `peripherals/co2_controller.py`. Implement it and wire it into the system.

**Requirements:**

- CO2 levels follow a random walk bounded to **400–2000 ppm**.
- Each cycle, consume **0.5 power units** from the `PowerManager` for the ventilation check. If power is unavailable, skip the check.
- Emit two telemetry signals per cycle:
  - `co2_heartbeat` — heartbeat counter (int)
  - `co2_ppm` — current CO2 level, rounded to 1 decimal (float)
- Register the controller with the `GardenHub` under the code `"co2"`. You will need to update `peripherals/__init__.py` and `garden_hub.py`.
- Add tests for the new controller.

---

## Submission

1. Create a branch (your choice of name).
2. Commit all changes to the branch.
3. When ready, open a pull request to merge your branch into `main`.

---

## Credits

Inspired by: https://gitlab.com/roelle/controller-implementation-comparison-take-home

Original by: https://github.com/okyang-mse/software-test-engineer-take-home/tree/main
