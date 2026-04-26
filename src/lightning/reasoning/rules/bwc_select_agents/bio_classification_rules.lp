% =============================================================================
% Biological Agent Classification Rules
% Source: 42 CFR 73 (HHS/CDC), 7 CFR 331 (USDA), Australia Group Guidelines
% =============================================================================
% Classifies biological agents, toxins, and select agents under BWC controls

% Core biological agent classification
classified(S, "bwc_select_agents", "hhs_select_agent", "HHS/CDC Select Agent (42 CFR 73)") :-
    substance(S),
    schedule(S, "hhs_select", "agent").

classified(S, "bwc_select_agents", "usda_select_agent", "USDA Select Agent (7 CFR 331)") :-
    substance(S),
    schedule(S, "usda_select", "agent").

classified(S, "bwc_select_agents", "australia_group_bio", "Australia Group Biological Agent") :-
    substance(S),
    schedule(S, "australia_group", "biological").

% Tier 1 select agents (highest security level)
classified(S, "bwc_select_agents", "tier_1_select_agent", "Tier 1 Select Agent - Enhanced Security Required") :-
    substance(S),
    schedule(S, "hhs_select", "agent"),
    tier_1(S, "yes").

classified(S, "bwc_select_agents", "tier_1_select_agent", "Tier 1 Select Agent - Enhanced Security Required") :-
    substance(S),
    schedule(S, "usda_select", "agent"),
    tier_1(S, "yes").

% Biosafety level classifications
classified(S, "bwc_select_agents", "bsl_4_pathogen", "BSL-4 Pathogen - Maximum Containment Required") :-
    substance(S),
    biosafety_level(S, "4").

classified(S, "bwc_select_agents", "bsl_3_pathogen", "BSL-3 Pathogen - High Containment Required") :-
    substance(S),
    biosafety_level(S, "3").

% Pathogen type classifications
classified(S, "bwc_select_agents", "bacterial_pathogen", "Bacterial Select Agent") :-
    substance(S), pathogen_type(S, "bacterium"), schedule(S, "hhs_select", "agent").
classified(S, "bwc_select_agents", "bacterial_pathogen", "Bacterial Select Agent") :-
    substance(S), pathogen_type(S, "bacterium"), schedule(S, "usda_select", "agent").
classified(S, "bwc_select_agents", "bacterial_pathogen", "Bacterial Select Agent") :-
    substance(S), pathogen_type(S, "bacterium"), schedule(S, "australia_group", "biological").

classified(S, "bwc_select_agents", "viral_pathogen", "Viral Select Agent") :-
    substance(S), pathogen_type(S, "virus"), schedule(S, "hhs_select", "agent").
classified(S, "bwc_select_agents", "viral_pathogen", "Viral Select Agent") :-
    substance(S), pathogen_type(S, "virus"), schedule(S, "usda_select", "agent").
classified(S, "bwc_select_agents", "viral_pathogen", "Viral Select Agent") :-
    substance(S), pathogen_type(S, "virus"), schedule(S, "australia_group", "biological").

classified(S, "bwc_select_agents", "fungal_pathogen", "Fungal Select Agent") :-
    substance(S), pathogen_type(S, "fungus"), schedule(S, "hhs_select", "agent").
classified(S, "bwc_select_agents", "fungal_pathogen", "Fungal Select Agent") :-
    substance(S), pathogen_type(S, "fungus"), schedule(S, "usda_select", "agent").
classified(S, "bwc_select_agents", "fungal_pathogen", "Fungal Select Agent") :-
    substance(S), pathogen_type(S, "fungus"), schedule(S, "australia_group", "biological").

classified(S, "bwc_select_agents", "biological_toxin", "Biological Toxin") :-
    substance(S), pathogen_type(S, "toxin"), schedule(S, "hhs_select", "agent").
classified(S, "bwc_select_agents", "biological_toxin", "Biological Toxin") :-
    substance(S), pathogen_type(S, "toxin"), schedule(S, "usda_select", "agent").
classified(S, "bwc_select_agents", "biological_toxin", "Biological Toxin") :-
    substance(S), pathogen_type(S, "toxin"), schedule(S, "australia_group", "biological").

% Proliferation concerns for biological agents
proliferation_concern(S, "select_agent_diversion") :-
    classified(S, "bwc_select_agents", "tier_1_select_agent", _).

proliferation_concern(S, "biological_weapons_precursor") :-
    classified(S, "bwc_select_agents", "bsl_4_pathogen", _).

% Human review requirements
requires_human_review(S, "Tier 1 select agent requires enhanced security review") :-
    classified(S, "bwc_select_agents", "tier_1_select_agent", _).

requires_human_review(S, "BSL-4 pathogen requires maximum containment verification") :-
    classified(S, "bwc_select_agents", "bsl_4_pathogen", _).

requires_human_review(S, "Biological toxin requires dual-use review") :-
    classified(S, "bwc_select_agents", "biological_toxin", _).