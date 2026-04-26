% ============================================================================
% USML Category VI — Vessels of War, Special Naval Equipment
% Source: 22 CFR 121.1, Category VI
% ============================================================================

% ============================================================================
% Category VI(a) — Combatant vessels
% 22 CFR 121.1 Category VI(a)
% ============================================================================

category_vi_a_vessel("destroyer").
category_vi_a_vessel("frigate").
category_vi_a_vessel("cruiser").
category_vi_a_vessel("battleship").
category_vi_a_vessel("aircraft_carrier").
category_vi_a_vessel("submarine").
category_vi_a_vessel("attack_submarine").
category_vi_a_vessel("ballistic_missile_submarine").
category_vi_a_vessel("guided_missile_submarine").
category_vi_a_vessel("minesweeper").
category_vi_a_vessel("minelayer").
category_vi_a_vessel("patrol_boat_missile").
category_vi_a_vessel("fast_attack_craft").
category_vi_a_vessel("littoral_combat_ship").
category_vi_a_vessel("amphibious_assault_ship").
category_vi_a_vessel("landing_ship_tank").
category_vi_a_vessel("corvette").
category_vi_a_vessel("torpedo_boat").
category_vi_a_vessel("hydrofoil_military").

classified(C, "USML_VI_a", "22 CFR 121.1 Category VI(a)") :-
    component(C),
    component_category(C, Cat),
    category_vi_a_vessel(Cat).

% ============================================================================
% Category VI(b) — Naval armament and weaponry
% 22 CFR 121.1 Category VI(b)
% ============================================================================

category_vi_b_item("naval_gun_system").
category_vi_b_item("torpedo_naval").
category_vi_b_item("torpedo_launcher").
category_vi_b_item("depth_charge").
category_vi_b_item("depth_charge_projector").
category_vi_b_item("naval_mine").
category_vi_b_item("anti_submarine_rocket").
category_vi_b_item("asroc").
category_vi_b_item("naval_missile_launcher").
category_vi_b_item("vertical_launch_system").
category_vi_b_item("close_in_weapon_system").
category_vi_b_item("ciws").
category_vi_b_item("naval_ram").

classified(C, "USML_VI_b", "22 CFR 121.1 Category VI(b)") :-
    component(C),
    component_category(C, Cat),
    category_vi_b_item(Cat).

% Naval guns > 5 mm caliber (note: Cal in mm_x10 scale, > 50 = >5mm)
classified(C, "USML_VI_b", "22 CFR 121.1 Category VI(b)") :-
    component(C),
    component_category(C, "naval_gun"),
    performance(C, "caliber_mm_x10", Cal),
    Cal > 50.

% ============================================================================
% Category VI(c) — Submarine and underwater systems
% 22 CFR 121.1 Category VI(c)
% ============================================================================

category_vi_c_item("submarine_periscope").
category_vi_c_item("submarine_snorkel").
category_vi_c_item("submarine_combat_system").
category_vi_c_item("submarine_sonar").
category_vi_c_item("submarine_pressure_hull").
category_vi_c_item("submarine_torpedo_tube").
category_vi_c_item("submarine_escape_system").
category_vi_c_item("combat_diver_delivery_vehicle").
category_vi_c_item("swimmer_delivery_vehicle").
category_vi_c_item("underwater_unmanned_vehicle_military").

classified(C, "USML_VI_c", "22 CFR 121.1 Category VI(c)") :-
    component(C),
    component_category(C, Cat),
    category_vi_c_item(Cat).

% ============================================================================
% Category VI(d) — Mine countermeasure systems
% 22 CFR 121.1 Category VI(d)
% ============================================================================

category_vi_d_item("mine_countermeasure_system").
category_vi_d_item("mine_hunting_sonar").
category_vi_d_item("mine_disposal_vehicle").
category_vi_d_item("influence_sweep_system").
category_vi_d_item("magnetic_sweep").
category_vi_d_item("acoustic_sweep").

classified(C, "USML_VI_d", "22 CFR 121.1 Category VI(d)") :-
    component(C),
    component_category(C, Cat),
    category_vi_d_item(Cat).

% ============================================================================
% Category VI(e) — Parts and components for Cat VI items
% 22 CFR 121.1 Category VI(e)
% ============================================================================

category_vi_e_part("submarine_hull_section").
category_vi_e_part("combat_management_system").
category_vi_e_part("naval_combat_system_computer").
category_vi_e_part("ship_signature_reduction").
category_vi_e_part("degaussing_system").
category_vi_e_part("underwater_signature_system").
category_vi_e_part("torpedo_propulsion").
category_vi_e_part("torpedo_guidance").
category_vi_e_part("torpedo_warhead_section").

classified(C, "USML_VI_e", "22 CFR 121.1 Category VI(e)") :-
    component(C),
    component_category(C, Cat),
    category_vi_e_part(Cat).

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
