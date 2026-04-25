% ============================================================================
% MTCR — Missile Technology Control Regime
% Source: MTCR Equipment, Software and Technology Annex
% ============================================================================
% Five-section layout per aegis_RULE_EXPANSION.md Phase C template:
%   1. Taxonomy facts     — known component categories
%   2. Threshold rules    — numerical cutoffs (Category I)
%   3. Inheritance rules  — specially_designed parts → Category II
%   4. Exclusion rules    — (MTCR has no release paragraphs at this layer)
%   5. Classification output rules
%
% Threshold facts (range_km, payload_kg) must be emitted as performance/3
% on a system atom. The engine propagates component specifications to the
% parent system so these rules fire on standalone-system submissions too
% (see reasoning/engine.py B.2 performance-propagation logic).

% ----------------------------------------------------------------------------
% Section 1 — Taxonomy
% ----------------------------------------------------------------------------
category_ii_component("rocket_engine").
category_ii_component("rocket_motor").
category_ii_component("composite_motor_case").
category_ii_component("re_entry_vehicle").
category_ii_component("guidance_equipment").
category_ii_component("thrust_vector_control_mtcr").
category_ii_component("propellant_production_equipment").

% ----------------------------------------------------------------------------
% Section 2 — Thresholds: Category I complete systems
% ----------------------------------------------------------------------------
% A complete system with payload >= 500 kg AND range >= 300 km is MTCR Cat I.
classified(System, "MTCR_Category_I", "MTCR Annex Category I") :-
    system(System),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P >= 500, R >= 300.

% UAV variant — same thresholds; separate classification code for display.
classified(System, "MTCR_Category_I_UAV", "MTCR Annex Category I (UAVs)") :-
    system(System),
    system_type(System, "uav"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P >= 500, R >= 300.

% ----------------------------------------------------------------------------
% Section 3 — Inheritance: Category II components
% ----------------------------------------------------------------------------
% specially_designed/1 is defined in usml_cat_iv.lp and shared across the
% single clingo program — so MTCR Cat II inheritance piggybacks on the same
% 22 CFR 120.41(b) logic.
classified(Component, "MTCR_Category_II", "MTCR Annex Category II") :-
    component(Component),
    component_category(Component, Cat),
    category_ii_component(Cat),
    specially_designed(Component).

% ----------------------------------------------------------------------------
% Sub-threshold systems capable of WMD delivery
% ----------------------------------------------------------------------------
% MTCR Annex Cat II treats sub-threshold rockets/missiles/UAVs (300-499 kg
% payload, range >= 300 km) as presumptive controlled.
% Implemented as three separate rules because clingo ASP does not support
% Prolog-style in-body disjunction.
classified(System, "MTCR_Category_II_sub_threshold",
           "MTCR Annex Category II (sub-threshold)") :-
    system(System),
    system_type(System, "rocket"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P < 500, R >= 300, P >= 300.

classified(System, "MTCR_Category_II_sub_threshold",
           "MTCR Annex Category II (sub-threshold)") :-
    system(System),
    system_type(System, "ballistic_missile"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P < 500, R >= 300, P >= 300.

classified(System, "MTCR_Category_II_sub_threshold",
           "MTCR Annex Category II (sub-threshold)") :-
    system(System),
    system_type(System, "cruise_missile"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P < 500, R >= 300, P >= 300.

classified(System, "MTCR_Category_II_sub_threshold",
           "MTCR Annex Category II (sub-threshold)") :-
    system(System),
    system_type(System, "uav"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P < 500, R >= 300, P >= 300.

#show classified/3.
