"""
Airfare Intelligence Platform
Common schema definitions and constants.

All data — historical, demo, or live — must conform to this schema
before being stored or used in calculations.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

# ── IATA airport codes for major Indian airports ──────────────
IATA_CITY_MAP: dict[str, str] = {
    # Code → Full Name
    "DEL": "Delhi (Indira Gandhi Intl)",
    "BOM": "Mumbai (Chhatrapati Shivaji Maharaj Intl)",
    "BLR": "Bengaluru (Kempegowda Intl)",
    "HYD": "Hyderabad (Rajiv Gandhi Intl)",
    "MAA": "Chennai (Chennai Intl)",
    "CCU": "Kolkata (Netaji Subhas Chandra Bose Intl)",
    "COK": "Kochi (Cochin Intl)",
    "GOI": "Goa (Goa Intl / Mopa)",
    "PNQ": "Pune (Pune Airport)",
    "AMD": "Ahmedabad (Sardar Vallabhbhai Patel Intl)",
    "JAI": "Jaipur (Jaipur Intl)",
    "LKO": "Lucknow (Chaudhary Charan Singh Intl)",
    "PAT": "Patna (Jay Prakash Narayan Intl)",
    "BBI": "Bhubaneswar (Biju Patnaik Intl)",
    "IXC": "Chandigarh (Shaheed Bhagat Singh Intl)",
    "SXR": "Srinagar (Sheikh ul-Alam Intl)",
    "GAU": "Guwahati (Lokpriya Gopinath Bordoloi Intl)",
    "NAG": "Nagpur (Dr. Babasaheb Ambedkar Intl)",
    "VNS": "Varanasi (Lal Bahadur Shastri Intl)",
    "TRV": "Thiruvananthapuram (Trivandrum Intl)",
    "VTZ": "Visakhapatnam (Visakhapatnam Airport)",
    "RPR": "Raipur (Swami Vivekananda Airport)",
    "IXB": "Bagdogra (Bagdogra Airport)",
    "DIB": "Dibrugarh (Dibrugarh Airport)",
    "DED": "Dehradun (Jolly Grant Airport)",
    "IXR": "Ranchi (Birsa Munda Airport)",
    "BHO": "Bhopal (Raja Bhoj Airport)",
    "IDR": "Indore (Devi Ahilyabai Holkar Airport)",
    "BDQ": "Vadodara (Vadodara Airport)",
    "STV": "Surat (Surat Airport)",
    "ATQ": "Amritsar (Sri Guru Ram Dass Jee Intl)",
}

# Canonical airline name mapping (normalize scraper/API variations)
AIRLINE_NAME_MAP: dict[str, str] = {
    # Raw name → Canonical name
    "indigo": "IndiGo",
    "Indigo": "IndiGo",
    "INDIGO": "IndiGo",
    "6E": "IndiGo",
    "air india": "Air India",
    "Air India": "Air India",
    "AI": "Air India",
    "air india express": "Air India Express",
    "Air India Express": "Air India Express",
    "Air-India Express": "Air India Express",
    "IX": "Air India Express",
    "vistara": "Vistara",
    "Vistara": "Vistara",
    "UK": "Vistara",
    "air asia": "AirAsia India",
    "AirAsia": "AirAsia India",
    "AirAsia India": "AirAsia India",
    "I5": "AirAsia India",
    "spicejet": "SpiceJet",
    "SpiceJet": "SpiceJet",
    "SG": "SpiceJet",
    "go first": "Go First",
    "GoFirst": "Go First",
    "Go First": "Go First",
    "G8": "Go First",
    "akasa": "Akasa Air",
    "Akasa": "Akasa Air",
    "Akasa Air": "Akasa Air",
    "QP": "Akasa Air",
    "star air": "Star Air",
    "Star Air": "Star Air",
    "S5": "Star Air",
    "alliance air": "Alliance Air",
    "Alliance Air": "Alliance Air",
    "9I": "Alliance Air",
    "blue dart": "Blue Dart Aviation",
    "trujet": "TruJet",
}

# Cabin class normalization
CABIN_CLASS_MAP: dict[str, str] = {
    "economy": "Economy",
    "Economy": "Economy",
    "ECONOMY": "Economy",
    "eco": "Economy",
    "Y": "Economy",
    "business": "Business",
    "Business": "Business",
    "BUSINESS": "Business",
    "biz": "Business",
    "J": "Business",
    "C": "Business",
    "first": "First",
    "First": "First",
    "FIRST": "First",
    "F": "First",
    "premium economy": "Premium Economy",
    "Premium Economy": "Premium Economy",
    "PREMIUM_ECONOMY": "Premium Economy",
    "W": "Premium Economy",
}

# Data source identifiers — used in `source` field to keep provenance clear
class DataSource:
    KAGGLE_HISTORICAL = "kaggle_historical"       # Kaggle Flight Price Prediction dataset
    GITHUB_HISTORICAL = "github_historical"        # GitHub flight-fare-analysis (Avij112)
    AMADEUS_LIVE = "amadeus"                       # Amadeus Flight Offers Search API (live)
    DEMO = "demo"                                  # Synthetic/seeded demo data
    HISTORICAL_AUGMENTED = "historical_augmented"  # Synthetic augmentation

    # SIH 26056 Provenance Classification Tags
    REAL_API = "REAL_API"                         # Live authorized GDS/Airline API
    HISTORICAL_SNAPSHOT = "HISTORICAL_SNAPSHOT"   # Kaggle/GitHub archival dataset
    SYNTHETIC_AUGMENTED = "SYNTHETIC_AUGMENTED"   # Synthetic route expansion
    SYNTHETIC_DEMO = "SYNTHETIC_DEMO"             # Controlled yield curve simulation
    DGCA_STATUTORY_PUBLIC = "DGCA_STATUTORY_PUBLIC" # Official DGCA Gazette Fare Caps

# Stops normalization
STOPS_MAP: dict[str, int] = {
    "non-stop": 0,
    "nonstop": 0,
    "direct": 0,
    "0": 0,
    "1 stop": 1,
    "1stop": 1,
    "1": 1,
    "2 stops": 2,
    "2stops": 2,
    "2": 2,
    "3 stops": 3,
    "3": 3,
}


@dataclass
class NormalizedFareObservation:
    """
    Common schema for a single airfare observation.
    All data sources must be normalized to this schema.
    Complies with SIH 26056 Requirement 4 (full fare breakdown & metadata).
    """
    source: str                          # DataSource constant
    airline: str                         # Canonical airline name
    origin: str                          # IATA code (3-letter)
    destination: str                     # IATA code (3-letter)
    travel_date: date                    # Date of travel (departure)
    booking_date: Optional[date]         # Date fare was observed/booked
    departure_time: Optional[str]        # HH:MM format
    arrival_time: Optional[str]          # HH:MM format
    stops: int                           # Number of stops (0 = non-stop)
    duration_minutes: Optional[int]      # Total flight duration in minutes
    cabin_class: str                     # Economy / Business / First / Premium Economy
    fare: float                          # Total Fare in INR
    base_fare: Optional[float] = None    # Base airfare excluding statutory taxes
    taxes: Optional[float] = None        # Statutory taxes (GST, etc.)
    airport_fees: Optional[float] = None # Passenger Service Fee / UDF
    service_charge: Optional[float] = None # Fuel surcharge / convenience fee
    flight_number: Optional[str] = None  # e.g. "6E-205", "AI-101"
    availability: bool = True            # Available seat inventory indicator
    source_provenance: Optional[str] = None # REAL_API / HISTORICAL_SNAPSHOT / SYNTHETIC_DEMO
    currency: str = "INR"
    collected_at: datetime = field(default_factory=datetime.utcnow)
    days_left: Optional[int] = None      # Days between booking and travel

    def __post_init__(self):
        if self.days_left is None and self.booking_date and self.travel_date:
            delta = (self.travel_date - self.booking_date)
            self.days_left = max(0, delta.days)
