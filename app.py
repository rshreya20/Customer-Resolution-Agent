import streamlit as st
from agent import ResolutionAgent
from datetime import datetime


# =============================================================
# PAGE CONFIG
# =============================================================

st.set_page_config(
    page_title="Customer Resolution Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================
# LOAD AGENT
# =============================================================

@st.cache_resource
def get_agent():
    return ResolutionAgent()


agent = get_agent()


# =============================================================
# SESSION STATE
# =============================================================

if "selected_customer" not in st.session_state:

    st.session_state.selected_customer = (
        list(agent.customers.keys())[0]
    )


if "messages_by_customer" not in st.session_state:

    st.session_state.messages_by_customer = {}


if "activity_by_customer" not in st.session_state:

    st.session_state.activity_by_customer = {}


if "pending_prompt" not in st.session_state:

    st.session_state.pending_prompt = None


# =============================================================
# HELPERS
# =============================================================

def current_messages(customer_name):

    return st.session_state.messages_by_customer.setdefault(
        customer_name,
        []
    )


def current_activity(customer_name):

    return st.session_state.activity_by_customer.setdefault(
        customer_name,
        []
    )


def add_activity(customer_name, items):

    log = current_activity(customer_name)

    timestamp = datetime.now().strftime(
        "%H:%M:%S"
    )

    for item in items:

        log.append(
            f"{timestamp}  {item}"
        )

    st.session_state.activity_by_customer[
        customer_name
    ] = log[-40:]


def status_badge(status):

    if status == "RESOLVED":

        return "🟢 Resolved"

    if status in [
        "ESCALATE",
        "PARTIAL + ESCALATE"
    ]:

        return "🟠 Human escalation"

    if status == "POLICY_LIMIT":

        return "🟡 Policy limit"

    if status == "EMPATHY":

        return "🔵 Customer care"

    if status == "KNOWLEDGE_BOUNDARY":

        return "⚪ Knowledge boundary"

    if status == "POLICY_INFO":

        return "🔵 Policy information"

    return f"ℹ️ {status}"


# =============================================================
# CUSTOMER PROFILE
# =============================================================

def render_customer_profile(customer_name):

    customer = agent.customers[
        customer_name
    ]

    booking = agent.get_booking(
        customer_name
    )

    st.sidebar.markdown(
        "### 👤 Customer profile"
    )

    st.sidebar.markdown(
        f"## {customer_name}"
    )

    st.sidebar.caption(
        f"{customer['loyalty_tier']} loyalty tier"
    )

    col1, col2 = st.sidebar.columns(2)

    col1.metric(
        "PNR",
        customer["pnr"]
    )

    # Extract number of flights from travel history.
    flights = customer[
        "travel_history"
    ].split(" flights")[0]

    col2.metric(
        "Flights",
        flights
    )

    st.sidebar.markdown(
        f"**Email:** {customer['email']}"
    )

    st.sidebar.markdown(
        f"**Phone:** {customer['phone']}"
    )

    st.sidebar.markdown(
        f"**Travel history:** "
        f"{customer['travel_history']}"
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        "### ✈️ Current flight"
    )

    st.sidebar.markdown(
        f"## {booking['flight']}"
    )

    st.sidebar.markdown(
        f"**{booking['route']}**"
    )

    st.sidebar.markdown(
        f"**Date:** {booking['date']}"
    )

    st.sidebar.markdown(
        f"**Scheduled:** "
        f"{booking.get('departure', booking.get('scheduled_departure', '—'))}"
    )

    if booking.get("new_departure"):

        st.sidebar.markdown(
            f"**New departure:** "
            f"{booking['new_departure']}"
        )

    status = booking["status"]

    if status.lower().startswith(
        "cancelled"
    ):

        st.sidebar.error(
            f"🔴 {status}"
        )

    elif status.lower().startswith(
        "delayed"
    ):

        st.sidebar.warning(
            f"🟠 {status}"
        )

    else:

        st.sidebar.success(
            f"🟢 {status}"
        )

    # Return flight information.
    if booking.get("return_flight"):

        ret = booking[
            "return_flight"
        ]

        st.sidebar.markdown(
            "### 🔄 Return flight"
        )

        st.sidebar.caption(

            f"{ret['route']}\n\n"
            f"{ret['date']} • "
            f"{ret['departure']} • "
            f"{ret['status']}"
        )


# =============================================================
# ACTIVITY LOG
# =============================================================

def render_activity(customer_name):

    log = current_activity(
        customer_name
    )

    with st.expander(
        "🧾 Agent activity log",
        expanded=False
    ):

        if not log:

            st.caption(
                "No agent activity yet."
            )

        else:

            for item in log:

                st.markdown(
                    f"`{item}`"
                )




# =============================================================
# RUN AGENT
# =============================================================

def run_prompt(
    customer_name,
    prompt
):

    messages = current_messages(
        customer_name
    )

    result = agent.respond(
        customer_name,
        prompt,
        messages
    )

    # Add user message.
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Add assistant message.
    messages.append(
        {
            "role": "assistant",
            "content": result["message"],
            "details": result.get(
                "details",
                {}
            )
        }
    )

    add_activity(
        customer_name,
        result.get(
            "activity",
            []
        )
    )

    return result


# =============================================================
# HEADER
# =============================================================

st.title(
    "✈️ Customer Resolution Agent"
)

st.caption(
    "Airline Disruption • Assignment 3 • "
    "Grounded strictly in the supplied Data Pack"
)


# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:

    st.markdown(
        "## 🎧 Support Console"
    )

    customers = list(
        agent.customers.keys()
    )

    selected_index = customers.index(
        st.session_state.selected_customer
    )

    customer_name = st.selectbox(
        "Select customer",
        customers,
        index=selected_index
    )

    if (
        customer_name
        != st.session_state.selected_customer
    ):

        st.session_state.selected_customer = (
            customer_name
        )

        st.session_state.pending_prompt = None

        st.rerun()

    render_customer_profile(
        customer_name
    )

    # ---------------------------------------------------------
    # DEMO MODE
    # ---------------------------------------------------------

    st.divider()

    st.markdown(
        "### 🧪 Demo mode"
    )

    st.caption(
        "Run the exact assignment scenarios."
    )

    demo_scenarios = {

        "Scenario 1 — Priya":
            (
                "I am furious. My flight was cancelled "
                "and I want a full cash refund plus a "
                "free business class upgrade on my "
                "return flight."
            ),

        "Scenario 2 — Arvind":
            (
                "I am very frustrated. My flight is "
                "delayed 4 hours and I want a hotel "
                "because this is unacceptable."
            ),

        "Scenario 3 — Meher":
            (
                "I am furious. My flight is delayed "
                "6 hours. I want a full night's hotel "
                "stay and I want the ₹2,000 fare "
                "difference waived on the higher-fare flight."
            )
    }

    scenario_customers = {

        "Scenario 1 — Priya":
            "Priya Nair",

        "Scenario 2 — Arvind":
            "Arvind Kulkarni",

        "Scenario 3 — Meher":
            "Meher Kaur"
    }

    for label, demo_prompt in demo_scenarios.items():

        if st.button(
            label,
            use_container_width=True,
            key=f"demo_{label}"
        ):

            st.session_state.selected_customer = (
                scenario_customers[label]
            )

            st.session_state.pending_prompt = (
                demo_prompt
            )

            st.rerun()

    # ---------------------------------------------------------
    # QUICK ACTIONS
    # ---------------------------------------------------------

    st.divider()

    st.markdown(
        "### ⚡ Quick actions"
    )

    booking = agent.get_booking(
        customer_name
    )

    quick_actions = agent.quick_actions(
        booking
    )

    for index, action_text in enumerate(
        quick_actions
    ):

        if st.button(
            action_text,
            key=(
                f"quick_{customer_name}_"
                f"{index}"
            ),
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                action_text
            )

            st.rerun()

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    st.divider()

    if st.button(
        "🗑️ Clear this conversation",
        use_container_width=True
    ):

        st.session_state.messages_by_customer[
            customer_name
        ] = []

        st.session_state.activity_by_customer[
            customer_name
        ] = []

        st.session_state.pending_prompt = None

        st.rerun()


# =============================================================
# MAIN FLIGHT OVERVIEW
# =============================================================

customer = agent.customers[
    customer_name
]

booking = agent.get_booking(
    customer_name
)

st.subheader(
    f"Conversation with {customer_name}"
)


# =============================================================
# FLIGHT SUMMARY CARDS
# =============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "PNR",
    customer["pnr"]
)

col2.metric(
    "Flight",
    booking["flight"]
)

col3.metric(
    "Route",
    booking["route"]
)

if booking.get(
    "delay_hours"
):

    col4.metric(
        "Delay",
        f"{booking['delay_hours']}h"
    )

elif booking[
    "status"
].lower().startswith(
    "cancelled"
):

    col4.metric(
        "Status",
        "Cancelled"
    )

else:

    col4.metric(
        "Status",
        booking["status"]
    )


# =============================================================
# STATUS ALERT
# =============================================================

if booking[
    "status"
].lower().startswith(
    "cancelled"
):

    st.error(
        "🔴 Airline-caused cancellation recorded"
    )

elif booking[
    "status"
].lower().startswith(
    "delayed"
):

    st.warning(

        f"🟠 {booking['status']} "
        f"• New departure: "
        f"{booking.get('new_departure', '—')}"
    )


# =============================================================
# CONVERSATION
# =============================================================

messages = current_messages(
    customer_name
)

for msg in messages:

    with st.chat_message(
        msg["role"]
    ):

        st.markdown(
            msg["content"]
        )

        


# =============================================================
# INPUT
# =============================================================

pending = st.session_state.pending_prompt

st.session_state.pending_prompt = None

prompt = (
    pending
    or
    st.chat_input(
        "Ask about your status, refund, rebooking, "
        "meal voucher, lounge, hotel, or escalation..."
    )
)


# =============================================================
# PROCESS MESSAGE
# =============================================================

if prompt:

    result = run_prompt(
        customer_name,
        prompt
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            prompt
        )

    with st.chat_message(
        "assistant"
    ):

        st.markdown(
            result["message"]
        )

    render_activity(
        customer_name
    )


# =============================================================
# EMPTY STATE
# =============================================================

if not messages:

    st.info(

        "👋 Start by asking a question, use a quick "
        "action, or run one of the three assignment "
        "scenarios from the sidebar."
    )


# =============================================================
# KNOWLEDGE BOUNDARY
# =============================================================

with st.expander(
    "📚 Knowledge boundary",
    expanded=False
):

    st.markdown(

        "This prototype uses only the supplied "
        "Assignment 3 Data Pack. If a requested "
        "benefit, process, flight option, or "
        "customer fact is not present in that "
        "source, the agent will not invent it. "
        "It will ask for clarification or escalate "
        "when required."
    )