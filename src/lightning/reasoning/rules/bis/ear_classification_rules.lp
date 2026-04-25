% =============================================================================
% Export Administration Regulations (EAR) Classification Rules
% Source: 15 CFR 730-774 (Bureau of Industry and Security)
% =============================================================================
% Classifies items under EAR export controls, Entity List restrictions, and
% AI/compute controls under ECCN 3A001, 4A001, and 5D002

% Entity List classifications — predicates match bis_entity_list_generated.lp
classified(S, "ear", "entity_list_restriction", "BIS Entity List - license required") :-
    restricted_entity(S),
    entity_regime(S, "bis_entity_list").

% Entity List country-based classifications
classified(S, "ear", "china_entity", "Chinese Entity List Organization") :-
    restricted_entity(S),
    entity_regime(S, "bis_entity_list"),
    entity_country(S, "CHINA").

classified(S, "ear", "russia_entity", "Russian Entity List Organization") :-
    restricted_entity(S),
    entity_regime(S, "bis_entity_list"),
    entity_country(S, "RUSSIA").

% AI-relevant entity restrictions
classified(S, "ear", "ai_entity_restriction", "AI-Relevant Entity List Restriction") :-
    restricted_entity(S),
    entity_regime(S, "bis_entity_list"),
    entity_ai_relevant(S, "yes").

% AI/Compute export control classifications — predicates match bis_ai_compute_generated.lp
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

classified(S, "ear", "eccn_3b001", "ECCN 3B001 - Semiconductor Manufacturing Equipment") :-
    substance(S),
    eccn_code(S, "3B001").

classified(S, "ear", "eccn_4a001", "ECCN 4A001 - Computer Systems") :-
    substance(S),
    eccn_code(S, "4A001").

classified(S, "ear", "eccn_4a003", "ECCN 4A003 - Networking Equipment") :-
    substance(S),
    eccn_code(S, "4A003").

classified(S, "ear", "eccn_5d002", "ECCN 5D002 - Information Security Software") :-
    substance(S),
    eccn_code(S, "5D002").

% High-performance computing thresholds
classified(S, "ear", "high_performance_ai", "High Performance AI System") :-
    substance(S),
    schedule(S, "bis_ai_compute", "controlled"),
    performance_threshold(S, "100_TOPS").
classified(S, "ear", "high_performance_ai", "High Performance AI System") :-
    substance(S),
    schedule(S, "bis_ai_compute", "controlled"),
    performance_threshold(S, "1_exaflop").
classified(S, "ear", "high_performance_ai", "High Performance AI System") :-
    substance(S),
    schedule(S, "bis_ai_compute", "controlled"),
    performance_threshold(S, "100_petaflops").

classified(S, "ear", "quantum_technology", "Quantum Computing Technology") :-
    substance(S),
    performance_threshold(S, "50_qubits").
classified(S, "ear", "quantum_technology", "Quantum Computing Technology") :-
    substance(S),
    performance_threshold(S, "20_qubits").

classified(S, "ear", "semiconductor_equipment", "Controlled Semiconductor Equipment") :-
    substance(S),
    eccn_code(S, "3B001").

% Proliferation concerns
proliferation_concern(S, "dual_use_ai_technology") :-
    classified(S, "ear", "high_performance_ai", _).

proliferation_concern(S, "quantum_advantage_risk") :-
    classified(S, "ear", "quantum_technology", _).

proliferation_concern(S, "entity_list_diversion") :-
    classified(S, "ear", "ai_entity_restriction", _).

proliferation_concern(S, "advanced_chip_manufacturing_transfer") :-
    classified(S, "ear", "semiconductor_equipment", _).

% Human review requirements
requires_human_review(S, "Entity List transaction requires BIS license") :-
    classified(S, "ear", "entity_list_restriction", _).

requires_human_review(S, "High-performance AI technology requires export license review") :-
    classified(S, "ear", "high_performance_ai", _).

requires_human_review(S, "Quantum technology requires national security review") :-
    classified(S, "ear", "quantum_technology", _).

requires_human_review(S, "AI Entity List organization requires enhanced due diligence") :-
    classified(S, "ear", "ai_entity_restriction", _).

requires_human_review(S, "Semiconductor equipment requires export license under EAR 3B001") :-
    classified(S, "ear", "semiconductor_equipment", _).