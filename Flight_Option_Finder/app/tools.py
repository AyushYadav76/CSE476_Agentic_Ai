import os
import re
from typing import Optional

import serpapi
from dotenv import load_dotenv

# Load variables from .env
load_dotenv(override=True)


# ============================================================
# CITY → IATA AIRPORT CODE
# ============================================================

CITY_TO_IATA = {
    "delhi": "DEL",
    "new delhi": "DEL",

    "mumbai": "BOM",

    "bengaluru": "BLR",
    "bangalore": "BLR",

    "chennai": "MAA",
    "hyderabad": "HYD",
    "kolkata": "CCU",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "goa": "GOI",

    "chandigarh": "IXC",
    "amritsar": "ATQ",
}


# ============================================================
# CABIN CLASS MAPPING
# ============================================================

CABIN_CLASS_MAP = {
    "economy": "1",
    "premium economy": "2",
    "business": "3",
    "first": "4",
}


# ============================================================
# TOOL 1: SEARCH FLIGHTS
# ============================================================

def search_flights(
    from_city: str,
    to_city: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    cabin_class: str = "economy",
) -> str:
    """
    Search live Google Flights data through SerpApi.

    Parameters
    ----------
    from_city : str
        Origin city or IATA airport code.

    to_city : str
        Destination city or IATA airport code.

    departure_date : str
        Departure date in YYYY-MM-DD format.

    return_date : str, optional
        Return date in YYYY-MM-DD format.
        If omitted, the search is one-way.

    passengers : int
        Number of adult passengers.

    cabin_class : str
        economy, premium economy, business, or first.

    Returns
    -------
    str
        Human-readable flight search results.
    """

    # --------------------------------------------------------
    # Check API key
    # --------------------------------------------------------

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return "ERROR: SERPAPI_KEY is not configured."

    # --------------------------------------------------------
    # Validate basic inputs
    # --------------------------------------------------------

    if not from_city or not from_city.strip():
        return "ERROR: Origin city is required."

    if not to_city or not to_city.strip():
        return "ERROR: Destination city is required."

    if not departure_date or not departure_date.strip():
        return "ERROR: Departure date is required."

    if passengers < 1:
        return "ERROR: Passengers must be at least 1."

    # --------------------------------------------------------
    # Convert city names to IATA codes
    # --------------------------------------------------------

    origin_input = from_city.strip().lower()
    destination_input = to_city.strip().lower()

    origin = CITY_TO_IATA.get(
        origin_input,
        from_city.strip().upper()
    )

    destination = CITY_TO_IATA.get(
        destination_input,
        to_city.strip().upper()
    )

    # --------------------------------------------------------
    # Cabin class
    # --------------------------------------------------------

    cabin_input = cabin_class.strip().lower()

    cabin = CABIN_CLASS_MAP.get(
        cabin_input,
        "1"
    )

    # --------------------------------------------------------
    # Trip type
    #
    # SerpApi Google Flights:
    #
    # type=1 → Round trip
    # type=2 → One way
    # type=3 → Multi-city
    # --------------------------------------------------------

    trip_type = "1" if return_date else "2"

    # --------------------------------------------------------
    # Build SerpApi parameters
    # --------------------------------------------------------

    params = {
        "engine": "google_flights",

        "departure_id": origin,

        "arrival_id": destination,

        "type": trip_type,

        "outbound_date": departure_date,

        "currency": "INR",

        "hl": "en",

        "gl": "in",

        "travel_class": cabin,

        "adults": str(passengers),
    }

    # Add return date only for round trips
    if return_date:
        params["return_date"] = return_date

    # --------------------------------------------------------
    # Call SerpApi
    # --------------------------------------------------------

    try:

        client = serpapi.Client(
            api_key=api_key
        )

        results = client.search(params)

    except Exception as e:

        return (
            "ERROR: Flight API request failed: "
            f"{str(e)}"
        )

    # --------------------------------------------------------
    # Extract flight options
    # --------------------------------------------------------

    flights = []

    for group_name in [
        "best_flights",
        "other_flights"
    ]:

        for flight_option in results.get(
            group_name,
            []
        ):

            price = flight_option.get(
                "price"
            )

            total_duration = flight_option.get(
                "total_duration",
                "Unknown"
            )

            stops = flight_option.get(
                "stops",
                0
            )

            legs = flight_option.get(
                "flights",
                []
            )

            # Ignore malformed results
            if not legs:
                continue

            # ------------------------------------------------
            # First and last flight legs
            # ------------------------------------------------

            first_leg = legs[0]

            last_leg = legs[-1]

            # ------------------------------------------------
            # Airline names
            # ------------------------------------------------

            airline_names = []

            for leg in legs:

                airline = leg.get(
                    "airline"
                )

                if (
                    airline
                    and airline not in airline_names
                ):
                    airline_names.append(
                        airline
                    )

            airline = ", ".join(
                airline_names
            )

            # ------------------------------------------------
            # Departure airport
            # ------------------------------------------------

            departure = first_leg.get(
                "departure_airport",
                {}
            )

            # ------------------------------------------------
            # Arrival airport
            # ------------------------------------------------

            arrival = last_leg.get(
                "arrival_airport",
                {}
            )

            departure_time = departure.get(
                "time",
                "Unknown"
            )

            arrival_time = arrival.get(
                "time",
                "Unknown"
            )

            departure_airport = departure.get(
                "id",
                origin
            )

            arrival_airport = arrival.get(
                "id",
                destination
            )

            # ------------------------------------------------
            # Store normalized flight
            # ------------------------------------------------

            flights.append(
                {
                    "airline": airline,

                    "price": price,

                    "departure": departure_time,

                    "arrival": arrival_time,

                    "from": departure_airport,

                    "to": arrival_airport,

                    "stops": stops,

                    "duration": total_duration,
                }
            )

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not flights:

        return (
            "No flight options were returned by "
            f"the flight API for {origin} to "
            f"{destination} on {departure_date}."
        )

    # --------------------------------------------------------
    # Remove duplicate flights
    # --------------------------------------------------------

    unique_flights = []

    seen = set()

    for flight in flights:

        key = (
            flight["airline"],
            flight["price"],
            flight["departure"],
            flight["arrival"],
        )

        if key not in seen:

            seen.add(key)

            unique_flights.append(
                flight
            )

    # Keep output manageable
    unique_flights = unique_flights[:15]

    # --------------------------------------------------------
    # Build readable output
    # --------------------------------------------------------

    output = [
        f"Flight search results: "
        f"{origin} → {destination}",

        f"Departure date: "
        f"{departure_date}",
    ]

    if return_date:

        output.append(
            f"Return date: {return_date}"
        )

    output.append("")

    # --------------------------------------------------------
    # Format every flight
    # --------------------------------------------------------

    for i, flight in enumerate(
        unique_flights,
        1
    ):

        price = flight["price"]

        if price is not None:

            price_text = (
                f"₹{price:,}"
            )

        else:

            price_text = (
                "Price unavailable"
            )

        # Stops
        if flight["stops"] == 0:

            stops_text = "Non-stop"

        else:

            stops_text = (
                f'{flight["stops"]} stop(s)'
            )

        output.append(
            f"{i}. "
            f"{flight['airline']} | "
            f"{flight['from']} → "
            f"{flight['to']} | "
            f"{flight['departure']} - "
            f"{flight['arrival']} | "
            f"{price_text} | "
            f"{stops_text} | "
            f"Duration: "
            f"{flight['duration']}"
        )

    return "\n".join(output)


# ============================================================
# TOOL 2: COMPARE PRICE
# ============================================================

def compare_price(options: str) -> str:
    """
    Rank flight options from cheapest to most expensive.

    Parameters
    ----------
    options : str
        Output returned by search_flights().

    Returns
    -------
    str
        Flights ranked by price.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not options or not options.strip():

        return (
            "ERROR: No flight options were provided."
        )

    # --------------------------------------------------------
    # Find flight lines
    # --------------------------------------------------------

    lines = options.splitlines()

    flight_lines = []

    for line in lines:

        stripped = line.strip()

        # Flight lines look like:
        #
        # 1. IndiGo | DEL → BOM | ...
        #
        if (
            stripped
            and stripped[0].isdigit()
            and "." in stripped[:4]
        ):

            flight_lines.append(
                stripped
            )

    # --------------------------------------------------------
    # No comparable flights
    # --------------------------------------------------------

    if not flight_lines:

        return (
            "ERROR: No comparable flight "
            "options found."
        )

    # --------------------------------------------------------
    # Extract price
    # --------------------------------------------------------

    def extract_price(line):

        try:

            # Find everything after ₹
            price_part = (
                line.split("₹", 1)[1]
                .strip()
            )

            # Match numbers including commas
            #
            # Example:
            # 6,425
            # 12,500
            #
            match = re.match(
                r"([\d,]+)",
                price_part
            )

            if match:

                price_text = (
                    match.group(1)
                    .replace(",", "")
                )

                return int(
                    price_text
                )

        except Exception:

            pass

        # Put flights without a price
        # at the end.
        return float("inf")

    # --------------------------------------------------------
    # Sort flights by price
    # --------------------------------------------------------

    sorted_lines = sorted(
        flight_lines,
        key=extract_price
    )

    # --------------------------------------------------------
    # Re-number results
    # --------------------------------------------------------

    ranked_lines = []

    for i, line in enumerate(
        sorted_lines,
        1
    ):

        # Remove original number
        cleaned_line = re.sub(
            r"^\d+\.\s*",
            "",
            line
        )

        ranked_lines.append(
            f"{i}. {cleaned_line}"
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    return (
        "Flights ranked by price:\n"
        + "\n".join(ranked_lines)
    )


# ============================================================
# TOOL REGISTRY
# ============================================================
#
# The agent is only allowed to execute
# functions present in this registry.
# ============================================================

REGISTRY = {
    "search_flights": search_flights,
    "compare_price": compare_price,
}


# ============================================================
# TOOL SCHEMA
# ============================================================
#
# This schema is provided to the LLM so it knows:
# - which tools exist
# - what arguments they require
# - what each argument means
# ============================================================

TOOL_SCHEMA = [

    {
        "type": "function",

        "function": {

            "name": "search_flights",

            "description": (
                "Search live flight options using "
                "Google Flights through SerpApi. "
                "Use this tool whenever the user "
                "needs actual flight availability "
                "or prices."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "from_city": {
                        "type": "string",
                        "description": (
                            "Origin city or airport "
                            "code, for example Delhi "
                            "or DEL."
                        ),
                    },

                    "to_city": {
                        "type": "string",
                        "description": (
                            "Destination city or airport "
                            "code, for example Mumbai "
                            "or BOM."
                        ),
                    },

                    "departure_date": {
                        "type": "string",
                        "description": (
                            "Departure date in "
                            "YYYY-MM-DD format."
                        ),
                    },

                    "return_date": {
                        "type": "string",
                        "description": (
                            "Optional return date in "
                            "YYYY-MM-DD format. "
                            "Leave unspecified for "
                            "one-way travel."
                        ),
                    },

                    "passengers": {
                        "type": "integer",
                        "description": (
                            "Number of adult passengers."
                        ),
                    },

                    "cabin_class": {
                        "type": "string",
                        "description": (
                            "Cabin class: economy, "
                            "premium economy, business, "
                            "or first."
                        ),
                    },
                },

                "required": [
                    "from_city",
                    "to_city",
                    "departure_date",
                    "passengers",
                    "cabin_class",
                ],
            },
        },
    },

    {
        "type": "function",

        "function": {

            "name": "compare_price",

            "description": (
                "Compare flight options and rank "
                "them from cheapest to most expensive."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "options": {
                        "type": "string",
                        "description": (
                            "Flight search results returned "
                            "by search_flights."
                        ),
                    },

                },

                "required": [
                    "options"
                ],
            },
        },
    },
]