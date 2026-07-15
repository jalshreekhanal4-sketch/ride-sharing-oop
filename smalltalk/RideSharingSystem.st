"Ride Sharing System - GNU Smalltalk Implementation"
"Demonstrates Encapsulation, Inheritance, and Polymorphism"

"=====================================================================
 NumberFormatter: small utility for printing fixed-point decimals
 (fares, distances, ratings) without relying on Float>>printString.
====================================================================="
Object subclass: #NumberFormatter
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

NumberFormatter class extend [
    decimal: aNumber places: n [
        | scale scaled whole frac |
        scale := 10 raisedTo: n.
        scaled := (aNumber * scale) rounded.
        whole := scaled // scale.
        frac := (scaled \\ scale) abs.
        ^whole printString, '.', (frac printPaddedWith: $0 to: n)
    ]
]

"=====================================================================
 Ride: base class. Holds core ride details (private instance
 variables reachable only through accessor methods) and declares the
 polymorphic protocol fare / rideDetails that every subclass fills in.
====================================================================="
Object subclass: #Ride
    instanceVariableNames: 'rideID pickupLocation dropoffLocation distance'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

Ride class extend [
    rideID: anID pickup: aPickup dropoff: aDropoff distance: aDistance [
        | r |
        r := self new.
        r setRideID: anID pickup: aPickup dropoff: aDropoff distance: aDistance.
        ^r
    ]
]

Ride extend [
    setRideID: anID pickup: aPickup dropoff: aDropoff distance: aDistance [
        rideID := anID.
        pickupLocation := aPickup.
        dropoffLocation := aDropoff.
        distance := aDistance.
    ]

    "Read-only accessors - the only way outside code can see the state."
    rideID [ ^rideID ]
    pickupLocation [ ^pickupLocation ]
    dropoffLocation [ ^dropoffLocation ]
    distance [ ^distance ]

    "Every subclass MUST override fare - this is the polymorphic hook."
    fare [ ^self subclassResponsibility ]

    rideDetails [
        Transcript showCr: 'Ride #', rideID printString, ' | ',
            pickupLocation, ' -> ', dropoffLocation,
            ' | Distance: ', (NumberFormatter decimal: distance places: 1), ' mi',
            ' | Fare: $', (NumberFormatter decimal: self fare places: 2).
    ]
]

"=====================================================================
 StandardRide: everyday, budget-friendly ride type.
====================================================================="
Ride subclass: #StandardRide
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

StandardRide extend [
    fare [
        ^2.00 + (distance * 1.25)
    ]

    rideDetails [
        Transcript show: '[Standard] '.
        super rideDetails.
    ]
]

"=====================================================================
 PremiumRide: higher base fare, higher per-mile rate, plus a luxury
 surcharge - overrides fare differently than StandardRide.
====================================================================="
Ride subclass: #PremiumRide
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

PremiumRide extend [
    fare [
        ^5.00 + (distance * 2.75) + 3.50
    ]

    rideDetails [
        Transcript show: '[Premium]  '.
        super rideDetails.
    ]
]

"=====================================================================
 SharedRide: a third ride type - discounted rate for pooled trips.
====================================================================="
Ride subclass: #SharedRide
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

SharedRide extend [
    fare [
        ^1.50 + (distance * 0.85)
    ]

    rideDetails [
        Transcript show: '[Shared]   '.
        super rideDetails.
    ]
]

"=====================================================================
 Driver: assignedRides is a private instance variable with NO direct
 accessor - it can only be modified via addRide: and inspected via
 getDriverInfo, enforcing encapsulation.
====================================================================="
Object subclass: #Driver
    instanceVariableNames: 'driverID name rating assignedRides'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

Driver class extend [
    driverID: anID name: aName rating: aRating [
        | d |
        d := self new.
        d setDriverID: anID name: aName rating: aRating.
        ^d
    ]
]

Driver extend [
    setDriverID: anID name: aName rating: aRating [
        driverID := anID.
        name := aName.
        rating := aRating.
        assignedRides := OrderedCollection new.
    ]

    addRide: aRide [
        assignedRides add: aRide.
    ]

    totalEarnings [
        | total |
        total := 0.
        assignedRides do: [:eachRide | total := total + eachRide fare].
        ^total
    ]

    getDriverInfo [
        Transcript showCr: 'Driver #', driverID printString, ' - ', name,
            ' | Rating: ', (NumberFormatter decimal: rating places: 1), '/5.0',
            ' | Rides completed: ', assignedRides size printString,
            ' | Total earnings: $', (NumberFormatter decimal: self totalEarnings places: 2).
        assignedRides do: [:eachRide |
            Transcript show: '    '.
            eachRide rideDetails.
        ].
    ]
]

"=====================================================================
 Rider: requestedRides is likewise private, reachable only through
 requestRide: and viewRides.
====================================================================="
Object subclass: #Rider
    instanceVariableNames: 'riderID name requestedRides'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'.

Rider class extend [
    riderID: anID name: aName [
        | r |
        r := self new.
        r setRiderID: anID name: aName.
        ^r
    ]
]

Rider extend [
    setRiderID: anID name: aName [
        riderID := anID.
        name := aName.
        requestedRides := OrderedCollection new.
    ]

    requestRide: aRide [
        requestedRides add: aRide.
    ]

    viewRides [
        Transcript showCr: 'Rider #', riderID printString, ' - ', name,
            ' | Requested rides: ', requestedRides size printString.
        requestedRides do: [:eachRide |
            Transcript show: '    '.
            eachRide rideDetails.
        ].
    ]
]

"=====================================================================
 Demonstration
====================================================================="
| allRides driver rider |

Transcript showCr: '====================================================='.
Transcript showCr: '           RIDE SHARING SYSTEM (Smalltalk)'.
Transcript showCr: '====================================================='.
Transcript showCr: ''.

allRides := OrderedCollection new.
allRides add: (StandardRide rideID: 101 pickup: 'Downtown' dropoff: 'Airport' distance: 12.5).
allRides add: (PremiumRide rideID: 102 pickup: 'Uptown' dropoff: 'Stadium' distance: 8.0).
allRides add: (SharedRide rideID: 103 pickup: 'Campus' dropoff: 'Mall' distance: 5.2).
allRides add: (PremiumRide rideID: 104 pickup: 'Hotel' dropoff: 'Convention Center' distance: 3.4).

Transcript showCr: '--- All Rides (polymorphic fare and rideDetails) ---'.
allRides do: [:eachRide | eachRide rideDetails].

driver := Driver driverID: 1 name: 'Amara Chen' rating: 4.9.
driver addRide: (allRides at: 1).
driver addRide: (allRides at: 2).
driver addRide: (allRides at: 4).

rider := Rider riderID: 1 name: 'Jordan Patel'.
rider requestRide: (allRides at: 1).
rider requestRide: (allRides at: 3).

Transcript showCr: ''.
Transcript showCr: '--- Driver Info ---'.
driver getDriverInfo.

Transcript showCr: ''.
Transcript showCr: '--- Rider Ride History ---'.
rider viewRides.

Transcript showCr: ''.
Transcript showCr: '====================================================='.
