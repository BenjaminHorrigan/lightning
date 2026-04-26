% ============================================================================
% USML Categories I, II, III — Firearms, Guns/Armament, Ammunition/Ordnance
% Source: 22 CFR 121.1, Categories I, II, III
% ============================================================================

% ============================================================================
% Category I(a) — Nonautomatic, semiautomatic, and fully automatic firearms
% to and including .50 caliber (12.7 mm)
% 22 CFR 121.1 Category I(a)
% ============================================================================

category_i_a_firearm("machine_gun").
category_i_a_firearm("submachine_gun").
category_i_a_firearm("assault_rifle").
category_i_a_firearm("battle_rifle").
category_i_a_firearm("combat_shotgun").
category_i_a_firearm("military_pistol").
category_i_a_firearm("military_revolver").
category_i_a_firearm("select_fire_rifle").
category_i_a_firearm("light_machine_gun").

classified(C, "USML_I_a", "22 CFR 121.1 Category I(a)") :-
    component(C),
    component_category(C, Cat),
    category_i_a_firearm(Cat).

% ============================================================================
% Category I(b) — Firearms using caseless ammunition
% 22 CFR 121.1 Category I(b)
% ============================================================================

category_i_b_firearm("caseless_ammunition_firearm").
category_i_b_firearm("caseless_rifle").

classified(C, "USML_I_b", "22 CFR 121.1 Category I(b)") :-
    component(C),
    component_category(C, Cat),
    category_i_b_firearm(Cat).

% ============================================================================
% Category I(c) — Firearms and components: automatic conversion kits,
% suppressors/silencers, barrels
% 22 CFR 121.1 Category I(c)
% ============================================================================

category_i_c_component("suppressor").
category_i_c_component("silencer").
category_i_c_component("sound_suppressor").
category_i_c_component("automatic_conversion_kit").
category_i_c_component("auto_sear").
category_i_c_component("swift_link").
category_i_c_component("forced_reset_trigger_auto").
category_i_c_component("lightning_link_auto").
category_i_c_component("military_barrel_heavy").
category_i_c_component("military_receiver").

classified(C, "USML_I_c", "22 CFR 121.1 Category I(c)") :-
    component(C),
    component_category(C, Cat),
    category_i_c_component(Cat).

% ============================================================================
% Category I(f) — Fully automatic firearms > .50 caliber (12.7 mm)
% 22 CFR 121.1 Category I(f)
% ============================================================================

category_i_f_firearm("heavy_machine_gun").
category_i_f_firearm("autocannon").
category_i_f_firearm("gatling_gun").
category_i_f_firearm("minigun").
category_i_f_firearm("rotary_cannon_small").

% Numerical threshold: caliber > 12.7 mm but <= 20 mm (above 20 mm is Cat II)
classified(C, "USML_I_f", "22 CFR 121.1 Category I(f)") :-
    component(C),
    component_category(C, Cat),
    category_i_f_firearm(Cat).

% Performance-based: caliber in mm * 10 (to avoid floats), > 127 (>12.7mm) and <= 200 (<=20mm)
classified(C, "USML_I_f", "22 CFR 121.1 Category I(f)") :-
    component(C),
    performance(C, "caliber_mm_x10", Cal),
    Cal > 127,
    Cal <= 200.

% ============================================================================
% Category I(j) — Components for firearms in I(a)–I(f):
% barrels, stocks, frames, bolts, bolt carriers, slides, cylinders
% 22 CFR 121.1 Category I(j)
% ============================================================================

category_i_j_part("firearm_barrel").
category_i_j_part("firearm_stock").
category_i_j_part("firearm_frame").
category_i_j_part("firearm_receiver").
category_i_j_part("firearm_bolt").
category_i_j_part("firearm_bolt_carrier").
category_i_j_part("firearm_slide").
category_i_j_part("firearm_cylinder").
category_i_j_part("firearm_trigger_group").
category_i_j_part("firearm_lower_receiver").
category_i_j_part("firearm_upper_receiver").

classified(C, "USML_I_j", "22 CFR 121.1 Category I(j)") :-
    component(C),
    component_category(C, Cat),
    category_i_j_part(Cat),
    specially_designed_for_cat_i(C).

% A component is specially designed for Cat I if its parent system is a Cat I firearm
specially_designed_for_cat_i(C) :-
    component(C),
    parent_system(C, S),
    system(S),
    system_type(S, T),
    category_i_a_firearm(T).

specially_designed_for_cat_i(C) :-
    component(C),
    parent_system(C, S),
    system(S),
    system_type(S, T),
    category_i_f_firearm(T).

% ============================================================================
% Category II(a) — Guns and armament > 12.7 mm
% 22 CFR 121.1 Category II(a)
% ============================================================================

category_ii_a_item("artillery_piece").
category_ii_a_item("howitzer").
category_ii_a_item("field_gun").
category_ii_a_item("naval_gun").
category_ii_a_item("mortar_military").
category_ii_a_item("recoilless_rifle").
category_ii_a_item("antitank_gun").
category_ii_a_item("flamethrower_military").
category_ii_a_item("grenade_launcher_military").
category_ii_a_item("autocannon_large").
category_ii_a_item("cannon_military").
category_ii_a_item("antiaircraft_gun").

classified(C, "USML_II_a", "22 CFR 121.1 Category II(a)") :-
    component(C),
    component_category(C, Cat),
    category_ii_a_item(Cat).

% Numerical threshold: caliber > 12.7 mm (> 127 in x10 scale)
classified(C, "USML_II_a", "22 CFR 121.1 Category II(a)") :-
    component(C),
    component_category(C, "gun"),
    performance(C, "caliber_mm_x10", Cal),
    Cal > 127.

% ============================================================================
% Category II(b) — Military flamethrowers with range > 20 m
% 22 CFR 121.1 Category II(b)
% ============================================================================

classified(C, "USML_II_b", "22 CFR 121.1 Category II(b)") :-
    component(C),
    component_category(C, "flamethrower"),
    performance(C, "range_m", R),
    R >= 20.

% ============================================================================
% Category II(c) — Parts, components, accessories for Cat II items
% 22 CFR 121.1 Category II(c)
% ============================================================================

category_ii_c_part("artillery_barrel").
category_ii_c_part("artillery_breech").
category_ii_c_part("artillery_carriage").
category_ii_c_part("mortar_tube").
category_ii_c_part("mortar_baseplate").
category_ii_c_part("recoilless_rifle_barrel").
category_ii_c_part("cannon_mount").
category_ii_c_part("gun_sight_military").
category_ii_c_part("muzzle_brake_military").

classified(C, "USML_II_c", "22 CFR 121.1 Category II(c)") :-
    component(C),
    component_category(C, Cat),
    category_ii_c_part(Cat).

% ============================================================================
% Category III(a) — Ammunition for firearms in Cat I and Cat II
% 22 CFR 121.1 Category III(a)
% ============================================================================

category_iii_a_ammo("armor_piercing_round").
category_iii_a_ammo("explosive_projectile").
category_iii_a_ammo("incendiary_round").
category_iii_a_ammo("tracer_round").
category_iii_a_ammo("steel_core_penetrator").
category_iii_a_ammo("depleted_uranium_round").
category_iii_a_ammo("flechette_round").
category_iii_a_ammo("military_blank_cartridge").
category_iii_a_ammo("artillery_shell").
category_iii_a_ammo("mortar_bomb").
category_iii_a_ammo("naval_projectile").
category_iii_a_ammo("grenade_round").
category_iii_a_ammo("caseless_cartridge").

classified(C, "USML_III_a", "22 CFR 121.1 Category III(a)") :-
    component(C),
    component_category(C, Cat),
    category_iii_a_ammo(Cat).

% Substance-level: energetic fill in projectiles
classified(S, "USML_III_a", "22 CFR 121.1 Category III(a)") :-
    substance(S),
    attribute(S, "explosive_projectile_fill").

% ============================================================================
% Category III(b) — Cartridge cases, powder bags, primers for Cat II weapons
% 22 CFR 121.1 Category III(b)
% ============================================================================

category_iii_b_part("artillery_cartridge_case").
category_iii_b_part("powder_bag_propellant").
category_iii_b_part("primer_artillery").
category_iii_b_part("fuze_military").
category_iii_b_part("point_detonating_fuze").
category_iii_b_part("proximity_fuze").
category_iii_b_part("time_fuze_military").

classified(C, "USML_III_b", "22 CFR 121.1 Category III(b)") :-
    component(C),
    component_category(C, Cat),
    category_iii_b_part(Cat).

% ============================================================================
% NFA items — National Firearms Act, 26 USC 5845
% Encoded here as they share the Cat I/II physical items domain
% ============================================================================

% 26 USC 5845(b) — Machine guns (automatic fire)
classified(C, "NFA_machinegun", "26 USC 5845(b)") :-
    component(C),
    attribute(C, "automatic_fire_capable").

classified(C, "NFA_machinegun", "26 USC 5845(b)") :-
    component(C),
    component_category(C, "machine_gun").

classified(C, "NFA_machinegun", "26 USC 5845(b)") :-
    component(C),
    component_category(C, Cat),
    category_i_a_firearm(Cat),
    attribute(C, "fully_automatic").

% 26 USC 5845(a)(3) — Short-barreled rifles (barrel < 16 inches)
classified(C, "NFA_sbr", "26 USC 5845(a)(3)") :-
    component(C),
    component_category(C, "rifle"),
    performance(C, "barrel_length_inches_x10", BL),
    BL < 160.

% 26 USC 5845(a)(2) — Short-barreled shotguns (barrel < 18 inches)
classified(C, "NFA_sbs", "26 USC 5845(a)(2)") :-
    component(C),
    component_category(C, "shotgun"),
    performance(C, "barrel_length_inches_x10", BL),
    BL < 180.

% 26 USC 5845(a)(1) — Suppressors/silencers
classified(C, "NFA_suppressor", "26 USC 5845(a)(1)") :-
    component(C),
    component_category(C, "suppressor").

classified(C, "NFA_suppressor", "26 USC 5845(a)(1)") :-
    component(C),
    component_category(C, "silencer").

% 26 USC 5845(f) — Destructive devices: bore > 0.5 inch (grenades, rockets, bombs)
% Bore > 0.5 inch = caliber_mm_x10 > 127 (12.7mm) for the destructive device test
classified(C, "NFA_destructive_device", "26 USC 5845(f)") :-
    component(C),
    component_category(C, Cat),
    category_iii_a_ammo(Cat),
    performance(C, "caliber_mm_x10", Cal),
    Cal > 127.

classified(C, "NFA_destructive_device", "26 USC 5845(f)") :-
    component(C),
    component_category(C, "grenade").

classified(C, "NFA_destructive_device", "26 USC 5845(f)") :-
    component(C),
    component_category(C, "bomb_military").

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
#show specially_designed_for_cat_i/1.
