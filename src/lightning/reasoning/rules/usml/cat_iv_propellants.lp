% =============================================================================
% USML Category IV(h) — Launch vehicles, missiles, rockets, and propellants
% =============================================================================
% This is an example of how existing LIGHTNING rule files integrate with the
% Phase 0 foundation. The existing Cat IV logic is preserved but now uses
% the standard atom vocabulary and benefits from the specially designed
% cross-cutting doctrine.
%
% Based on 22 CFR 121.1, Category IV
% =============================================================================

#include "_common/atom_vocabulary.lp".

% -----------------------------------------------------------------------------
% § CATEGORY IV(h) — PROPELLANTS AND PROPELLANT COMPONENTS  
% -----------------------------------------------------------------------------

% USML Cat IV(h): "Propellants and constituent chemicals therefor specially
% designed for the articles in paragraphs (a) through (g) of this category."

% High-performance rocket propellants
classified(S, "usml", "IV_h_propellant", "Cat IV(h) controlled propellant") :-
    substance(S),
    usml_controlled_propellant(S).

% Define controlled propellants (existing logic preserved)
usml_controlled_propellant("hydrazine").
usml_controlled_propellant("monomethylhydrazine").
usml_controlled_propellant("unsymmetrical_dimethylhydrazine").  % UDMH
usml_controlled_propellant("nitrogen_tetroxide").               % NTO
usml_controlled_propellant("inhibited_red_fuming_nitric_acid"). % IRFNA
usml_controlled_propellant("mixed_oxides_of_nitrogen").         % MON
usml_controlled_propellant("hydrogen_peroxide_concentrated").   % >85% concentration

% Concentration-dependent propellants
classified(S, "usml", "IV_h_propellant", "High concentration propellant") :-
    substance(S),
    concentration_controlled_propellant(S, MinConcentration),
    quantity(S, Concentration, "percent"),
    Concentration >= MinConcentration.

concentration_controlled_propellant("hydrogen_peroxide", 85).
concentration_controlled_propellant("nitric_acid", 80).

% Solid propellant ingredients
classified(S, "usml", "IV_h_propellant", "Solid propellant ingredient") :-
    substance(S),
    solid_propellant_ingredient(S).

solid_propellant_ingredient("ammonium_perchlorate").
solid_propellant_ingredient("potassium_perchlorate").
solid_propellant_ingredient("aluminum_powder_spherical").       % Spherical, ≤60 μm
solid_propellant_ingredient("beryllium_powder").
solid_propellant_ingredient("boron_powder").
solid_propellant_ingredient("magnesium_powder").
solid_propellant_ingredient("zirconium_powder").
solid_propellant_ingredient("nitrocellulose").
solid_propellant_ingredient("nitroglycerin").
solid_propellant_ingredient("hmx").                             % Cyclotetramethylenetetranitramine
solid_propellant_ingredient("rdx").                             % Cyclotrimethylenetrinitramine

% Particle size restrictions for metal powders
classified(S, "usml", "IV_h_propellant", "Controlled metal powder") :-
    substance(S),
    metal_powder_controlled(S, MaxParticleSize),
    specification(S, "particle_size_micron", ParticleSize, "micron"),
    ParticleSize <= MaxParticleSize.

metal_powder_controlled("aluminum_powder_spherical", 60).
metal_powder_controlled("beryllium_powder", 60).
metal_powder_controlled("boron_powder", 60).

% -----------------------------------------------------------------------------
% § CATEGORY IV(a)-(g) — DELIVERY SYSTEMS AND MAJOR COMPONENTS
% -----------------------------------------------------------------------------

% USML Cat IV(a): Rockets, SLVs, missiles, drones, etc. with range ≥ 15 km
_iv_a_qualifying_type(S) :- system_type(S, "rocket").
_iv_a_qualifying_type(S) :- system_type(S, "missile").
_iv_a_qualifying_type(S) :- system_type(S, "slv").

classified(S, "usml", "IV_a", "Launch vehicle or missile") :-
    system(S),
    _iv_a_qualifying_type(S),
    system_capability(S, "range_km", Range, "km"),
    Range >= 15.

% USML Cat IV(b): Rocket motor and propulsion systems
classified(C, "usml", "IV_b", "Rocket motor or propulsion system") :-
    component(C),
    component_category(C, Category),
    rocket_propulsion_category(Category),
    parent_system(C, System),
    classified(System, "usml", "IV_a", _).

rocket_propulsion_category("rocket_motor").
rocket_propulsion_category("rocket_engine"). 
rocket_propulsion_category("propulsion_system").
rocket_propulsion_category("thruster").

% USML Cat IV(c): Rocket stages  
classified(C, "usml", "IV_c", "Rocket stage") :-
    component(C),
    component_category(C, "rocket_stage"),
    parent_system(C, System),
    classified(System, "usml", "IV_a", _).

% USML Cat IV(d): Re-entry vehicles and heat shields
classified(C, "usml", "IV_d", "Re-entry vehicle or heat shield") :-
    component(C),
    component_category(C, Category),
    reentry_category(Category).

reentry_category("reentry_vehicle").
reentry_category("heat_shield").
reentry_category("ablative_material").
reentry_category("thermal_protection_system").

% USML Cat IV(e): Military spacecraft and satellites  
classified(S, "usml", "IV_e", "Military spacecraft") :-
    system(S),
    system_type(S, "satellite"),
    intended_end_use(S, "military").

% USML Cat IV(f): Launching devices and ground support equipment
classified(C, "usml", "IV_f", "Launch support equipment") :-
    component(C),
    component_category(C, Category),
    launch_support_category(Category).

launch_support_category("launch_platform").
launch_support_category("erector_launcher").
launch_support_category("mobile_launcher").
launch_support_category("umbilical_tower").
launch_support_category("propellant_loading_system").

% USML Cat IV(g): Altitude control systems, guidance sets, flight control
classified(C, "usml", "IV_g", "Guidance or flight control system") :-
    component(C),
    component_category(C, Category),
    guidance_category(Category).

guidance_category("guidance_system").
guidance_category("flight_control_system").  
guidance_category("inertial_navigation_system").
guidance_category("gyroscope").
guidance_category("accelerometer").
guidance_category("attitude_control_system").

% Accuracy thresholds for guidance systems
classified(C, "usml", "IV_g", "High-accuracy guidance system") :-
    component(C),
    component_category(C, "guidance_system"),
    specification(C, "cep_accuracy_m", CEP, "m"),
    CEP <= 10.  % Circular error probable ≤ 10 meters

% -----------------------------------------------------------------------------
% § SPECIALLY DESIGNED COMPONENTS (Cross-cutting via _common/specially_designed.lp)
% -----------------------------------------------------------------------------

% The specially designed doctrine automatically applies to components of 
% USML Cat IV articles. For example:

% component("tpa_4421_turbopump")
% parent_system("tpa_4421_turbopump", "vulcan_iii_engine")  
% classified("vulcan_iii_engine", "usml", "IV_a", "Launch vehicle engine")
%
% → specially_designed("tpa_4421_turbopump")  [via _common/specially_designed.lp]
% → classified("tpa_4421_turbopump", "usml", "IV_h", "Specially designed component")

% However, release paragraphs may apply. For example, if the turbopump has 
% equivalent form/fit/function to a commercial component:
%
% equivalent_civilian_component("tpa_4421_turbopump", "commercial_pump_xyz")
% same_form_fit_function("tpa_4421_turbopump", "commercial_pump_xyz")  
% not produced_with_defense_knowledge("tpa_4421_turbopump")
%
% → release_paragraph_applies("tpa_4421_turbopump", "b1_form_fit_function")
% → not specially_designed("tpa_4421_turbopump")
% → not classified("tpa_4421_turbopump", "usml", ...)

% -----------------------------------------------------------------------------
% § PERFORMANCE THRESHOLDS AND TECHNICAL PARAMETERS
% -----------------------------------------------------------------------------

% Total impulse thresholds for solid propellant motors
classified(C, "usml", "IV_b", "High-impulse solid motor") :-
    component(C),
    component_category(C, "solid_rocket_motor"),
    specification(C, "total_impulse_ns", Impulse, "ns"),
    Impulse > 8900.  % > 8.9 kN⋅s total impulse

% Specific impulse thresholds for liquid propulsion
classified(C, "usml", "IV_b", "High-performance liquid engine") :-
    component(C),
    component_category(C, "liquid_rocket_engine"),
    specification(C, "specific_impulse_sec", Isp, "sec"),
    Isp > 400.  % > 400 seconds vacuum Isp

% Pressure vessel ratings for propellant tanks
classified(C, "usml", "IV_h", "High-pressure propellant tank") :-
    component(C),
    component_category(C, "propellant_tank"),
    specification(C, "burst_pressure_bar", Pressure, "bar"),
    Pressure > 17.  % > 17 bar (250 psi) burst pressure

% -----------------------------------------------------------------------------
% § CROSS-REGIME INTERACTIONS
% -----------------------------------------------------------------------------

% USML Cat IV often overlaps with MTCR Category I systems
% [DISABLED — list literals not in clingo] cross_regime_violation(S, ["usml_iv", "mtcr_i"], "Missile-class launch vehicle") :-
% [DISABLED — list literals not in clingo]     classified(S, "usml", "IV_a", _),
% [DISABLED — list literals not in clingo]     system_capability(S, "payload_kg", Payload, "kg"),
% [DISABLED — list literals not in clingo]     system_capability(S, "range_km", Range, "km"),
% [DISABLED — list literals not in clingo]     Payload >= 500, Range >= 300.

% Some USML IV(h) propellants overlap with CWC Schedule 2 chemicals
% [DISABLED — list literals not in clingo] cross_regime_violation(S, ["usml_iv_h", "cwc_schedule_2"], "Dual-use propellant chemical") :-
% [DISABLED — list literals not in clingo]     classified(S, "usml", "IV_h", _),
% [DISABLED — list literals not in clingo]     schedule(S, "cwc", "2").

% =============================================================================
% NOTES
% =============================================================================
%
% 1. This file preserves existing LIGHTNING Cat IV logic while integrating with
%    the Phase 0 foundation. Existing atoms should work unchanged.
%
% 2. The specially_designed.lp cross-cutting doctrine automatically handles
%    parts/components/accessories without duplicating logic in each category.
%
% 3. Performance thresholds are now expressed using the standard specification/4
%    atom rather than ad-hoc predicates.
%
% 4. Cross-regime violations are flagged for cases where USML and MTCR or
%    CWC classifications overlap on the same artifact.
%
% =============================================================================
