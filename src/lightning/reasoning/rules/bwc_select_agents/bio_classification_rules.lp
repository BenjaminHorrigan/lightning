% =============================================================================
% Biological Agent Classification Rules
% Source: 42 CFR 73 (HHS/CDC), 7 CFR 331 (USDA), Australia Group Guidelines
% =============================================================================
% HHS and USDA select agent classifications are handled by select_agents.lp
% (3-arg classified atoms with authoritative labels SELECT_AGENT_HHS/USDA).
% This file only adds Australia Group and BSL classifications that do not
% conflict with select_agents.lp.

% Australia Group biological agents (not covered by select_agents.lp)
classified(S, "bwc_select_agents", "australia_group_bio", "Australia Group Biological Agent") :-
    substance(S),
    schedule(S, "australia_group", "biological"),
    not schedule(S, "hhs_select", "agent"),
    not schedule(S, "usda_select", "agent").

% Biosafety level classifications
classified(S, "bwc_select_agents", "bsl_4_pathogen", "BSL-4 Pathogen - Maximum Containment Required") :-
    substance(S),
    biosafety_level(S, "4").

classified(S, "bwc_select_agents", "bsl_3_pathogen", "BSL-3 Pathogen - High Containment Required") :-
    substance(S),
    biosafety_level(S, "3").

% Proliferation concerns
proliferation_concern(S, "select_agent_diversion") :-
    classified(S, "SELECT_AGENT_HHS", _).

proliferation_concern(S, "select_agent_diversion") :-
    classified(S, "SELECT_AGENT_USDA", _).

proliferation_concern(S, "biological_weapons_precursor") :-
    classified(S, "bwc_select_agents", "bsl_4_pathogen", _).

% Human review requirements
requires_human_review(S, "BSL-4 pathogen requires maximum containment verification") :-
    classified(S, "bwc_select_agents", "bsl_4_pathogen", _).

requires_human_review(S, "Australia Group biological agent requires end-use review") :-
    classified(S, "bwc_select_agents", "australia_group_bio", _).
