% ============================================================================
% USML Category IV — Launch Vehicles, Missiles, Rockets, Torpedoes, Bombs, Mines
% Source: 22 CFR 121.1, Category IV
% ============================================================================
%
% Encoding strategy:
% - Facts (`substance/1`, `component/1`, `parent_system/2`, etc.) are asserted
%   by the extraction layer from the TechnicalArtifact.
% - Rules below define when facts map to USML classifications.
% - The "specially designed" logic from 22 CFR 120.41 is the hardest and most
%   important piece — it's what makes USML reasoning non-trivial and what
%   most LLM baselines get wrong.
% - Every classification produces a classified/3 atom carrying the citation
%   key, which the Python layer converts to a RegulationCitation.
%
% This is v1 — encodes the rocket-relevant portions of Category IV only.
% Extension to Categories V, VIII, XV follows the same pattern.

% ============================================================================
% Category IV subcategory facts (from 22 CFR 121.1)
% ============================================================================

% IV(a) — complete rockets, SLVs, missiles
category_iv_a("rocket").
category_iv_a("space_launch_vehicle").
category_iv_a("ballistic_missile").
category_iv_a("cruise_missile").
category_iv_a("sounding_rocket").

% IV(d) — rocket, missile, and bomb components (enumerated)
category_iv_d_component("warhead").
category_iv_d_component("reentry_vehicle").
category_iv_d_component("guidance_set").
category_iv_d_component("thrust_vector_control").
category_iv_d_component("safing_arming_fuzing").

% IV(h) — parts, components, accessories, attachments, and associated equipment
% This is the *inheritance* category — the one that matters for hackathon demos.
% A component falls under IV(h) if it is "specially designed" for a Category IV item.

category_iv_h_component("turbopump").
category_iv_h_component("combustion_chamber").
category_iv_h_component("injector").
category_iv_h_component("nozzle").
category_iv_h_component("rocket_engine").
category_iv_h_component("solid_rocket_motor").
category_iv_h_component("liquid_rocket_engine").
category_iv_h_component("propellant_tank_specialized").
category_iv_h_component("thrust_chamber").
category_iv_h_component("gimbal_actuator").
category_iv_h_component("staging_mechanism").
% A.5 expansion — missile-structure and guidance parts
category_iv_h_component("rocket_motor_case").
category_iv_h_component("flange_motor_case").
category_iv_h_component("flange_seal_motor_case").
category_iv_h_component("end_dome_motor_case").
category_iv_h_component("inertial_measurement_unit").
category_iv_h_component("thrust_chamber_regen_cooled").
category_iv_h_component("ablative_liner").
category_iv_h_component("reentry_vehicle_heat_shield").
category_iv_h_component("penetration_aid").
category_iv_h_component("decoy_reentry").
category_iv_h_component("submunition_dispenser").

% ============================================================================
% "Specially designed" — 22 CFR 120.41
% ============================================================================
%
% A part/component is "specially designed" if:
%   (a) As a result of development, it has properties peculiarly responsible for
%       achieving or exceeding the controlled performance levels, characteristics,
%       or functions of a USML-controlled end item; OR
%   (b) It is a part/component/accessory/attachment/associated equipment of a
%       USML-controlled end item (the "catch-all" inheritance rule).
%
% EXCEPTIONS (the "release" paragraphs of 120.41(b)(1)-(5)):
%   (1) Has the same function, performance capabilities, and the same or
%       "equivalent" form and fit as a commodity used in or with a non-USML
%       commodity;
%   (2) Was developed with knowledge of use in both USML and non-USML items;
%   (3) Was developed as a general-purpose commodity;
%   (4) Was developed with knowledge of only non-USML use;
%   (5) Has been identified in a commodity jurisdiction determination as not
%       USML-controlled.
%
% We encode (a) and (b) as the positive rule and (1)-(5) as defeaters.
% ============================================================================

% Core inference: a component inherits USML control from its parent system.
specially_designed(Component) :-
    component(Component),
    parent_system(Component, System),
    usml_controlled_end_item(System),
    not released_from_control(Component).

% Alternative positive basis: performance peculiarly responsible
specially_designed(Component) :-
    component(Component),
    performance_peculiar_to_controlled_function(Component),
    not released_from_control(Component).

% The 120.41(b) release paragraphs — any one of these defeats "specially designed"
released_from_control(Component) :-
    equivalent_form_fit_function(Component, CommercialItem),
    commercial_widely_available(CommercialItem).

released_from_control(Component) :-
    general_purpose_development(Component).

released_from_control(Component) :-
    commodity_jurisdiction_determination(Component, "not_controlled").

% ============================================================================
% USML-controlled end items (what the above inherits from)
% ============================================================================

usml_controlled_end_item(System) :-
    system(System),
    system_type(System, Type),
    category_iv_a(Type).

usml_controlled_end_item(System) :-
    system(System),
    system_type(System, Type),
    category_iv_d_component(Type).

% ============================================================================
% Final classification rules
% ============================================================================

% Direct Category IV(a) hit — the item itself is a controlled end item
classified(Component, "USML_IV_a", "22 CFR 121.1 Category IV(a)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_a(Cat).

% Direct Category IV(d) hit — enumerated major component
classified(Component, "USML_IV_d", "22 CFR 121.1 Category IV(d)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_d_component(Cat).

% Category IV(h) via inheritance — the interesting case
classified(Component, "USML_IV_h", "22 CFR 121.1 Category IV(h); 22 CFR 120.41") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_h_component(Cat),
    specially_designed(Component).

% Substance-level classification (propellants under IV(h))
classified(Substance, "USML_IV_h_propellant", "22 CFR 121.1 Category IV(h)(1)") :-
    substance(Substance),
    controlled_propellant(Substance).

controlled_propellant("hydrazine").
controlled_propellant("monomethylhydrazine").
controlled_propellant("unsymmetrical_dimethylhydrazine").
controlled_propellant("nitrogen_tetroxide").
controlled_propellant("inhibited_red_fuming_nitric_acid").
% A.9 expansion — solid propellants, energetic binders, and plasticizers
controlled_propellant("nitromethane").
controlled_propellant("ammonium_perchlorate").
controlled_propellant("hmx").
controlled_propellant("rdx").
controlled_propellant("cl_20").
controlled_propellant("gap").
controlled_propellant("htpb_bound_propellant").

% ============================================================================
% A.1 — Paragraph (b): launch vehicle sub-articles
% ============================================================================
category_iv_b("solid_rocket_motor").
category_iv_b("liquid_rocket_engine").
category_iv_b("hybrid_rocket_motor").
category_iv_b("ramjet").
category_iv_b("scramjet").
category_iv_b("stage").
category_iv_b("interstage").
category_iv_b("payload_fairing").

classified(Component, "USML_IV_b", "22 CFR 121.1 Category IV(b)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_b(Cat).

% ============================================================================
% A.2 — Paragraph (c): launch-support equipment with NFPA 1122 release
% ============================================================================
category_iv_c("transporter_erector_launcher").
category_iv_c("launch_stand").
category_iv_c("umbilical_tower").
category_iv_c("launch_control_system").
category_iv_c("propellant_loading_equipment").

% 22 CFR 121.1 Category IV(c) note 1: consumer hobby launch items meeting
% NFPA 1122 are not USML-controlled. Encoded as a release predicate so the
% defeater surfaces in the proof tree alongside other 120.41(b) releases.
released_from_control(Component) :-
    component(Component),
    attribute(Component, "hobby_rocket_nfpa_1122").

classified(Component, "USML_IV_c", "22 CFR 121.1 Category IV(c)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_c(Cat),
    not released_from_control(Component).

% ============================================================================
% A.3 — Paragraph (f): test and production equipment
% ============================================================================
category_iv_f_production("filament_winding_machine").
category_iv_f_production("isostatic_press_rocket").
category_iv_f_production("rocket_motor_test_stand").
category_iv_f_production("engine_test_cell").
category_iv_f_production("propellant_mixer_industrial").
category_iv_f_production("nozzle_forming_equipment").
category_iv_f_production("vacuum_chamber_spacecraft_testing").

classified(Component, "USML_IV_f", "22 CFR 121.1 Category IV(f)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_f_production(Cat),
    specially_designed(Component).

% Inherited control: generic "test_equipment" whose parent is a Category IV
% end item. Handles the case where the extractor identifies equipment as
% test/support without naming a specific production-equipment taxon.
classified(Component, "USML_IV_f", "22 CFR 121.1 Category IV(f)") :-
    component(Component),
    component_category(Component, "test_equipment"),
    parent_system(Component, System),
    usml_controlled_end_item(System).

% ============================================================================
% A.4 — Paragraph (g): DoD-funded developmental articles
% ============================================================================
classified(Component, "USML_IV_g", "22 CFR 121.1 Category IV(g)") :-
    component(Component),
    attribute(Component, "dod_funded_development").

% ============================================================================
% A.6 — MTCR cross-marking bridge
% ============================================================================
% Cross-regime marking: when a USML-classified article also appears on the
% MTCR Annex taxonomy, record mtcr_controlled/1 so the MTCR KB module (and
% downstream proof display) can surface it as dual-flagged.
mtcr_marked("rocket").
mtcr_marked("space_launch_vehicle").
mtcr_marked("ballistic_missile").
mtcr_marked("cruise_missile").
mtcr_marked("rocket_motor_case").
mtcr_marked("solid_rocket_motor").
mtcr_marked("liquid_rocket_engine").

mtcr_controlled(Component) :-
    classified(Component, _, _),
    component_category(Component, Cat),
    mtcr_marked(Cat).

% ============================================================================
% A.7 — Paragraph (a)(2): numerical threshold for complete systems
% ============================================================================
% A complete system with payload >= 500 kg and range >= 300 km is captured
% by the MTCR-aligned numerical threshold embedded in Category IV(a). This
% is the rule that requires performance/3 facts on systems (see engine.py
% parent-system performance propagation).
classified(System, "USML_IV_a_2", "22 CFR 121.1 Category IV(a)(2)") :-
    system(System),
    performance(System, "payload_kg", Payload),
    performance(System, "range_km", Range),
    Payload >= 500,
    Range >= 300.

% ============================================================================
% A.8 — Additional 120.41(b) release paragraphs
% ============================================================================
% 120.41(b)(2) — developed with knowledge of both USML and non-USML use,
% AND commercially available equivalent. Both conditions must hold.
released_from_control(Component) :-
    attribute(Component, "developed_for_both_usml_and_non_usml"),
    attribute(Component, "general_commercial_availability").

% 120.41(b)(4) — developed with knowledge of only non-USML use, when no
% controlled parent system is established (otherwise the catch-all (b)
% inheritance still applies).
released_from_control(Component) :-
    attribute(Component, "developed_only_non_usml"),
    not parent_system(Component, _).

% ============================================================================
% Output predicates — what the Python layer reads back
% ============================================================================

% Controlled element summary
controlled_element(X) :- classified(X, _, _).

% Export: proof-relevant atoms
#show classified/3.
#show specially_designed/1.
#show released_from_control/1.
#show controlled_element/1.
#show mtcr_controlled/1.
