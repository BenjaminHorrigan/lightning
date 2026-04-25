"""
Benign example: Palladium-catalyzed Suzuki coupling of a boronic acid with
an aryl halide. Published example, no dual-use concerns, no controlled
substances, no ITAR-relevant components.

This is the canonical "happy path" demo — every regime checked, no hits,
clean ALLOW.
"""
from opentrons import protocol_api

metadata = {
    "protocolName": "Suzuki coupling — 4-bromoanisole + phenylboronic acid",
    "author": "Demo / benign baseline",
    "description": (
        "Pd(PPh3)4-catalyzed coupling of 4-bromoanisole with phenylboronic acid "
        "in THF/water with potassium carbonate base. Target: 4-methoxybiphenyl."
    ),
    "apiLevel": "2.14",
}


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    plate = protocol.load_labware("nest_96_wellplate_2ml_deep", 2)
    reagents = protocol.load_labware("opentrons_24_tuberack_2ml", 3)

    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])

    # Reagents
    bromoanisole = reagents.wells_by_name()["A1"]  # 4-bromoanisole, 1 mmol
    phenylboronic = reagents.wells_by_name()["A2"]  # phenylboronic acid, 1.2 mmol
    catalyst = reagents.wells_by_name()["A3"]  # Pd(PPh3)4, 5 mol%
    base = reagents.wells_by_name()["A4"]  # K2CO3, 2 equiv
    solvent = reagents.wells_by_name()["A5"]  # THF/H2O 3:1

    reaction_well = plate.wells_by_name()["A1"]

    # Step 1: add solvent
    pipette.transfer(1500, solvent, reaction_well, new_tip="always")

    # Step 2: add aryl halide
    pipette.transfer(200, bromoanisole, reaction_well, new_tip="always")

    # Step 3: add boronic acid
    pipette.transfer(240, phenylboronic, reaction_well, new_tip="always")

    # Step 4: add base
    pipette.transfer(400, base, reaction_well, new_tip="always")

    # Step 5: add catalyst
    pipette.transfer(50, catalyst, reaction_well, new_tip="always")

    # Step 6: heat to 80 C for 4 hours
    protocol.comment("Heat reaction well to 80 C for 4 hours with stirring.")
    protocol.delay(minutes=240)
