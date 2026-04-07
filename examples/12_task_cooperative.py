"""
12_task_cooperative.py - Non-blocking cooperative multitasking with Task

Demonstrates the Task class (Arduino-style rate-gate pattern):
  - Task(fn, rate)             run fn(current_time) at most every rate seconds
  - Task.every(rate) decorator decorator form -- same behaviour
  - task(time.monotonic())     call repeatedly in a loop; fn fires only when due
  - task.rate                  read/update the interval at runtime
  - task.reset()               force the task to fire on the next call
  - run_immediately=True/False control whether fn fires on the very first call

Key principle: the main loop calls time.monotonic() once and passes it to
every Task.  The Task only executes its function when (current_time -
last_run) >= rate.  This keeps the loop non-blocking like Arduino's
millis() pattern.

Run anywhere (no hardware required for this example).
"""

import time

from raspbot import Task

# ------------------------------------------------------------------
# 1. Basic constructor form
# ------------------------------------------------------------------


def print_status(ct: float) -> None:
    print(f"  [status]  t={ct:.2f}s")


status_task = Task(print_status, rate=1.0, run_immediately=True)

# ------------------------------------------------------------------
# 2. Decorator form -- recommended for named tasks
# ------------------------------------------------------------------


@Task.every(0.5)
def blink(ct: float) -> None:
    print(f"  [blink]   t={ct:.2f}s")


@Task.every(2.0, run_immediately=False)
def slow_task(ct: float) -> None:
    print(f"  [slow]    t={ct:.2f}s  (runs every 2 s, skips first cycle)")


# ------------------------------------------------------------------
# 3. Run the cooperative loop for 5 seconds
# ------------------------------------------------------------------

print("Running cooperative task loop for 5 s ...")
print(f"  status_task rate: {status_task.rate} s")
print(f"  blink rate:       {blink.rate} s")
print(f"  slow_task rate:   {slow_task.rate} s")
print()

end = time.monotonic() + 5.0
while time.monotonic() < end:
    ct = time.monotonic()
    status_task(ct)
    blink(ct)
    slow_task(ct)
    # No sleep here -- the tasks self-throttle via the rate-gate.
    # A tiny sleep just prevents 100 % CPU usage in this example.
    time.sleep(0.001)

# ------------------------------------------------------------------
# 4. Dynamic rate change
# ------------------------------------------------------------------

print("\nChanging blink rate to 0.2 s for 2 s ...")
blink.rate = 0.2
end = time.monotonic() + 2.0
while time.monotonic() < end:
    ct = time.monotonic()
    blink(ct)
    time.sleep(0.001)

# ------------------------------------------------------------------
# 5. reset() -- force a task to fire immediately on the next call
# ------------------------------------------------------------------

print("\nResetting slow_task so it fires immediately ...")
slow_task.reset()
slow_task(time.monotonic())  # fires now regardless of last run time

print("\nDone.")
