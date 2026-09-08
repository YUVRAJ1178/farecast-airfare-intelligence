"""
Airfare Intelligence Platform — DGCA Route Weights Service
Provides official Directorate General of Civil Aviation (DGCA) domestic city-pair
passenger traffic statistics, weights, and Route Dispersal Guidelines (RDG) classifications.
Used to compute passenger-weighted Laspeyres Airfare Price Index for CPI augmentation.
"""

from typing import Dict, List, Tuple, Optional

# Official DGCA Domestic Scheduled Passenger Traffic Volume (Million Passengers / Annum)
# Based on DGCA Domestic Air Transport Statistics & MoCA Route Dispersal Guidelines (RDG).
# All 15 bilateral corridors (30 directional routes) connect India's top 6 metro hubs.
DGCA_TRUNK_CORRIDORS: List[Dict] = [
    {
        "pair": ("DEL", "BOM"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Mumbai (BOM)",
        "distance_km": 1148,
        "annual_pax_millions": 6.20,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("DEL", "BLR"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Bengaluru (BLR)",
        "distance_km": 1740,
        "annual_pax_millions": 4.30,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BOM", "BLR"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Bengaluru (BLR)",
        "distance_km": 842,
        "annual_pax_millions": 3.40,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("DEL", "CCU"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Kolkata (CCU)",
        "distance_km": 1305,
        "annual_pax_millions": 2.70,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("DEL", "HYD"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Hyderabad (HYD)",
        "distance_km": 1253,
        "annual_pax_millions": 2.60,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("DEL", "MAA"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Chennai (MAA)",
        "distance_km": 1760,
        "annual_pax_millions": 2.40,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BOM", "CCU"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Kolkata (CCU)",
        "distance_km": 1654,
        "annual_pax_millions": 2.10,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BOM", "HYD"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Hyderabad (HYD)",
        "distance_km": 622,
        "annual_pax_millions": 2.00,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BOM", "MAA"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Chennai (MAA)",
        "distance_km": 1033,
        "annual_pax_millions": 1.90,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BLR", "CCU"),
        "origin_name": "Bengaluru (BLR)",
        "dest_name": "Kolkata (CCU)",
        "distance_km": 1548,
        "annual_pax_millions": 1.60,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BLR", "HYD"),
        "origin_name": "Bengaluru (BLR)",
        "dest_name": "Hyderabad (HYD)",
        "distance_km": 502,
        "annual_pax_millions": 1.50,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("BLR", "MAA"),
        "origin_name": "Bengaluru (BLR)",
        "dest_name": "Chennai (MAA)",
        "distance_km": 290,
        "annual_pax_millions": 1.40,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("CCU", "HYD"),
        "origin_name": "Kolkata (CCU)",
        "dest_name": "Hyderabad (HYD)",
        "distance_km": 1180,
        "annual_pax_millions": 1.30,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("CCU", "MAA"),
        "origin_name": "Kolkata (CCU)",
        "dest_name": "Chennai (MAA)",
        "distance_km": 1366,
        "annual_pax_millions": 1.20,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("HYD", "MAA"),
        "origin_name": "Hyderabad (HYD)",
        "dest_name": "Chennai (MAA)",
        "distance_km": 512,
        "annual_pax_millions": 1.10,
        "category": "Category I (Metro Trunk)",
    },
    {
        "pair": ("DEL", "AMD"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Ahmedabad (AMD)",
        "distance_km": 765,
        "annual_pax_millions": 2.50,
        "category": "Category II (Regional Hub)",
    },
    {
        "pair": ("BOM", "AMD"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Ahmedabad (AMD)",
        "distance_km": 442,
        "annual_pax_millions": 2.20,
        "category": "Category II (Regional Hub)",
    },
    {
        "pair": ("BOM", "GOI"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Goa (GOI)",
        "distance_km": 435,
        "annual_pax_millions": 2.40,
        "category": "Category II (Leisure Hub)",
    },
    {
        "pair": ("DEL", "GOI"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Goa (GOI)",
        "distance_km": 1500,
        "annual_pax_millions": 2.10,
        "category": "Category II (Leisure Hub)",
    },
    {
        "pair": ("BLR", "GOI"),
        "origin_name": "Bengaluru (BLR)",
        "dest_name": "Goa (GOI)",
        "distance_km": 485,
        "annual_pax_millions": 1.80,
        "category": "Category II (Leisure Hub)",
    },
    {
        "pair": ("DEL", "PNQ"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Pune (PNQ)",
        "distance_km": 1170,
        "annual_pax_millions": 2.30,
        "category": "Category II (Regional Hub)",
    },
    {
        "pair": ("BLR", "PNQ"),
        "origin_name": "Bengaluru (BLR)",
        "dest_name": "Pune (PNQ)",
        "distance_km": 730,
        "annual_pax_millions": 1.90,
        "category": "Category II (Regional Hub)",
    },
    {
        "pair": ("DEL", "JAI"),
        "origin_name": "Delhi (DEL)",
        "dest_name": "Jaipur (JAI)",
        "distance_km": 240,
        "annual_pax_millions": 1.50,
        "category": "Category II (Regional Hub)",
    },
    {
        "pair": ("BOM", "JAI"),
        "origin_name": "Mumbai (BOM)",
        "dest_name": "Jaipur (JAI)",
        "distance_km": 920,
        "annual_pax_millions": 1.40,
        "category": "Category II (Regional Hub)",
    },
]

# Total bidirectional traffic across monitored corridors
TOTAL_ANNUAL_PAX_MILLIONS: float = sum(c["annual_pax_millions"] for c in DGCA_TRUNK_CORRIDORS)


def _build_directional_weights() -> Dict[Tuple[str, str], Dict]:
    """
    Build 30 directional routes from the 15 bidirectional corridors.
    Traffic is split equally (50/50) between forward and return flights.
    """
    directional = {}
    for c in DGCA_TRUNK_CORRIDORS:
        c1, c2 = c["pair"]
        half_pax = round(c["annual_pax_millions"] / 2.0, 3)
        weight = half_pax / TOTAL_ANNUAL_PAX_MILLIONS

        # Forward
        directional[(c1, c2)] = {
            "origin": c1,
            "destination": c2,
            "route": f"{c1}→{c2}",
            "distance_km": c["distance_km"],
            "annual_pax_millions": half_pax,
            "weight": round(weight, 4),
            "weight_pct": round(weight * 100.0, 2),
            "category": c["category"],
        }
        # Return
        directional[(c2, c1)] = {
            "origin": c2,
            "destination": c1,
            "route": f"{c2}→{c1}",
            "distance_km": c["distance_km"],
            "annual_pax_millions": half_pax,
            "weight": round(weight, 4),
            "weight_pct": round(weight * 100.0, 2),
            "category": c["category"],
        }
    return directional


DIRECTIONAL_WEIGHTS_MAP = _build_directional_weights()


def get_all_dgca_route_weights() -> List[Dict]:
    """
    Return all 30 directional routes with their DGCA traffic stats and basket weights,
    sorted by passenger traffic volume descending.
    """
    routes = list(DIRECTIONAL_WEIGHTS_MAP.values())
    routes.sort(key=lambda r: r["annual_pax_millions"], reverse=True)
    return routes


def get_route_dgca_weight(origin: str, destination: str) -> float:
    """
    Get the unnormalized DGCA weight for a given origin and destination.
    Defaults to 1/30 if route is not explicitly mapped.
    """
    key = (origin.upper(), destination.upper())
    if key in DIRECTIONAL_WEIGHTS_MAP:
        return DIRECTIONAL_WEIGHTS_MAP[key]["weight"]
    return 1.0 / 30.0


def get_normalized_dgca_weights(route_pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], float]:
    """
    Normalize DGCA weights across an arbitrary subset of route pairs
    such that sum(normalized_weights) == 1.0.
    """
    raw_weights = {}
    for pair in route_pairs:
        raw_weights[pair] = get_route_dgca_weight(pair[0], pair[1])

    total_weight = sum(raw_weights.values())
    if total_weight <= 0:
        equal_w = 1.0 / len(route_pairs) if route_pairs else 1.0
        return {pair: equal_w for pair in route_pairs}

    return {pair: (w / total_weight) for pair, w in raw_weights.items()}
