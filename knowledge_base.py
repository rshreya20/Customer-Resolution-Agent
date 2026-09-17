# Source of truth: Assignment 3 — Customer-Facing Resolution Agent (Airline Disruption)
# Date in the assignment: Wednesday, 23 September 2026

CUSTOMERS = {
    "Priya Nair": {
        "loyalty_tier": "Gold",
        "pnr": "SK4821X",
        "email": "priya.nair@example.com",
        "phone": "+91-98xxxxxxx1",
        "travel_history": "6 flights, 1 prior complaint (delayed baggage, resolved with voucher)"
    },
    "Arvind Kulkarni": {
        "loyalty_tier": "Silver",
        "pnr": "TR1190B",
        "email": "arvind.kulkarni@example.com",
        "phone": "+91-98xxxxxxx2",
        "travel_history": "3 flights, no prior complaints"
    },
    "Meher Kaur": {
        "loyalty_tier": "Platinum",
        "pnr": "WL7742",
        "email": "meher.kaur@example.com",
        "phone": "+91-98xxxxxxx3",
        "travel_history": "10 flights, 1 prior complaint (overbooking, resolved with a tier-status upgrade)"
    }
}

BOOKINGS = {
    "SK4821X": {
        "customer": "Priya Nair",
        "flight": "SK-204",
        "route": "Delhi → Goa",
        "date": "Wed 23 Sep 2026",
        "departure": "18:40",
        "status": "Cancelled",
        "reason": "operational reasons",
        "return_flight": {
            "route": "Goa → Delhi",
            "date": "Fri 25 Sep 2026",
            "departure": "16:20",
            "status": "Unaffected"
        }
    },
    "TR1190B": {
        "customer": "Arvind Kulkarni",
        "flight": "SK-118",
        "route": "Mumbai → Bengaluru",
        "date": "Wed 23 Sep 2026",
        "departure": "07:10",
        "status": "Delayed 4h",
        "delay_hours": 4,
        "new_departure": "11:10"
    },
    "WL7742": {
        "customer": "Meher Kaur",
        "flight": "SK-305",
        "route": "Delhi → Hyderabad",
        "date": "Wed 23 Sep 2026",
        "departure": "14:00",
        "status": "Delayed 6h",
        "delay_hours": 6,
        "new_departure": "20:00",
        "requested_fare_difference": 2000
    }
}

RULES = {
    "cancellation_rebooking": "Airline-caused cancellation → free rebooking on next available flight within 24 hours OR full refund, customer's choice.",
    "delay_under_3h": "₹500 meal voucher.",
    "delay_over_3h": "Meal voucher + lounge access.",
    "delay_over_5h": "Meal voucher + hotel accommodation covering only delayed hours, not a full night's stay.",
    "refund": "Full refund within 7 business days to original payment method only.",
    "fare_difference": "Voluntary higher-fare rebooking requires customer to pay fare difference.",
    "fare_waiver": "Agents cannot waive fare differences above ₹1,500 without supervisor approval.",
    "loyalty": "Gold and Platinum receive priority rebooking but no additional compensation beyond standard policy.",
    "prohibited": [
        "Compensation beyond stated policy amounts",
        "Fare-difference waiver above ₹1,500",
        "Exceptions for non-airline-caused disruptions",
        "Threats of legal action or formal complaints",
        "Refund to a different payment method"
    ]
}
