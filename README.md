# Ride Sharing System (OOP in C++ and Smalltalk)

A class-based Ride Sharing System implemented twice, once in **C++** and once in **GNU Smalltalk**, to demonstrate encapsulation, inheritance, and polymorphism in two very different OOP languages.

## Structure

```
cpp/
  RideSharingSystem.cpp   C++ implementation
smalltalk/
  RideSharingSystem.st    GNU Smalltalk implementation
```

## Design

- **`Ride`** — base class with `rideID`, `pickupLocation`, `dropoffLocation`, `distance`. Declares the polymorphic `fare()` and `rideDetails()` operations.
- **`StandardRide`**, **`PremiumRide`**, **`SharedRide`** — subclasses of `Ride`, each overriding `fare()` with its own pricing formula.
- **`Driver`** — has a private list of assigned rides (`assignedRides`), only reachable via `addRide()` and `getDriverInfo()`.
- **`Rider`** — has a private list of requested rides (`requestedRides`), only reachable via `requestRide()` and `viewRides()`.
- The demo program stores different ride types in one collection and calls `fare()` / `rideDetails()` polymorphically on each.

## Running the C++ version

```bash
cd cpp
g++ -std=c++17 -Wall -o RideSharingSystem RideSharingSystem.cpp
./RideSharingSystem
```

## Running the Smalltalk version

Requires [GNU Smalltalk](https://www.gnu.org/software/smalltalk/) (`brew install gnu-smalltalk` on macOS).

```bash
cd smalltalk
gst RideSharingSystem.st
```
