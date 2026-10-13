# Rotary Car Parking System

A simulation of a rotary (carousel) car parking system, built as an MDP project. Cars are parked on platforms of a rotating carousel. To park or retrieve a car, the carousel rotates the chosen platform to the bay (the entrance/exit) along the shortest path.

**Live demo:** https://ramyakeez1789-droid.github.io/rotary-parking/

## Features

1. **Store slot information:** keeps track of which of the 8 platforms hold cars.
2. **Accept user input:** park in the nearest empty platform, or choose a platform; retrieve a car by its number.
3. **Calculate movement:** works out the shortest direction and number of positions to rotate.
4. **Control the motor:** a simulated stepper motor rotates clockwise or counter-clockwise.
5. **Stop at the correct position:** a position sensor confirms alignment before the motor stops.
6. **Update status:** a platform is marked occupied after parking and empty after retrieval (red = occupied, green = free).
7. **Calculate parked time:** time between entry and exit.
8. **Calculate fee:** 20 per hour, rounded up to a full hour, with a 1-hour minimum.

## Smart parking extras (in the website)

- **Sensors:** simulated ultrasonic distance and IR readings for each slot.
- **Barrier arm:** a servo-controlled barrier that lifts when a car enters or leaves.
- **ESP32 / MQTT messages:** a live log of messages the controller would publish, such as `parking/slot3/status`.
- **Cloud database and dashboard:** a simulated Firebase-style database with a live slot dashboard and an entry/exit history.

## Files

| File | Description |
|------|-------------|
| `index.html` | The website simulator (runs in any browser, no install needed) |
| `car_rotating_system.py` | The Python version of the system (console simulation) |

## How to run

**Website:** open the live demo link above, or open `index.html` in a browser.

**Python version:**
```
python car_rotating_system.py
```
Use the menu to park a car, retrieve a car or show the status.

## Team and roles

| Role | Member | Work |
|------|--------|------|
| A | Ethen Leslie Vivin | Barrier arm mechanism, slot markers, scale-model structure, sensor brackets |
| B | Kanishk Agarwal | Ultrasonic and IR sensor wiring, servo driver circuit, power supply |
| C | Sowmitha S | ESP32 firmware: sensor polling, WiFi, MQTT / HTTP data push |
| D | Ramyakeerthana R | Cloud database setup and live slot dashboard |

## Notes

- This is a software simulation. To use real hardware (for example a Raspberry Pi with a stepper driver), replace the motor pulse and sensor read functions with GPIO code.
- The simulated "cloud database" is saved in the visitor's own browser, so each visitor sees their own data.
