% ============================================================================
% USML Category VII — Tanks and Military Vehicles
% Source: 22 CFR 121.1, Category VII
% ============================================================================

% ============================================================================
% Category VII(a) — Tanks and military motor vehicles with armor or weapons
% 22 CFR 121.1 Category VII(a)
% ============================================================================

category_vii_a_vehicle("main_battle_tank").
category_vii_a_vehicle("tank").
category_vii_a_vehicle("armored_personnel_carrier").
category_vii_a_vehicle("infantry_fighting_vehicle").
category_vii_a_vehicle("armored_fighting_vehicle").
category_vii_a_vehicle("light_armored_vehicle").
category_vii_a_vehicle("armored_car_military").
category_vii_a_vehicle("self_propelled_howitzer").
category_vii_a_vehicle("self_propelled_gun").
category_vii_a_vehicle("self_propelled_mortar").
category_vii_a_vehicle("armored_command_vehicle").
category_vii_a_vehicle("armored_recovery_vehicle").
category_vii_a_vehicle("armored_ambulance").
category_vii_a_vehicle("mine_resistant_ambush_protected").
category_vii_a_vehicle("mrap").
category_vii_a_vehicle("high_mobility_multipurpose_wheeled").
category_vii_a_vehicle("humvee_armed").

classified(C, "USML_VII_a", "22 CFR 121.1 Category VII(a)") :-
    component(C),
    component_category(C, Cat),
    category_vii_a_vehicle(Cat).

% ============================================================================
% Category VII(b) — Military trucks > 2.5 ton tactical payload
% 22 CFR 121.1 Category VII(b)
% ============================================================================

% Payload threshold: > 2.5 ton = > 2500 kg
classified(C, "USML_VII_b", "22 CFR 121.1 Category VII(b)") :-
    component(C),
    component_category(C, "military_truck"),
    performance(C, "payload_kg", P),
    P > 2500.

classified(C, "USML_VII_b", "22 CFR 121.1 Category VII(b)") :-
    component(C),
    component_category(C, "tactical_truck").

classified(C, "USML_VII_b", "22 CFR 121.1 Category VII(b)") :-
    component(C),
    component_category(C, "military_logistics_vehicle").

% ============================================================================
% Category VII(c) — Military engineering vehicles
% 22 CFR 121.1 Category VII(c)
% ============================================================================

category_vii_c_vehicle("bridgelayer_vehicle").
category_vii_c_vehicle("armored_bridgelayer").
category_vii_c_vehicle("mine_plow_vehicle").
category_vii_c_vehicle("mine_roller_vehicle").
category_vii_c_vehicle("combat_engineer_vehicle").
category_vii_c_vehicle("armored_dozer").
category_vii_c_vehicle("countermine_vehicle").
category_vii_c_vehicle("armored_breacher").

classified(C, "USML_VII_c", "22 CFR 121.1 Category VII(c)") :-
    component(C),
    component_category(C, Cat),
    category_vii_c_vehicle(Cat).

% ============================================================================
% Category VII(d) — Parts and components specially designed for Cat VII items
% including armor, active protection, reactive armor
% 22 CFR 121.1 Category VII(d)
% ============================================================================

category_vii_d_part("reactive_armor").
category_vii_d_part("explosive_reactive_armor").
category_vii_d_part("active_protection_system").
category_vii_d_part("trophy_system").
category_vii_d_part("arena_system").
category_vii_d_part("soft_kill_protection").
category_vii_d_part("hard_kill_protection").
category_vii_d_part("tank_turret").
category_vii_d_part("tank_gun_system").
category_vii_d_part("tank_fire_control_system").
category_vii_d_part("tank_stabilization_system").
category_vii_d_part("armored_vehicle_hull").
category_vii_d_part("composite_armor_plate").
category_vii_d_part("ceramic_armor_ballistic").
category_vii_d_part("vehicle_underbody_armor").
category_vii_d_part("slat_armor").
category_vii_d_part("cage_armor").

classified(C, "USML_VII_d", "22 CFR 121.1 Category VII(d)") :-
    component(C),
    component_category(C, Cat),
    category_vii_d_part(Cat).

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
