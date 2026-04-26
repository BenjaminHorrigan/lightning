% =============================================================================
% USML Category VIII — Military Aircraft, Spacecraft, and Related Articles
% Source: 22 CFR 121.1 Category VIII (ITAR)
% =============================================================================
% Depth: production-ready for military aircraft, engines, and key subsystems.
% Release paragraph: commercial-derivative aircraft not specially designed
% for military use are outside USML (note 2 to Category VIII).
% =============================================================================

% ----------------------------------------------------------------------------
% VIII(a) — Aircraft specifically designed for military purposes
% ----------------------------------------------------------------------------
category_viii_a("combat_aircraft").
category_viii_a("attack_helicopter").
category_viii_a("military_trainer").        % armed or weapons-systems-capable
category_viii_a("armed_uav").
category_viii_a("military_transport_aircraft").
category_viii_a("electronic_warfare_aircraft").
category_viii_a("airborne_warning_aircraft").  % AWACS, JSTARS
category_viii_a("military_patrol_aircraft").
category_viii_a("gunship").

classified(C, "USML_VIII_a", "22 CFR 121.1 Category VIII(a)") :-
    component(C),
    component_category(C, Cat),
    category_viii_a(Cat),
    not released_from_control(C).

% VIII(a)(3) — performance threshold: aircraft with speed > 300 kts
% capable of weapons delivery
classified(C, "USML_VIII_a_performance", "22 CFR 121.1 Category VIII(a)") :-
    component(C),
    performance(C, "speed_knots", Speed),
    Speed > 300,
    attribute(C, "weapons_hardpoints"),
    not released_from_control(C).

% VIII(a) — armed UAV with range triggering MTCR concern
classified(C, "USML_VIII_a_uav_range", "22 CFR 121.1 Category VIII(a)") :-
    system(C),
    system_type(C, "armed_uav"),
    performance(C, "range_km", Range),
    Range >= 300,
    not released_from_control(C).

% MTCR bridge — armed UAVs with range >= 300 km are also MTCR Cat I
mtcr_controlled(C) :-
    classified(C, "USML_VIII_a_uav_range", _).

% ----------------------------------------------------------------------------
% VIII(b) — Jet engines specially designed for military aircraft
% ----------------------------------------------------------------------------
category_viii_b_engine("military_turbofan").
category_viii_b_engine("military_turbojet").
category_viii_b_engine("military_turboshaft").  % attack helicopter engines
category_viii_b_engine("military_turboprop").
category_viii_b_engine("afterburning_turbofan").

classified(C, "USML_VIII_b", "22 CFR 121.1 Category VIII(b)") :-
    component(C),
    component_category(C, Cat),
    category_viii_b_engine(Cat),
    not released_from_control(C).

% Engine with parent military aircraft — specially designed catches engines
% not named above but integral to a military aircraft system
classified(C, "USML_VIII_b", "22 CFR 121.1 Category VIII(b)") :-
    component(C),
    component_category(C, "turbofan_engine"),
    parent_system(C, System),
    classified(System, "USML_VIII_a", _),
    not released_from_control(C).
classified(C, "USML_VIII_b", "22 CFR 121.1 Category VIII(b)") :-
    component(C),
    component_category(C, "turbofan_engine"),
    parent_system(C, System),
    classified(System, "USML_VIII_a_performance", _),
    not released_from_control(C).

% ----------------------------------------------------------------------------
% VIII(c) — Parts and components specially designed for Cat VIII articles
% ----------------------------------------------------------------------------
category_viii_c("ejection_seat").
category_viii_c("aircraft_gun_system").    % M61 Vulcan mount, etc.
category_viii_c("military_avionics").      % fire control, EW suite
category_viii_c("stealth_coating").        % RAM, low-observable coatings
category_viii_c("combat_aircraft_landing_gear").
category_viii_c("missile_pylon").
category_viii_c("weapons_bay_door").
category_viii_c("aerial_refueling_boom").  % military MRTT/tanker specific
category_viii_c("radar_absorbent_structure").
category_viii_c("military_flight_control_computer").

classified(C, "USML_VIII_c", "22 CFR 121.1 Category VIII(c)") :-
    component(C),
    component_category(C, Cat),
    category_viii_c(Cat),
    not released_from_control(C).

% Specially-designed catch-all for components of VIII(a) aircraft
classified(C, "USML_VIII_c", "22 CFR 121.1 Category VIII(c)") :-
    component(C),
    specially_designed(C),
    parent_system(C, System),
    classified(System, "USML_VIII_a", _),
    not released_from_control(C).
classified(C, "USML_VIII_c", "22 CFR 121.1 Category VIII(c)") :-
    component(C),
    specially_designed(C),
    parent_system(C, System),
    classified(System, "USML_VIII_a_performance", _),
    not released_from_control(C).

% ----------------------------------------------------------------------------
% Release paragraphs
% ----------------------------------------------------------------------------
% Note 2 to Category VIII: Commercial derivative aircraft not modified or
% configured for military use are not USML-controlled (they may be EAR).
released_from_control(C) :-
    attribute(C, "commercial_derivative_not_specially_designed").

% Component commercially available and not specially designed for military
released_from_control(C) :-
    attribute(C, "commercial_aircraft_part"),
    not attribute(C, "weapons_hardpoints"),
    not parent_system(C, _).

% ----------------------------------------------------------------------------
% Cross-regime: VIII(a) combat aircraft overlap with MTCR armed UAV category
% ----------------------------------------------------------------------------
mtcr_controlled(C) :-
    classified(C, "USML_VIII_a", _),
    component_category(C, "armed_uav").

#show classified/3.
#show specially_designed/1.
