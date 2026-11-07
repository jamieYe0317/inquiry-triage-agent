"""Fixed facts about the fictional company: products, teams, and the document index.

Everything here is invented. Fernhollow Equipment Supply is not a real company.
"""

from __future__ import annotations

COMPANY = "Fernhollow Equipment Supply"

PRODUCTS: dict[str, str] = {
    "FH-210": "FH-210 log splitter (22-ton, gas engine, hydraulic ram)",
    "FH-340": "FH-340 wood chipper (3-inch capacity, gas engine, belt-driven drum)",
    "FH-520": "FH-520 stump grinder (gas engine, belt-driven cutter wheel with carbide teeth)",
    "FH-P90": "FH-P90 pressure washer (3,100 PSI, gas engine, axial pump)",
    "FH-G7": "FH-G7 portable generator (7,000 running watts, gas engine)",
}

# source_type values. The retrieval policy in policy.py allows a subset per inquiry type.
SOURCE_TYPES = ("manual", "troubleshooting", "warranty", "partner", "quality", "general")

# The document index. The Markdown files in data/docs/ are the source of truth at run time;
# tests check that every ID here has a file and that the front matter agrees.
# `brief` is the writing brief that the synthetic documents were written from.
DOC_INDEX: list[dict] = [
    # --- product manuals ---
    {
        "id": "man-fh210",
        "title": "FH-210 Log Splitter Owner's Manual",
        "source_type": "manual",
        "products": ["FH-210"],
        "brief": "Specs (22-ton force, 25-inch max log length, 6.5 hp engine, AW-32 hydraulic fluid). "
        "Setup, safe operation (two-hand control, stand clear of the wedge, never split knotty "
        "logs at an angle), daily checks, maintenance schedule (engine oil every 50 hours, "
        "hydraulic fluid every 150 hours, grease the beam), storage.",
    },
    {
        "id": "man-fh340",
        "title": "FH-340 Wood Chipper Owner's Manual",
        "source_type": "manual",
        "products": ["FH-340"],
        "brief": "Specs (3-inch branch capacity, 7 hp engine, two reversible chipper blades, drive "
        "belt). Setup, safe feeding (never reach into the hopper, feed butt end first), "
        "maintenance (blade inspection every 25 hours, belt tension check, oil every 50 "
        "hours), blade removal and reversal steps, storage.",
    },
    {
        "id": "man-fh520",
        "title": "FH-520 Stump Grinder Owner's Manual",
        "source_type": "manual",
        "products": ["FH-520"],
        "brief": "Specs (14 hp engine, 12-inch cutter wheel, 16 carbide teeth, drive belt). Setup, "
        "safe operation (call before you dig for buried lines, debris shield on, keep "
        "bystanders 50 feet away), tooth rotation and replacement, belt tension, maintenance "
        "schedule, storage.",
    },
    {
        "id": "man-fhp90",
        "title": "FH-P90 Pressure Washer Owner's Manual",
        "source_type": "manual",
        "products": ["FH-P90"],
        "brief": "Specs (3,100 PSI, 2.5 GPM, axial pump, 5 quick-connect nozzles, 25-foot hose). Setup, "
        "safe use (never point at people, high-pressure injection risk, release trigger "
        "lock), winterizing the pump with pump saver, pump oil, maintenance schedule.",
    },
    {
        "id": "man-fhg7",
        "title": "FH-G7 Portable Generator Owner's Manual",
        "source_type": "manual",
        "products": ["FH-G7"],
        "brief": "Specs (7,000 running / 9,000 starting watts, 6-gallon tank, low-oil shutdown sensor, "
        "two 20A outlets, one 30A outlet, breakers). Carbon monoxide warning (outdoors only, "
        "20 feet from windows), grounding, never backfeed a house without a transfer switch, "
        "oil change every 100 hours, storage with fuel stabilizer.",
    },
    # --- troubleshooting guides ---
    {
        "id": "ts-fh210-hydraulic",
        "title": "FH-210 Troubleshooting: Hydraulic Problems",
        "source_type": "troubleshooting",
        "products": ["FH-210"],
        "brief": "Symptoms: ram moves slowly, ram stalls on a log, weak splitting force, ram will not "
        "return, hydraulic fluid leak at hose fittings or cylinder, whining pump, foamy fluid. "
        "Causes and checks: low fluid, air in the system, wrong fluid, cold fluid, clogged "
        "filter, loose fittings, worn cylinder seals, relief valve. Steps in order. When to "
        "stop and contact the Service desk.",
    },
    {
        "id": "ts-fh340-jam",
        "title": "FH-340 Troubleshooting: Jams and Clogging",
        "source_type": "troubleshooting",
        "products": ["FH-340"],
        "brief": "Symptoms: hopper jams, discharge chute clogs, branches stall the drum, green or "
        "stringy wood wraps around the drum, engine bogs down. Causes: wet or leafy material, "
        "feeding too fast, dull blades, loose belt. Steps: shut off engine, remove spark plug "
        "wire, wait for full stop, clear with a stick, never with hands. Prevention tips.",
    },
    {
        "id": "ts-fh340-vibration",
        "title": "FH-340 Troubleshooting: Vibration, Belts, and Blades",
        "source_type": "troubleshooting",
        "products": ["FH-340"],
        "brief": "Symptoms: heavy vibration, rattling, uneven or stringy chips, drum does not spin while "
        "engine runs, belt squeal or burning-rubber smell, belt slipping. Causes: dull or "
        "chipped blades, loose blade bolts, worn or loose belt, damaged drum bearing. Steps "
        "and when to stop using the machine.",
    },
    {
        "id": "ts-fh520-teeth",
        "title": "FH-520 Troubleshooting: Cutting Performance and Belts",
        "source_type": "troubleshooting",
        "products": ["FH-520"],
        "brief": "Symptoms: slow cutting, cutter wheel stops under load, belt squeal, smoke from the "
        "belt area, broken or missing teeth, wheel wobble. Causes: worn or broken carbide "
        "teeth, loose tooth bolts, loose belt, rocks in the stump. Tooth inspection and "
        "rotation steps, belt tension steps.",
    },
    {
        "id": "ts-fhp90-pressure",
        "title": "FH-P90 Troubleshooting: Pressure and Pump Problems",
        "source_type": "troubleshooting",
        "products": ["FH-P90"],
        "brief": "Symptoms: low pressure, pulsing or surging spray, no water from wand, water leaking "
        "from the pump, hose burst or fitting leak, pump frozen after winter. Causes: "
        "clogged nozzle or inlet filter, low water supply, air in the pump, worn pump seals, "
        "unloader valve, cracked pump head from freezing. Steps in order.",
    },
    {
        "id": "ts-fhg7-nostart",
        "title": "FH-G7 Troubleshooting: Will Not Start or Shuts Off",
        "source_type": "troubleshooting",
        "products": ["FH-G7"],
        "brief": "Symptoms: engine will not start, pull cord hard to pull, engine starts then shuts "
        "off after a few minutes, engine surges. Causes: low oil level triggers the low-oil "
        "shutdown sensor, fuel valve closed, choke position, stale fuel, dirty spark plug, "
        "generator not on level ground. Steps in order.",
    },
    {
        "id": "ts-fhg7-output",
        "title": "FH-G7 Troubleshooting: No Power at the Outlets",
        "source_type": "troubleshooting",
        "products": ["FH-G7"],
        "brief": "Symptoms: engine runs but outlets give no power, breaker trips, lights flicker, "
        "voltage drops under load, burning smell or smoke from the control panel. Causes: "
        "tripped breaker, overload (starting watts), loose outlet, loss of residual "
        "magnetism, damaged wiring. A burning smell or smoke means stop and unplug "
        "everything and do not run the unit again.",
    },
    {
        "id": "ts-engine-general",
        "title": "Small Engine Troubleshooting for All Fernhollow Machines",
        "source_type": "troubleshooting",
        "products": ["FH-210", "FH-340", "FH-520", "FH-P90", "FH-G7"],
        "brief": "Shared gas-engine problems for all five machines: hard starting, will not start after "
        "storage, stale fuel and ethanol, carburetor varnish, fouled spark plug, choke use, "
        "low oil, flooded engine, engine smokes white or blue, runs rough. Steps in order "
        "and a note on what voids the warranty (wrong fuel mix is not a defect).",
    },
    # --- warranty ---
    {
        "id": "war-summary",
        "title": "Fernhollow Limited Warranty Summary",
        "source_type": "warranty",
        "products": ["FH-210", "FH-340", "FH-520", "FH-P90", "FH-G7"],
        "brief": "Coverage periods (2 years residential, 1 year commercial or rental use, 90 days on "
        "wear parts such as blades, teeth, belts, and pump seals). What is covered (defects "
        "in materials and workmanship), what is not (wear, misuse, stale fuel, freezing "
        "damage). How to start a claim: model, serial number, proof of purchase, photos. "
        "A Fernhollow staff member reviews every claim and decides the remedy. Nothing is "
        "approved until staff confirm it in writing.",
    },
    # --- partner program ---
    {
        "id": "par-overview",
        "title": "Fernhollow Partner Program Overview",
        "source_type": "partner",
        "products": [],
        "brief": "Who can join (equipment dealers, hardware and farm stores, rental companies, "
        "regional distributors). Partner types: authorized dealer, rental partner, regional "
        "distributor. What partners get in general terms (product training, marketing "
        "materials, warranty service authorization). Pricing and terms are set in a signed "
        "agreement after review by the Partner team. No prices listed.",
    },
    {
        "id": "par-apply",
        "title": "How to Apply to Become a Fernhollow Dealer or Distributor",
        "source_type": "partner",
        "products": [],
        "brief": "Application steps: online form, business license and resale certificate, store or "
        "service location details, service capability, expected annual volume, references. "
        "Review timeline (about 3 to 4 weeks), interview call, site visit for distributors. "
        "How to check application status. The Partner team makes all decisions.",
    },
    {
        "id": "par-territory",
        "title": "Partner Territory FAQ",
        "source_type": "partner",
        "products": [],
        "brief": "How territories work: regional distributors cover a set of states, dealers are not "
        "exclusive by default, exclusivity is negotiated case by case and never promised in "
        "email. Inquiries from outside the United States (Canada, Mexico) go to the Partner "
        "team for a case-by-case review. What happens when two dealers overlap.",
    },
    {
        "id": "par-tiers",
        "title": "Partner Tiers and Requirements",
        "source_type": "partner",
        "products": [],
        "brief": "Three tiers (Bronze, Silver, Gold) by annual volume, trained technicians, demo "
        "units on display, and warranty service capability. How to request a tier review. "
        "Price lists and discounts are shared only by the Partner team after an agreement "
        "is signed. No numbers for discounts or prices.",
    },
    {
        "id": "par-marketing",
        "title": "Co-op Marketing and Demo Unit Program",
        "source_type": "partner",
        "products": [],
        "brief": "Co-op marketing: partners can request support for local ads, fair booths, and "
        "signage; each request needs a plan and is approved by the Partner team. Demo unit "
        "program: how to request a demo unit, rules for display and return. No amounts.",
    },
    # --- quality and returns ---
    {
        "id": "qa-returns-dtc",
        "title": "Returns and Damaged-on-Arrival Policy for Customers",
        "source_type": "quality",
        "products": [],
        "brief": "For people who bought direct: 30-day return window for unused machines, damaged on "
        "arrival (report within 7 days with photos of the box and the machine), missing "
        "parts, defective on first use. What to send: order number, photos, model, serial "
        "number. Customer care reviews each case and decides on a repair, a part, an "
        "exchange, or a refund. No outcome is promised before review.",
    },
    {
        "id": "qa-defect-report",
        "title": "Partner Defect Report Procedure",
        "source_type": "quality",
        "products": [],
        "brief": "For dealers and distributors: how to report a defect seen on one or more units. "
        "Needed: model, serial numbers, lot or ship date, failure description, hours of use, "
        "photos, number of units affected, whether units are quarantined. The Quality team "
        "investigates, may ask for a unit to be returned for inspection, and decides on "
        "credits or replacements after the investigation.",
    },
    {
        "id": "qa-safety-escalation",
        "title": "Safety Escalation Rule",
        "source_type": "quality",
        "products": [],
        "brief": "Any report of fire, smoke, burns, fuel leaks, electric shock, parts thrown from a "
        "machine, or injury is a safety case. The receiving person tells the sender to stop "
        "using the machine, and sends the case to the Quality team the same day as urgent. "
        "Staff do not discuss fault or compensation in the first reply.",
    },
    {
        "id": "qa-freight-damage",
        "title": "Freight Damage and Shipment Discrepancy Claims",
        "source_type": "quality",
        "products": [],
        "brief": "For partner shipments on pallets: note damage on the delivery receipt before "
        "signing, photos of the pallet and units, report within 5 business days, wrong "
        "items or short quantities, keep packaging for carrier inspection. The Quality team "
        "files the carrier claim and decides on replacement stock after review.",
    },
    {
        "id": "qa-parts-replacement",
        "title": "Replacement Parts Process",
        "source_type": "quality",
        "products": [],
        "brief": "How missing or defective parts are replaced: part number from the manual's parts "
        "list, order or serial number, photos. Wrong or defective replacement parts sent to "
        "partners. Customer care or the Quality team confirms if a part is covered before "
        "it ships.",
    },
    # --- general ---
    {
        "id": "gen-shipping",
        "title": "Shipping and Order Status",
        "source_type": "general",
        "products": [],
        "brief": "Ship times (in-stock machines ship in 2 to 4 business days, freight delivery for "
        "larger machines, curbside delivery), how to track an order with the order number, "
        "what to do if tracking has not updated, address changes before shipment.",
    },
    {
        "id": "gen-contact",
        "title": "Contact Hours and Channels",
        "source_type": "general",
        "products": [],
        "brief": "Office hours (Monday to Friday, 8 AM to 5 PM Central), web form, phone line for "
        "orders, the address for mail. Use example.com addresses and 555 phone numbers only.",
    },
    {
        "id": "gen-parts-order",
        "title": "Buying Parts and Accessories",
        "source_type": "general",
        "products": [],
        "brief": "How to buy wear parts and accessories (blades, carbide teeth, belts, nozzles, wheel "
        "kits, covers): find the part number in the manual, order through the website or an "
        "authorized dealer. No prices listed.",
    },
]

DOC_IDS = [d["id"] for d in DOC_INDEX]
