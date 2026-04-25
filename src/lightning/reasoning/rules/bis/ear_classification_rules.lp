% =============================================================================
% Export Administration Regulations (EAR) Classification Rules
% Source: 15 CFR 730-774 (Bureau of Industry and Security)
% =============================================================================
% Classifies items under EAR export controls, Entity List restrictions, and
% AI/compute controls under ECCN 3A001, 4A001, and 5D002

% Entity List classifications
classified(S, "ear", "entity_list_restriction", "BIS Entity List - license required") :-
    entity(S),
    schedule(S, "bis_entity_list", "restricted").

% AI/Compute export control classifications
classified(S, "ear", "ai_compute_controlled", "AI/Compute Export Control Item") :-
    substance(S),
    schedule(S, "bis_ai_compute", "controlled").

classified(S, "ear", "ai_compute_license_required", "AI/Compute License Required") :-
    substance(S),
    schedule(S, "bis_ai_compute", "controlled"),
    control_level(S, "license_required").

% ECCN-specific classifications
classified(S, "ear", "eccn_3a001", "ECCN 3A001 - Electronic Equipment/Components") :-
    substance(S),
    eccn_code(S, "3A001").

classified(S, "ear", "eccn_4a001", "ECCN 4A001 - Computer Systems") :-
    substance(S),
    eccn_code(S, "4A001").

classified(S, "ear", "eccn_5d002", "ECCN 5D002 - Software") :-
    substance(S),
    eccn_code(S, "5D002").

% High-performance computing thresholds
classified(S, "ear", "high_performance_ai", "High Performance AI System") :-
    substance(S),
    schedule(S, "bis_ai_compute", "controlled"),
    performance_threshold(S, Threshold),
    (Threshold = "100_TOPS"; Threshold = "1_exaflop"; Threshold = "100_petaflops").

classified(S, "ear", "quantum_technology", "Quantum Computing Technology") :-
    substance(S),
    (performance_threshold(S, "50_qubits"); performance_threshold(S, "20_qubits")).

% Entity List country-based classifications
classified(S, "ear", "china_entity", "Chinese Entity List Organization") :-
    entity(S),
    schedule(S, "bis_entity_list", "restricted"),
    country(S, "China").

classified(S, "ear", "russia_entity", "Russian Entity List Organization") :-
    entity(S),
    schedule(S, "bis_entity_list", "restricted"),
    country(S, "Russia").

% AI-relevant entity restrictions
classified(S, "ear", "ai_entity_restriction", "AI-Relevant Entity List Restriction") :-
    entity(S),
    schedule(S, "bis_entity_list", "restricted"),
    ai_compute_relevant(S, "yes").

% Proliferation concerns
proliferation_concern(S, "dual_use_ai_technology") :-
    classified(S, "ear", "high_performance_ai", _).

proliferation_concern(S, "quantum_advantage_risk") :-
    classified(S, "ear", "quantum_technology", _).

proliferation_concern(S, "entity_list_diversion") :-
    classified(S, "ear", "ai_entity_restriction", _).

% Human review requirements
requires_human_review(S, "Entity List transaction requires BIS license") :-
    classified(S, "ear", "entity_list_restriction", _).

requires_human_review(S, "High-performance AI technology requires export license review") :-
    classified(S, "ear", "high_performance_ai", _).

requires_human_review(S, "Quantum technology requires national security review") :-
    classified(S, "ear", "quantum_technology", _).

requires_human_review(S, "AI Entity List organization requires enhanced due diligence") :-
    classified(S, "ear", "ai_entity_restriction", _).