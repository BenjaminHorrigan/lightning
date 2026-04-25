"""
Opentrons protocol for hydrazine-based thruster propellant development.
Should trigger:
- USML IV(h)(1): controlled propellant
- MTCR Category II: propellant production equipment
- CWC Schedule 3: hydrazine as potential precursor
"""
from opentrons import protocol_api

metadata = {
    "protocolName": "Hydrazine thruster propellant characterization",
    "author": "Propulsion Research Lab",
    "description": "Synthesis and testing of MMH/NTO bipropellant mixture for 500N thrust chamber. Target performance: 330s Isp, 8 bar chamber pressure.",
    "apiLevel": "2.14",
}

def run(protocol: protocol_api.ProtocolContext):
    # This protocol should trigger multiple regimes
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reagent_rack = protocol.load_labware("opentrons_24_tuberack_2ml", 2)
    test_cell = protocol.load_labware("custom_test_chamber", 3)  # This is the key

    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])

    # Controlled substances under multiple regimes
    monomethylhydrazine = reagent_rack.wells_by_name()["A1"]  # USML IV(h)(1)
    nitrogen_tetroxide = reagent_rack.wells_by_name()["A2"]   # USML IV(h)(1)

    # The test chamber itself should trigger MTCR production equipment
    # when parent_system is extracted as "500N thrust chamber"

    protocol.comment("BEGIN: Bipropellant mixing for thrust chamber test")
    protocol.comment("Target chamber: 500N thrust, 8 bar, Isp 330s")
    protocol.comment("End use: satellite propulsion system")

    # This should be extracted as parent_system="satellite_propulsion"
    # → system_type="rocket" → MTCR Category II

    pipette.transfer(150, monomethylhydrazine, test_cell.wells()[0])
    pipette.transfer(250, nitrogen_tetroxide, test_cell.wells()[0])

    protocol.comment("Mixture characterization: ignition delay, Isp measurement")
    protocol.delay(minutes=30)