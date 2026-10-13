"""
Car Rotating System (Rotary Car Parking) - MDP Project
------------------------------------------------------
Platforms are arranged on a circular carousel. One position (the BAY) is the
entrance/exit. To park or retrieve a car, the carousel rotates so the chosen
platform arrives at the BAY.

Covers:
 1. Store slot information          -> self.slots
 2. Accept user input               -> menu in main()
 3. Calculate movement              -> calculate_movement()
 4. Control the motor               -> StepperMotor.rotate()
 5. Stop at correct position        -> sensor feedback loop in rotate()
 6. Update status                   -> park_car() / retrieve_car()
 7. Calculate parked time           -> parked_duration()
 8. Calculate fee                   -> calculate_fee()

Runs as a pure simulation. To use real hardware (e.g. Raspberry Pi + stepper
driver), replace the body of StepperMotor._pulse() and PositionSensor.read()
with GPIO code.
"""

import math
import time
from datetime import datetime, timedelta

# ---------------- Configuration ----------------
NUM_SLOTS = 8             # number of platforms on the carousel
STEPS_PER_SLOT = 50       # motor steps needed to move one platform
RATE_PER_HOUR = 20        # fee per hour (any currency)
MINIMUM_HOURS = 1         # minimum billable hours
TIME_SCALE = 60           # demo: 1 real second = 60 simulated seconds
                          # (set to 1 for real time)
STEP_DELAY = 0.0          # seconds per step (e.g. 0.002 to "see" rotation)


# ---------------- Simulated clock ----------------
_START_REAL = time.time()
_START_SIM = datetime.now()


def now():
    """Simulated current time (sped up by TIME_SCALE for demos)."""
    elapsed_real = time.time() - _START_REAL
    return _START_SIM + timedelta(seconds=elapsed_real * TIME_SCALE)


# ---------------- Hardware layer (simulated) ----------------
class PositionSensor:
    """Reports which platform is currently at the bay (like a hall/encoder sensor)."""

    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.step_count = 0          # absolute step position, 0..total_steps-1

    def update(self, direction):
        self.step_count = (self.step_count + direction) % self.total_steps

    def read_slot(self):
        """Return slot index if aligned exactly on a platform, else None."""
        if self.step_count % STEPS_PER_SLOT == 0:
            return self.step_count // STEPS_PER_SLOT
        return None


class StepperMotor:
    """Simulated stepper motor. direction: +1 = clockwise, -1 = counter-clockwise."""

    def __init__(self, sensor):
        self.sensor = sensor

    def _pulse(self, direction):
        # REAL HARDWARE: set DIR pin from `direction`, pulse STEP pin once.
        if STEP_DELAY:
            time.sleep(STEP_DELAY)
        self.sensor.update(direction)

    def rotate(self, direction, slots_to_move):
        """Rotate until the sensor confirms we reached the target slot."""
        if slots_to_move == 0:
            return
        start = self.sensor.read_slot()
        target = (start + direction * slots_to_move) % NUM_SLOTS
        name = "clockwise" if direction == 1 else "counter-clockwise"
        print(f"  [MOTOR] Rotating {name} by {slots_to_move} position(s)...")

        steps = 0
        while True:                               # drive until sensor says "arrived"
            self._pulse(direction)
            steps += 1
            if self.sensor.read_slot() == target:
                break
        print(f"  [MOTOR] Stopped at slot {target} after {steps} steps.")


# ---------------- Main system ----------------
class RotaryParking:
    def __init__(self, num_slots=NUM_SLOTS):
        self.n = num_slots
        # 1. Store slot information: None = empty, else dict with car data
        self.slots = [None] * self.n
        self.sensor = PositionSensor(self.n * STEPS_PER_SLOT)
        self.motor = StepperMotor(self.sensor)

    # --- helpers ---
    @property
    def position(self):
        """Slot index currently at the bay."""
        return self.sensor.read_slot()

    def empty_slots(self):
        return [i for i, s in enumerate(self.slots) if s is None]

    def find_car(self, plate):
        for i, s in enumerate(self.slots):
            if s and s["plate"].upper() == plate.upper():
                return i
        return None

    # 3. Calculate movement
    def calculate_movement(self, target):
        """Return (direction, positions) using the shortest path."""
        cw = (target - self.position) % self.n        # clockwise distance
        ccw = (self.position - target) % self.n       # counter-clockwise distance
        if cw <= ccw:
            return 1, cw
        return -1, ccw

    def move_to(self, target):
        direction, positions = self.calculate_movement(target)
        self.motor.rotate(direction, positions)

    # 7. Parked time
    @staticmethod
    def parked_duration(entry_time, exit_time):
        return exit_time - entry_time

    # 8. Fee
    @staticmethod
    def calculate_fee(duration):
        hours = duration.total_seconds() / 3600
        billable = max(MINIMUM_HOURS, math.ceil(hours))   # round up to full hour
        return billable, billable * RATE_PER_HOUR

    # --- operations ---
    def park_car(self, plate, slot=None):
        if self.find_car(plate) is not None:
            print("  This car is already parked.")
            return
        empties = self.empty_slots()
        if not empties:
            print("  Parking is FULL.")
            return

        # 2. user chooses a slot, or system picks the nearest available one
        if slot is None:
            slot = min(empties, key=lambda s: self.calculate_movement(s)[1])
            print(f"  Nearest available platform: {slot}")
        elif not (0 <= slot < self.n):
            print("  Invalid slot number.")
            return
        elif self.slots[slot] is not None:
            print(f"  Slot {slot} is occupied.")
            return

        self.move_to(slot)
        # 6. Update status -> occupied
        self.slots[slot] = {"plate": plate.upper(), "entry": now()}
        print(f"  Car {plate.upper()} parked on platform {slot} at "
              f"{self.slots[slot]['entry']:%H:%M:%S}.")

    def retrieve_car(self, plate):
        slot = self.find_car(plate)
        if slot is None:
            print("  Car not found.")
            return
        self.move_to(slot)

        exit_time = now()
        entry = self.slots[slot]["entry"]
        duration = self.parked_duration(entry, exit_time)
        hours, fee = self.calculate_fee(duration)

        # 6. Update status -> empty
        self.slots[slot] = None

        mins = int(duration.total_seconds() // 60)
        print(f"  Car {plate.upper()} retrieved from platform {slot}.")
        print(f"  Parked time : {mins // 60} h {mins % 60} min")
        print(f"  Billed hours: {hours}  x  {RATE_PER_HOUR}")
        print(f"  TOTAL FEE   : {fee}")

    def show_status(self):
        print(f"\n  Platform at bay: {self.position}")
        print("  Slot | Status")
        print("  -----+---------------------------")
        for i, s in enumerate(self.slots):
            if s:
                mins = int((now() - s["entry"]).total_seconds() // 60)
                info = f"OCCUPIED  {s['plate']} ({mins} min)"
            else:
                info = "empty"
            marker = "<- bay" if i == self.position else ""
            print(f"  {i:>4} | {info} {marker}")
        print()


# ---------------- User interface ----------------
def main():
    system = RotaryParking()
    print("=== CAR ROTATING SYSTEM ===")
    print(f"{NUM_SLOTS} platforms | Rate: {RATE_PER_HOUR}/hour "
          f"(demo clock: 1 sec = {TIME_SCALE} sim-seconds)")

    while True:
        print("\n1. Park car (auto - nearest empty platform)")
        print("2. Park car (choose a platform)")
        print("3. Retrieve car")
        print("4. Show status")
        print("5. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            plate = input("  Car number: ").strip()
            if plate:
                system.park_car(plate)
        elif choice == "2":
            plate = input("  Car number: ").strip()
            try:
                slot = int(input(f"  Platform (0-{NUM_SLOTS - 1}): "))
            except ValueError:
                print("  Enter a valid number.")
                continue
            if plate:
                system.park_car(plate, slot)
        elif choice == "3":
            plate = input("  Car number: ").strip()
            system.retrieve_car(plate)
        elif choice == "4":
            system.show_status()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
