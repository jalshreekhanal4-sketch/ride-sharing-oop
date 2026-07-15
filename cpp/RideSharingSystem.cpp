// Ride Sharing System - C++ Implementation
// Demonstrates Encapsulation, Inheritance, and Polymorphism

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <iomanip>

// ------------------------------------------------------------------
// Ride: base class. Holds core ride details and defines the
// polymorphic interface (fare() and rideDetails()) that every
// subclass must specialize.
// ------------------------------------------------------------------
class Ride {
protected:
    // Encapsulation: fields are protected/private, only reachable
    // through accessors or the constructor.
    int rideID;
    std::string pickupLocation;
    std::string dropoffLocation;
    double distance; // in miles

public:
    Ride(int rideID, const std::string& pickupLocation,
         const std::string& dropoffLocation, double distance)
        : rideID(rideID), pickupLocation(pickupLocation),
          dropoffLocation(dropoffLocation), distance(distance) {}

    virtual ~Ride() = default;

    // Polymorphism: subclasses override this to price rides differently.
    virtual double fare() const = 0;

    // Polymorphism: subclasses may customize the printed summary too.
    virtual void rideDetails() const {
        std::cout << "Ride #" << rideID
                   << " | " << pickupLocation << " -> " << dropoffLocation
                   << " | Distance: " << std::fixed << std::setprecision(1)
                   << distance << " mi"
                   << " | Fare: $" << std::fixed << std::setprecision(2)
                   << fare() << std::endl;
    }

    // Read-only accessors keep the internal state encapsulated.
    int getRideID() const { return rideID; }
    double getDistance() const { return distance; }
    std::string getPickupLocation() const { return pickupLocation; }
    std::string getDropoffLocation() const { return dropoffLocation; }
};

// ------------------------------------------------------------------
// StandardRide: everyday, budget-friendly ride type.
// ------------------------------------------------------------------
class StandardRide : public Ride {
private:
    static constexpr double BASE_FARE = 2.00;
    static constexpr double RATE_PER_MILE = 1.25;

public:
    StandardRide(int rideID, const std::string& pickup,
                 const std::string& dropoff, double distance)
        : Ride(rideID, pickup, dropoff, distance) {}

    double fare() const override {
        return BASE_FARE + (distance * RATE_PER_MILE);
    }

    void rideDetails() const override {
        std::cout << "[Standard] ";
        Ride::rideDetails();
    }
};

// ------------------------------------------------------------------
// PremiumRide: higher per-mile rate, higher base fare, and a
// luxury surcharge.
// ------------------------------------------------------------------
class PremiumRide : public Ride {
private:
    static constexpr double BASE_FARE = 5.00;
    static constexpr double RATE_PER_MILE = 2.75;
    static constexpr double LUXURY_SURCHARGE = 3.50;

public:
    PremiumRide(int rideID, const std::string& pickup,
                const std::string& dropoff, double distance)
        : Ride(rideID, pickup, dropoff, distance) {}

    double fare() const override {
        return BASE_FARE + (distance * RATE_PER_MILE) + LUXURY_SURCHARGE;
    }

    void rideDetails() const override {
        std::cout << "[Premium]  ";
        Ride::rideDetails();
    }
};

// ------------------------------------------------------------------
// SharedRide: a third ride type (extra credit) - discounted rate
// since riders share the trip.
// ------------------------------------------------------------------
class SharedRide : public Ride {
private:
    static constexpr double BASE_FARE = 1.50;
    static constexpr double RATE_PER_MILE = 0.85;

public:
    SharedRide(int rideID, const std::string& pickup,
               const std::string& dropoff, double distance)
        : Ride(rideID, pickup, dropoff, distance) {}

    double fare() const override {
        return BASE_FARE + (distance * RATE_PER_MILE);
    }

    void rideDetails() const override {
        std::cout << "[Shared]   ";
        Ride::rideDetails();
    }
};

// ------------------------------------------------------------------
// Driver: encapsulates a driver's assigned rides behind addRide()
// and getDriverInfo(); assignedRides is never exposed directly.
// ------------------------------------------------------------------
class Driver {
private:
    int driverID;
    std::string name;
    double rating;
    std::vector<std::shared_ptr<Ride>> assignedRides; // private list

public:
    Driver(int driverID, const std::string& name, double rating)
        : driverID(driverID), name(name), rating(rating) {}

    void addRide(const std::shared_ptr<Ride>& ride) {
        assignedRides.push_back(ride);
    }

    double totalEarnings() const {
        double total = 0.0;
        for (const auto& ride : assignedRides) {
            total += ride->fare(); // polymorphic call
        }
        return total;
    }

    void getDriverInfo() const {
        std::cout << "Driver #" << driverID << " - " << name
                   << " | Rating: " << rating << "/5.0"
                   << " | Rides completed: " << assignedRides.size()
                   << " | Total earnings: $" << std::fixed
                   << std::setprecision(2) << totalEarnings() << std::endl;
        for (const auto& ride : assignedRides) {
            std::cout << "    ";
            ride->rideDetails(); // polymorphic call
        }
    }
};

// ------------------------------------------------------------------
// Rider: keeps a private history of requested rides.
// ------------------------------------------------------------------
class Rider {
private:
    int riderID;
    std::string name;
    std::vector<std::shared_ptr<Ride>> requestedRides; // private list

public:
    Rider(int riderID, const std::string& name)
        : riderID(riderID), name(name) {}

    void requestRide(const std::shared_ptr<Ride>& ride) {
        requestedRides.push_back(ride);
    }

    void viewRides() const {
        std::cout << "Rider #" << riderID << " - " << name
                   << " | Requested rides: " << requestedRides.size()
                   << std::endl;
        for (const auto& ride : requestedRides) {
            std::cout << "    ";
            ride->rideDetails(); // polymorphic call
        }
    }
};

// ------------------------------------------------------------------
// Demonstration driver program
// ------------------------------------------------------------------
int main() {
    std::cout << "=====================================================\n";
    std::cout << "           RIDE SHARING SYSTEM (C++)\n";
    std::cout << "=====================================================\n\n";

    // Create rides of different types (polymorphism)
    std::vector<std::shared_ptr<Ride>> allRides;
    allRides.push_back(std::make_shared<StandardRide>(101, "Downtown", "Airport", 12.5));
    allRides.push_back(std::make_shared<PremiumRide>(102, "Uptown", "Stadium", 8.0));
    allRides.push_back(std::make_shared<SharedRide>(103, "Campus", "Mall", 5.2));
    allRides.push_back(std::make_shared<PremiumRide>(104, "Hotel", "Convention Center", 3.4));

    std::cout << "--- All Rides (polymorphic fare() and rideDetails()) ---\n";
    for (const auto& ride : allRides) {
        ride->rideDetails(); // same call, different behavior per subclass
    }

    // Set up a driver and assign some rides
    Driver driver(1, "Amara Chen", 4.9);
    driver.addRide(allRides[0]);
    driver.addRide(allRides[1]);
    driver.addRide(allRides[3]);

    // Set up a rider and log requested rides
    Rider rider(1, "Jordan Patel");
    rider.requestRide(allRides[0]);
    rider.requestRide(allRides[2]);

    std::cout << "\n--- Driver Info ---\n";
    driver.getDriverInfo();

    std::cout << "\n--- Rider Ride History ---\n";
    rider.viewRides();

    std::cout << "\n=====================================================\n";
    return 0;
}
