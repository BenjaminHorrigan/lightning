% =============================================================================
% USML Category XV — Spacecraft Systems and Related Articles
% Source: 22 CFR 121.1 Category XV (ITAR)
% =============================================================================
% Depth: military/intelligence satellite systems, ground control, propulsion.
%
% EAR/ITAR boundary: Commercial remote-sensing satellites with ground-sampling
% distance >= 50 cm (500 mm) may be licensed under EAR (15 CFR 774 ECCN
% 9A515) rather than USML — this boundary is encoded as a release predicate.
% Satellites carrying classified payloads or built for intelligence missions
% remain USML regardless of resolution.
% =============================================================================

% ----------------------------------------------------------------------------
% XV(a) — Spacecraft designed for military or intelligence operations
% ----------------------------------------------------------------------------
military_spacecraft_type("military_satellite").
military_spacecraft_type("reconnaissance_satellite").
military_spacecraft_type("signals_intelligence_satellite").  % SIGINT
military_spacecraft_type("communications_satellite_military").  % MILSATCOM
military_spacecraft_type("early_warning_satellite").  % missile warning
military_spacecraft_type("navigation_satellite_military").  % GPS III class
military_spacecraft_type("geosynchronous_military_satellite").
military_spacecraft_type("electronic_intelligence_satellite").  % ELINT

classified(S, "USML_XV_a", "22 CFR 121.1 Category XV(a)") :-
    system(S),
    system_type(S, T),
    military_spacecraft_type(T),
    not released_from_control(S).

% XV(a) — military end-use declaration on any satellite type
classified(S, "USML_XV_a", "22 CFR 121.1 Category XV(a)") :-
    system(S),
    system_type(S, "satellite"),
    intended_end_use(S, "military"),
    not released_from_control(S).

classified(S, "USML_XV_a", "22 CFR 121.1 Category XV(a)") :-
    system(S),
    system_type(S, "spacecraft"),
    intended_end_use(S, "military"),
    not released_from_control(S).

% XV(a) — imaging threshold: sub-50cm ground-sampling distance (GSD) = military grade
% 50 cm is the current bright-line boundary where USML controls apply.
classified(S, "USML_XV_a_imaging", "22 CFR 121.1 Category XV(a)") :-
    system(S),
    system_type(S, "remote_sensing_satellite"),
    performance(S, "imaging_resolution_cm", Res),
    Res < 50,
    not released_from_control(S).

% Also capture imaging resolution expressed as ground_resolution_m < 0.5 m
classified(S, "USML_XV_a_imaging", "22 CFR 121.1 Category XV(a)") :-
    system(S),
    performance(S, "ground_resolution_m", Res),
    Res < 1,
    not released_from_control(S).

% ----------------------------------------------------------------------------
% XV(b) — Ground systems specifically for military satellites
% ----------------------------------------------------------------------------
classified(C, "USML_XV_b", "22 CFR 121.1 Category XV(b)") :-
    component(C),
    component_category(C, "satellite_command_and_control"),
    parent_system(C, System),
    classified(System, "USML_XV_a", _),
    not released_from_control(C).

classified(C, "USML_XV_b", "22 CFR 121.1 Category XV(b)") :-
    component(C),
    component_category(C, "satellite_command_and_control"),
    parent_system(C, System),
    classified(System, "USML_XV_a_imaging", _),
    not released_from_control(C).

classified(C, "USML_XV_b", "22 CFR 121.1 Category XV(b)") :-
    component(C),
    component_category(C, "military_ground_station"),
    not released_from_control(C).

% ----------------------------------------------------------------------------
% XV(c) — Propulsion systems for XV(a) spacecraft
% ----------------------------------------------------------------------------
spacecraft_propulsion_category("spacecraft_propulsion").
spacecraft_propulsion_category("satellite_thruster").
spacecraft_propulsion_category("orbit_raising_motor").
spacecraft_propulsion_category("apogee_kick_motor").
spacecraft_propulsion_category("attitude_control_thruster").

classified(C, "USML_XV_c", "22 CFR 121.1 Category XV(c)") :-
    component(C),
    component_category(C, Cat),
    spacecraft_propulsion_category(Cat),
    parent_system(C, System),
    classified(System, "USML_XV_a", _),
    not released_from_control(C).

classified(C, "USML_XV_c", "22 CFR 121.1 Category XV(c)") :-
    component(C),
    component_category(C, Cat),
    spacecraft_propulsion_category(Cat),
    parent_system(C, System),
    classified(System, "USML_XV_a_imaging", _),
    not released_from_control(C).

% ----------------------------------------------------------------------------
% EAR/ITAR boundary release: commercial remote-sensing above 50 cm threshold
% ----------------------------------------------------------------------------
% Commercial satellites with GSD >= 50 cm and no military end-use are EAR
% (ECCN 9A515), not USML. Note: ITAR still applies if satellite carries
% classified payload or is for intelligence collection regardless of GSD.
released_from_control(S) :-
    system(S),
    performance(S, "imaging_resolution_cm", Res),
    Res >= 50,
    not intended_end_use(S, "military"),
    not attribute(S, "classified_payload").

% Commercial communication satellites (non-military, non-classified) may
% qualify for EAR under ECCN 9A515 if not specially designed for military
released_from_control(S) :-
    system(S),
    system_type(S, "commercial_communication_satellite"),
    not intended_end_use(S, "military"),
    not attribute(S, "classified_payload").

#show classified/3.
