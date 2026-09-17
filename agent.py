from knowledge_base import CUSTOMERS, BOOKINGS, RULES


class ResolutionAgent:
    """
    Source-grounded Customer Resolution Agent.

    Responsibilities:
    - Customer and booking lookup
    - Intent detection
    - Sentiment detection
    - Conversation-context handling
    - Policy evaluation
    - Allowed resolution
    - Human escalation
    - Knowledge-boundary protection
    """

    def __init__(self):
        self.customers = CUSTOMERS
        self.bookings = BOOKINGS
        self.rules = RULES

    # =========================================================
    # CUSTOMER / BOOKING LOOKUP
    # =========================================================

    def get_customer(self, customer_name):
        return self.customers.get(customer_name)

    def get_booking(self, customer_name):
        customer = self.get_customer(customer_name)

        if not customer:
            return None

        return self.bookings.get(customer["pnr"])

    def _has_any(self, text, phrases):
        return any(phrase in text for phrase in phrases)

    # =========================================================
    # SENTIMENT DETECTION
    # =========================================================

    def detect_sentiment(self, message):

        text = message.lower().strip()

        frustrated_words = [
            "furious",
            "angry",
            "very angry",
            "frustrated",
            "frustrating",
            "unacceptable",
            "not acceptable",
            "ridiculous",
            "terrible",
            "awful",
            "disappointed",
            "disgusting",
            "worst",
            "hate",
            "very upset",
            "so upset",
            "fed up",
            "can't believe",
            "cannot believe",
            "this is unacceptable",
            "this is ridiculous"
        ]

        urgent_words = [
            "urgent",
            "urgently",
            "immediately",
            "right now",
            "as soon as possible",
            "emergency"
        ]

        positive_words = [
            "thank you",
            "thanks",
            "appreciate",
            "great",
            "perfect"
        ]

        if self._has_any(text, frustrated_words):
            return "Frustrated"

        if self._has_any(text, urgent_words):
            return "Urgent"

        if self._has_any(text, positive_words):
            return "Positive"

        return "Neutral"

    # =========================================================
    # INTENT DETECTION
    # =========================================================

    def detect_intent(self, message, history=None):

        text = message.lower().strip()

        # -----------------------------------------------------
        # LEGAL / FORMAL COMPLAINT
        # -----------------------------------------------------

        legal_keywords = [
            "legal action",
            "take legal action",
            "lawsuit",
            "sue",
            "lawyer",
            "court",
            "formal complaint",
            "file a complaint",
            "consumer complaint",
            "consumer court"
        ]

        if self._has_any(text, legal_keywords):
            return "Legal / Formal Complaint"

        # -----------------------------------------------------
        # UPGRADE
        # -----------------------------------------------------

        upgrade_keywords = [
            "business class",
            "business-class",
            "free upgrade",
            "upgrade me",
            "upgrade my",
            "upgrade"
        ]

        if self._has_any(text, upgrade_keywords):
            return "Upgrade Request"

        # -----------------------------------------------------
        # REFUND
        # -----------------------------------------------------

        refund_keywords = [
            "refund",
            "money back",
            "cash back",
            "give my money back",
            "return my money"
        ]

        if self._has_any(text, refund_keywords):
            return "Refund Request"

        # -----------------------------------------------------
        # HOTEL
        # -----------------------------------------------------

        hotel_keywords = [
            "hotel",
            "hotel room",
            "accommodation",
            "overnight",
            "full night",
            "whole night",
            "entire night",
            "night stay",
            "room",
            "stay"
        ]

        if self._has_any(text, hotel_keywords):
            return "Hotel Request"

        # -----------------------------------------------------
        # LOUNGE
        # -----------------------------------------------------

        lounge_keywords = [
            "lounge",
            "lounge access",
            "airport lounge"
        ]

        if self._has_any(text, lounge_keywords):
            return "Lounge Request"

        # -----------------------------------------------------
        # MEAL VOUCHER
        # -----------------------------------------------------

        meal_keywords = [
            "meal voucher",
            "food voucher",
            "voucher",
            "meal",
            "food"
        ]

        if self._has_any(text, meal_keywords):
            return "Meal Voucher Request"

        # -----------------------------------------------------
        # REBOOKING
        # -----------------------------------------------------

        rebooking_keywords = [
            "rebook",
            "rebooking",
            "change my flight",
            "change flight",
            "different flight",
            "another flight",
            "next flight",
            "move me",
            "move me to",
            "move to another",
            "alternative flight",
            "replacement flight",
            "fare difference",
            "higher fare",
            "higher-fare"
        ]

        if self._has_any(text, rebooking_keywords):
            return "Rebooking Request"

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        status_keywords = [
            "status",
            "flight status",
            "booking status",
            "booking details",
            "what is my flight",
            "when is my flight",
            "departure time",
            "departure",
            "pnr",
            "booking reference",
            "route"
        ]

        if self._has_any(text, status_keywords):
            return "Status / Booking Information"

        # -----------------------------------------------------
        # OPTIONS
        # -----------------------------------------------------

        options_keywords = [
            "what can you do",
            "what are my options",
            "what can i get",
            "what am i entitled to",
            "what am i eligible for",
            "benefits",
            "options",
            "how can you help"
        ]

        if self._has_any(text, options_keywords):
            return "Options / Entitlements"

        # -----------------------------------------------------
        # FRUSTRATION
        # -----------------------------------------------------

        frustration_keywords = [
            "furious",
            "angry",
            "frustrated",
            "frustrating",
            "unacceptable",
            "not acceptable",
            "ridiculous",
            "terrible",
            "awful",
            "disappointed",
            "disgusting",
            "worst",
            "hate",
            "very upset",
            "so upset",
            "fed up",
            "can't believe",
            "cannot believe",
            "this is unacceptable",
            "this is ridiculous"
        ]

        if self._has_any(text, frustration_keywords):
            return "Frustration"

        # -----------------------------------------------------
        # CONTEXT FOR VAGUE FOLLOW-UP QUESTIONS
        # -----------------------------------------------------

        vague_messages = [
            "what about that",
            "tell me more",
            "more details",
            "what happens next",
            "what now",
            "okay",
            "ok",
            "yes",
            "that one",
            "explain that"
        ]

        if self._has_any(text, vague_messages) and history:

            previous_intent = self._previous_intent(history)

            if previous_intent:
                return previous_intent

        return "Unknown / General"

    def _previous_intent(self, history):

        for item in reversed(history):

            if item.get("role") == "user":

                previous_message = item.get("content", "")

                return self.detect_intent(
                    previous_message,
                    None
                )

        return None

    # =========================================================
    # DELAY POLICY
    # =========================================================

    def delay_entitlement(self, hours):

        if hours < 3:

            return {
                "meal_voucher": True,
                "lounge": False,
                "hotel": False,
                "description": "₹500 meal voucher",
                "policy_rule": (
                    "Delay under 3 hours → ₹500 meal voucher."
                )
            }

        if hours > 5:

            return {
                "meal_voucher": True,
                "lounge": True,
                "hotel": True,
                "description": (
                    "meal voucher + lounge access + "
                    "hotel accommodation covering only "
                    "the delayed hours"
                ),
                "policy_rule": (
                    "Delay more than 5 hours → meal voucher + "
                    "hotel accommodation covering only delayed "
                    "hours. Delay more than 3 hours also qualifies "
                    "for lounge access."
                )
            }

        return {
            "meal_voucher": True,
            "lounge": True,
            "hotel": False,
            "description": "meal voucher + lounge access",
            "policy_rule": (
                "Delay more than 3 hours → meal voucher + "
                "lounge access."
            )
        }

    # =========================================================
    # BOOKING CARD DATA
    # =========================================================

    def _booking_card(
        self,
        customer_name,
        customer,
        booking
    ):

        return {
            "customer": customer_name,
            "loyalty_tier": customer["loyalty_tier"],
            "pnr": customer["pnr"],
            "flight": booking["flight"],
            "route": booking["route"],
            "date": booking["date"],
            "scheduled_departure": booking.get(
                "departure",
                booking.get("scheduled_departure", "")
            ),
            "status": booking["status"],
            "delay_hours": booking.get(
                "delay_hours",
                0
            ),
            "new_departure": booking.get(
                "new_departure"
            ),
            "reason": booking.get(
                "reason"
            ),
            "return_flight": booking.get(
                "return_flight"
            )
        }

    # =========================================================
    # DETAILS
    # =========================================================

    def _details(
        self,
        customer_name,
        customer,
        booking,
        intent,
        sentiment,
        status,
        action,
        policy_rule,
        allowed_actions=None,
        escalations=None,
        notes=None,
        history_used=False
    ):

        return {

            "customer": customer_name,

            "pnr": customer["pnr"],

            "flight": booking["flight"],

            "intent": intent,

            "sentiment": sentiment,

            "status": status,

            "action": action,

            "policy_rule": policy_rule,

            "allowed_actions": allowed_actions or [],

            "escalations": escalations or [],

            "notes": notes or [],

            "conversation_context_used": history_used,

            "source": "Assignment 3 Data Pack"
        }

    # =========================================================
    # RESULT BUILDER
    # =========================================================

    def _result(
        self,
        message,
        customer_name,
        customer,
        booking,
        intent,
        sentiment,
        status,
        action,
        policy_rule="",
        allowed_actions=None,
        escalations=None,
        notes=None,
        history_used=False
    ):

        return {

            "message": message,

            "details": self._details(
                customer_name,
                customer,
                booking,
                intent,
                sentiment,
                status,
                action,
                policy_rule,
                allowed_actions,
                escalations,
                notes,
                history_used
            ),

            "booking_card": self._booking_card(
                customer_name,
                customer,
                booking
            ),

            "customer_profile": customer,

            "activity": [],

            "quick_actions": self.quick_actions(
                booking
            )
        }

    # =========================================================
    # QUICK ACTION BUTTONS
    # =========================================================

    def quick_actions(self, booking):

        status = booking["status"].lower()

        if "cancelled" in status:

            return [
                "What are my options?",
                "I want a full refund",
                "I want to rebook my flight",
                "Show my flight status"
            ]

        if "delayed" in status:

            actions = [
                "What benefits am I entitled to?",
                "I want my meal voucher",
                "Show my flight status"
            ]

            hours = booking.get(
                "delay_hours",
                0
            )

            if hours > 3:

                actions.append(
                    "I want lounge access"
                )

            if hours > 5:

                actions.append(
                    "I want hotel accommodation"
                )

            actions.append(
                "I want to rebook my flight"
            )

            return actions

        return [
            "Show my flight status",
            "What are my options?"
        ]

    # =========================================================
    # MAIN RESPONSE
    # =========================================================

    def respond(
        self,
        customer_name,
        user_text,
        history=None
    ):

        history = history or []

        customer = self.get_customer(
            customer_name
        )

        booking = self.get_booking(
            customer_name
        )

        # -----------------------------------------------------
        # CUSTOMER / BOOKING ERROR
        # -----------------------------------------------------

        if not customer or not booking:

            return {

                "message": (
                    "I couldn't locate the customer or booking "
                    "information in the supplied Data Pack."
                ),

                "details": {
                    "status": "ERROR",
                    "action": "Customer/booking lookup failed",
                    "source": "Assignment 3 Data Pack"
                },

                "booking_card": {},

                "customer_profile": {},

                "activity": [
                    "Customer or booking lookup failed"
                ],

                "quick_actions": []
            }

        text = user_text.lower().strip()

        sentiment = self.detect_sentiment(
            user_text
        )

        intent = self.detect_intent(
            user_text,
            history
        )

        activity = [

            "Customer profile identified",

            f"Booking {customer['pnr']} located",

            f"Intent detected: {intent}",

            f"Sentiment detected: {sentiment}",

            "Applicable policy checked"
        ]

        # =====================================================
        # 1. LEGAL / FORMAL COMPLAINT
        # =====================================================

        if intent == "Legal / Formal Complaint":

            activity.append(
                "Mandatory escalation triggered"
            )

            result = self._result(

                (
                    "I hear you, and I'm sorry this situation "
                    "has been frustrating. Because you have "
                    "mentioned legal action or a formal complaint, "
                    "this needs to be escalated to a human support "
                    "specialist immediately."
                ),

                customer_name,
                customer,
                booking,
                intent,
                sentiment,

                "ESCALATE",

                "Immediate human escalation",

                (
                    "Threats of legal action or formal complaints "
                    "must be escalated immediately."
                ),

                escalations=[
                    "Legal/formal complaint requires immediate human handling."
                ]
            )

            result["activity"] = activity

            return result

        # =====================================================
        # 2. FRUSTRATION
        # =====================================================

        if intent == "Frustration":

            activity.append(
                "Frustration handled separately from resolution request"
            )

            result = self._result(

                (
                    f"I understand that you're frustrated, "
                    f"{customer_name}, and I'm sorry for the "
                    f"disruption.\n\n"
                    f"Your booking currently shows: "
                    f"{booking['status']}.\n\n"
                    "I don't want to assume what resolution "
                    "you want. I can help explain the options "
                    "available under the supplied policy. "
                    "Please tell me specifically whether you "
                    "need help with a refund, rebooking, meal "
                    "voucher, lounge access, hotel eligibility, "
                    "or another request."
                ),

                customer_name,
                customer,
                booking,
                intent,
                sentiment,

                "EMPATHY",

                "Clarify customer's requested resolution",

                (
                    "Customer frustration alone does not "
                    "authorize additional compensation."
                ),

                notes=[
                    "No policy action was assumed from sentiment alone."
                ]
            )

            result["activity"] = activity

            return result

        # =====================================================
        # 3. STATUS
        # =====================================================

        if intent == "Status / Booking Information":

            return_flight = booking.get(
                "return_flight"
            )

            message = (

                f"Here are the booking details available for you:\n\n"

                f"**PNR:** {customer['pnr']}\n"

                f"**Flight:** {booking['flight']}\n"

                f"**Route:** {booking['route']}\n"

                f"**Date:** {booking['date']}\n"

                f"**Scheduled departure:** "
                f"{booking.get('departure', booking.get('scheduled_departure', 'Not provided'))}\n"

                f"**Status:** {booking['status']}"
            )

            if booking.get("new_departure"):

                message += (
                    f"\n**New departure:** "
                    f"{booking['new_departure']}"
                )

            if return_flight:

                message += (

                    f"\n\n**Return flight:** "
                    f"{return_flight['route']} on "
                    f"{return_flight['date']} at "
                    f"{return_flight['departure']} — "
                    f"{return_flight['status']}"
                )

            activity.append(
                "Booking and flight status provided"
            )

            result = self._result(

                message,

                customer_name,
                customer,
                booking,
                intent,
                sentiment,

                "RESOLVED",

                "Provided booking and flight status",

                (
                    "Provide the customer's own booking and "
                    "flight status information."
                )
            )

            result["activity"] = activity

            return result

        # =====================================================
        # 4. CANCELLATION
        # =====================================================

        if booking["status"].lower().startswith(
            "cancelled"
        ):

            actions = []
            escalations = []
            notes = []

            # -------------------------------------------------
            # REFUND
            # -------------------------------------------------

            if intent == "Refund Request":

                actions.append(
                    "Initiate a full refund request to the original payment method."
                )

                notes.append(
                    "Refunds are processed in full within 7 business days."
                )

                activity.append(
                    "Refund request accepted under cancellation policy"
                )

                # Multiple requests in one message.
                if self._has_any(
                    text,
                    [
                        "upgrade",
                        "business class",
                        "business-class"
                    ]
                ):

                    escalations.append(
                        "The requested free business-class upgrade "
                        "is not authorized by the supplied rules."
                    )

            # -------------------------------------------------
            # REBOOKING
            # -------------------------------------------------

            elif intent == "Rebooking Request":

                actions.append(
                    "Rebook on the next available flight within "
                    "24 hours at no charge."
                )

                activity.append(
                    "Free cancellation rebooking identified"
                )

                if self._has_any(
                    text,
                    [
                        "upgrade",
                        "business class",
                        "business-class"
                    ]
                ):

                    escalations.append(
                        "The requested free business-class upgrade "
                        "is not authorized by the supplied rules."
                    )

            # -------------------------------------------------
            # UPGRADE
            # -------------------------------------------------

            elif intent == "Upgrade Request":

                escalations.append(
                    "The requested free business-class upgrade "
                    "is not provided for by the supplied rules."
                )

                activity.append(
                    "Unsupported free upgrade request requires human review"
                )

            # -------------------------------------------------
            # OPTIONS
            # -------------------------------------------------

            elif intent == "Options / Entitlements":

                actions.append(
                    "Offer free rebooking on the next available "
                    "flight within 24 hours."
                )

                actions.append(
                    "Offer a full refund to the original payment method."
                )

                activity.append(
                    "Cancellation options presented"
                )

            # -------------------------------------------------
            # UNKNOWN
            # -------------------------------------------------

            else:

                message = (

                    "Your flight is shown as cancelled due to "
                    "operational reasons.\n\n"

                    "Under the supplied policy, you can choose "
                    "either:\n\n"

                    "1. Free rebooking on the next available "
                    "flight within 24 hours.\n\n"

                    "2. A full refund to the original payment method.\n\n"

                    "Tell me which option you want."
                )

                result = self._result(

                    message,

                    customer_name,
                    customer,
                    booking,
                    intent,
                    sentiment,

                    "POLICY_INFO",

                    "Present cancellation options",

                    (
                        "Airline-caused cancellation → free "
                        "rebooking within 24 hours OR full refund."
                    )
                )

                activity.append(
                    "No action taken because customer request was not specific"
                )

                result["activity"] = activity

                return result

            # -------------------------------------------------
            # RESPONSE
            # -------------------------------------------------

            if escalations:

                message = (

                    "I'm sorry for the disruption. Your flight "
                    "was cancelled due to operational reasons. "

                    + " ".join(actions)

                    + " However, "

                    + " ".join(escalations)

                    + " I'm escalating that part to a human agent."
                )

                status = "PARTIAL + ESCALATE"

                action = (
                    "Resolve permitted request and escalate "
                    "unsupported request"
                )

                activity.append(
                    "Permitted portion resolved; unsupported portion escalated"
                )

            else:

                message = (

                    "I'm sorry for the disruption. Your flight "
                    "was cancelled due to operational reasons. "

                    + " ".join(actions)
                )

                if intent == "Refund Request":

                    message += (

                        " The refund is issued to the original "
                        "payment method and processed within "
                        "7 business days."
                    )

                status = "RESOLVED"

                action = (
                    actions[0]
                    if actions
                    else "Explain cancellation options"
                )

            result = self._result(

                message,

                customer_name,
                customer,
                booking,
                intent,
                sentiment,

                status,

                action,

                (
                    "Airline-caused cancellation → free rebooking "
                    "within 24 hours OR full refund. Refund uses "
                    "the original payment method and is processed "
                    "within 7 business days."
                ),

                allowed_actions=actions,

                escalations=escalations,

                notes=notes
            )

            result["activity"] = activity

            return result

        # =====================================================
        # 5. DELAY
        # =====================================================

        if booking["status"].lower().startswith(
            "delayed"
        ):

            hours = booking.get(
                "delay_hours",
                0
            )

            entitlement = self.delay_entitlement(
                hours
            )

            actions = []
            escalations = []
            notes = []

            # -------------------------------------------------
            # HOTEL
            # -------------------------------------------------

            if intent == "Hotel Request":

                full_night = self._has_any(
                    text,
                    [
                        "full night",
                        "whole night",
                        "entire night",
                        "overnight",
                        "night stay"
                    ]
                )

                if hours > 5:

                    actions.append(
                        "Arrange hotel accommodation covering "
                        "only the delayed hours."
                    )

                    notes.append(
                        "A full night's stay is not provided "
                        "by the supplied policy."
                    )

                    activity.append(
                        "Hotel eligibility confirmed for delayed hours only"
                    )

                    if full_night:

                        notes.append(
                            "Customer requested a full night; "
                            "policy limits coverage to delayed hours."
                        )

                else:

                    notes.append(
                        f"Hotel accommodation is not included for "
                        f"a {hours}-hour delay; the hotel threshold "
                        f"is more than 5 hours."
                    )

                    activity.append(
                        "Hotel request denied by policy threshold"
                    )

            # -------------------------------------------------
            # MEAL VOUCHER
            # -------------------------------------------------

            elif intent == "Meal Voucher Request":

                actions.append(
                    "Provide the applicable meal voucher."
                )

                activity.append(
                    "Meal voucher eligibility confirmed"
                )

            # -------------------------------------------------
            # LOUNGE
            # -------------------------------------------------

            elif intent == "Lounge Request":

                if entitlement["lounge"]:

                    actions.append(
                        "Provide lounge access."
                    )

                    activity.append(
                        "Lounge eligibility confirmed"
                    )

                else:

                    notes.append(
                        "Lounge access requires a delay of "
                        "more than 3 hours under the supplied rule."
                    )

                    activity.append(
                        "Lounge request denied by policy threshold"
                    )

            # -------------------------------------------------
            # REBOOKING
            # -------------------------------------------------

            elif intent == "Rebooking Request":

                fare_diff = booking.get(
                    "requested_fare_difference"
                )

                actions.append(
                    "Explain that voluntary higher-fare rebooking "
                    "requires payment of the fare difference."
                )

                activity.append(
                    "Voluntary rebooking policy checked"
                )

                if (
                    fare_diff is not None
                    and fare_diff > 1500
                ):

                    escalations.append(

                        f"The requested fare difference is "
                        f"₹{fare_diff:,}. A fare-difference "
                        f"waiver above ₹1,500 requires "
                        f"supervisor approval."
                    )

                    activity.append(
                        "Fare difference exceeds ₹1,500 authority threshold"
                    )

            # -------------------------------------------------
            # UPGRADE
            # -------------------------------------------------

            elif intent == "Upgrade Request":

                escalations.append(
                    "The supplied rules do not authorize a free "
                    "business-class upgrade or additional "
                    "compensation beyond stated policy."
                )

                activity.append(
                    "Unsupported upgrade request requires human review"
                )

            # -------------------------------------------------
            # OPTIONS
            # -------------------------------------------------

            elif intent == "Options / Entitlements":

                actions.append(
                    f"Applicable standard entitlement: "
                    f"{entitlement['description']}."
                )

                activity.append(
                    "Delay entitlements presented"
                )

            # -------------------------------------------------
            # STANDARD COMPENSATION
            # -------------------------------------------------

            elif self._has_any(
                text,
                [
                    "compensation",
                    "additional compensation",
                    "extra compensation"
                ]
            ):

                actions.append(
                    f"Apply the stated delay entitlement: "
                    f"{entitlement['description']}."
                )

                activity.append(
                    "Standard compensation policy applied"
                )

            # -------------------------------------------------
            # UNKNOWN
            # -------------------------------------------------

            else:

                message = (

                    f"Your flight is delayed by {hours} hours.\n\n"

                    f"Under the supplied policy, the applicable "
                    f"standard entitlement is **"
                    f"{entitlement['description']}**.\n\n"

                    "Tell me which specific part you need help "
                    "with, such as the meal voucher, lounge access, "
                    "hotel eligibility, rebooking, or flight status."
                )

                result = self._result(

                    message,

                    customer_name,
                    customer,
                    booking,
                    intent,
                    sentiment,

                    "POLICY_INFO",

                    "Explain applicable delay entitlement",

                    entitlement["policy_rule"]
                )

                activity.append(
                    "No action taken because customer request was not specific"
                )

                result["activity"] = activity

                return result

            # -------------------------------------------------
            # DETECT MULTIPLE REQUESTS
            # -------------------------------------------------

            if (
                intent != "Hotel Request"
                and self._has_any(
                    text,
                    [
                        "hotel",
                        "accommodation",
                        "full night",
                        "overnight"
                    ]
                )
            ):

                if hours > 5:

                    actions.append(
                        "Hotel accommodation is available "
                        "for delayed hours only."
                    )

                else:

                    notes.append(
                        "Hotel is not covered because the delay "
                        "is not more than 5 hours."
                    )

            if (
                intent != "Upgrade Request"
                and self._has_any(
                    text,
                    [
                        "business class",
                        "business-class",
                        "free upgrade",
                        "upgrade"
                    ]
                )
            ):

                escalations.append(
                    "The requested free upgrade is not "
                    "authorized by the supplied rules."
                )

                activity.append(
                    "Additional unsupported upgrade request detected"
                )

            if self._has_any(
                text,
                [
                    "fare difference",
                    "higher fare",
                    "higher-fare",
                    "₹2,000",
                    "2000"
                ]
            ):

                fare_diff = booking.get(
                    "requested_fare_difference"
                )

                if fare_diff is not None:

                    if fare_diff > 1500:

                        escalations.append(

                            f"The requested fare difference is "
                            f"₹{fare_diff:,}. A waiver above "
                            f"₹1,500 requires supervisor approval."
                        )

                        activity.append(
                            "Fare difference waiver requires supervisor approval"
                        )

                    else:

                        actions.append(
                            f"The higher-fare rebooking requires "
                            f"payment of the ₹{fare_diff:,} fare difference."
                        )

            # -------------------------------------------------
            # FINAL DELAY RESPONSE
            # -------------------------------------------------

            if escalations:

                status = (
                    "PARTIAL + ESCALATE"
                    if actions
                    else "ESCALATE"
                )

                message = (

                    f"I'm sorry for the disruption. Your flight "
                    f"is delayed by {hours} hours.\n\n"

                    f"Under the supplied policy, the standard "
                    f"entitlement is **{entitlement['description']}**."
                )

                if actions:

                    message += (
                        "\n\n"
                        + " ".join(actions)
                    )

                if notes:

                    message += (
                        "\n\n"
                        + " ".join(notes)
                    )

                message += (

                    "\n\n"
                    + " ".join(escalations)
                    + " I'm escalating that part to a human agent."
                )

                activity.append(
                    "Human escalation generated"
                )

                action = (
                    "Resolve permitted request and escalate "
                    "unsupported request"
                )

            elif actions:

                status = "RESOLVED"

                message = (

                    f"I'm sorry for the disruption. Your flight "
                    f"is delayed by {hours} hours.\n\n"

                    f"Under the supplied policy, you qualify for "
                    f"**{entitlement['description']}**.\n\n"

                    + " ".join(actions)
                )

                if notes:

                    message += (
                        "\n\n"
                        + " ".join(notes)
                    )

                action = actions[0]

            else:

                status = "POLICY_LIMIT"

                message = (

                    f"Your flight is delayed by {hours} hours.\n\n"

                    + " ".join(notes)
                )

                action = "Explain policy limit"

            result = self._result(

                message,

                customer_name,
                customer,
                booking,
                intent,
                sentiment,

                status,

                action,

                entitlement["policy_rule"],

                allowed_actions=actions,

                escalations=escalations,

                notes=notes
            )

            result["activity"] = activity

            return result

        # =====================================================
        # 6. UNKNOWN / KNOWLEDGE BOUNDARY
        # =====================================================

        activity.append(
            "No matching supported request found"
        )

        result = self._result(

            (
                "I don't have enough information in the supplied "
                "Data Pack to answer that specific question. "
                "I don't want to invent an airline policy or "
                "customer information.\n\n"
                "I can help with your recorded flight status, "
                "refund, rebooking, delay benefits, hotel "
                "eligibility, lounge access, or escalation."
            ),

            customer_name,
            customer,
            booking,
            intent,
            sentiment,

            "KNOWLEDGE_BOUNDARY",

            "Ask customer to clarify or choose a supported request",

            (
                "Only customer information, booking information, "
                "service rules, allowed actions, and prohibited "
                "actions supplied in the Data Pack may be used."
            ),

            notes=[
                "No unsupported policy or customer information was generated."
            ]
        )

        result["activity"] = activity

        return result