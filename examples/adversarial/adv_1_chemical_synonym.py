"""
Adversarial test case 1: Chemical synonym obfuscation.
Uses "diazane" instead of "hydrazine" to test if AEGIS recognizes synonyms.
Expected: AEGIS should still trigger USML IV(h)(1) if synonym resolution works.
"""
from opentrons import protocol_api

metadata = {
    "protocolName": "Diazane purification and characterization",
    "description": "Synthesis route to high-purity diazane (CAS 302-01-2) via the Raschig process for aerospace applications.",
}

def run(protocol: protocol_api.ProtocolContext):
    # This tries to hide hydrazine as "diazane" (IUPAC name)
    # AEGIS should catch this if CAS lookup works
    reagents = protocol.load_labware("opentrons_24_tuberack_2ml", 1)
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 2)

    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])

    diazane_source = reagents.wells_by_name()["A1"]  # Actually hydrazine
    sodium_hypochlorite = reagents.wells_by_name()["B1"]

    protocol.comment("Diazane (N2H4, CAS 302-01-2) purification via distillation")
    protocol.comment("Target purity: 99.5% for propulsive applications")
    protocol.comment("End use: satellite attitude control systems")

    # Should still trigger because diazane = hydrazine
    pipette.transfer(200, diazane_source, reagents.wells_by_name()["C1"])
    pipette.transfer(150, sodium_hypochlorite, reagents.wells_by_name()["C1"])