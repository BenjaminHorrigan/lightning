% =============================================================================
% EAR Category 1 Advanced Materials Classification Rules
% Source: 15 CFR 774 - Commerce Control List Category 1 (BIS/EAR)
% =============================================================================
% Classifies advanced materials, composites, and alloys under EAR Category 1
% export controls (dual-use materials with military applications)

% Core EAR Category 1 classification
classified(S, "ear", "cat1_material", "EAR Category 1 - Advanced Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    eccn_code(S, _).

% ECCN-specific classifications
classified(S, "ear", "eccn_1c002", "ECCN 1C002 - Metal Alloys") :-
    substance(S),
    eccn_code(S, "1C002").

classified(S, "ear", "eccn_1c004", "ECCN 1C004 - Ceramic Materials") :-
    substance(S),
    eccn_code(S, "1C004").

classified(S, "ear", "eccn_1c007", "ECCN 1C007 - Ceramic Matrix Composites") :-
    substance(S),
    eccn_code(S, "1C007").

classified(S, "ear", "eccn_1c010", "ECCN 1C010 - Fibrous/Filamentary Materials") :-
    substance(S),
    eccn_code(S, "1C010").

classified(S, "ear", "eccn_1c011", "ECCN 1C011 - Refractory Metals") :-
    substance(S),
    eccn_code(S, "1C011").

classified(S, "ear", "eccn_1c116", "ECCN 1C116 - Maraging Steel") :-
    substance(S),
    eccn_code(S, "1C116").

% Material type classifications
classified(S, "ear", "composite_material", "Advanced Composite Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    item_type(S, "composite_material").
classified(S, "ear", "composite_material", "Advanced Composite Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    item_type(S, "ceramic_composite").

classified(S, "ear", "refractory_metal", "Refractory Metal") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    item_type(S, "refractory_metal").

classified(S, "ear", "superalloy", "Superalloy Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    item_type(S, "superalloy").

classified(S, "ear", "high_performance_fiber", "High Performance Fiber") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    item_type(S, "fiber").
classified(S, "ear", "high_performance_fiber", "High Performance Fiber") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    item_type(S, "glass_fiber").

% Performance-based classifications
classified(S, "ear", "ultra_high_strength", "Ultra High Strength Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    performance_threshold(S, "tensile_strength_4800_MPa").
classified(S, "ear", "ultra_high_strength", "Ultra High Strength Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    performance_threshold(S, "yield_strength_2400_MPa").

classified(S, "ear", "ultra_high_temperature", "Ultra High Temperature Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    performance_threshold(S, "melting_point_3900C").
classified(S, "ear", "ultra_high_temperature", "Ultra High Temperature Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    performance_threshold(S, "operating_temp_1200C").

classified(S, "ear", "lightweight_structural", "Lightweight Structural Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    performance_threshold(S, "density_1_85_g_per_cm3").
classified(S, "ear", "lightweight_structural", "Lightweight Structural Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    performance_threshold(S, "density_2_5_g_per_cm3").

% Strategic material classifications
classified(S, "ear", "aerospace_material", "Aerospace-Grade Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "titanium").
classified(S, "ear", "aerospace_material", "Aerospace-Grade Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "aluminum").
classified(S, "ear", "aerospace_material", "Aerospace-Grade Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "fiber_composite").
classified(S, "ear", "aerospace_material", "Aerospace-Grade Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "ceramic").

classified(S, "ear", "nuclear_material", "Nuclear-Relevant Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "hafnium").
classified(S, "ear", "nuclear_material", "Nuclear-Relevant Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "beryllium").

classified(S, "ear", "rocket_nozzle_material", "Rocket Nozzle Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "tungsten").
classified(S, "ear", "rocket_nozzle_material", "Rocket Nozzle Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "rhenium").
classified(S, "ear", "rocket_nozzle_material", "Rocket Nozzle Material") :-
    substance(S),
    schedule(S, "ear_cat1", "controlled"),
    material_type(S, "carbide").

% Proliferation concerns
proliferation_concern(S, "missile_technology") :-
    classified(S, "ear", "rocket_nozzle_material", _).

proliferation_concern(S, "nuclear_program") :-
    classified(S, "ear", "nuclear_material", _).

proliferation_concern(S, "advanced_military_aircraft") :-
    classified(S, "ear", "aerospace_material", _).

proliferation_concern(S, "ballistic_missile_reentry_vehicle") :-
    classified(S, "ear", "ultra_high_temperature", _).

% Human review requirements
requires_human_review(S, "Category 1 material requires export license review") :-
    classified(S, "ear", "cat1_material", _).

requires_human_review(S, "Refractory metal requires missile technology assessment") :-
    classified(S, "ear", "rocket_nozzle_material", _).

requires_human_review(S, "Nuclear-relevant material requires proliferation review") :-
    classified(S, "ear", "nuclear_material", _).

requires_human_review(S, "Ultra-high temperature material requires military end-use review") :-
    classified(S, "ear", "ultra_high_temperature", _).
