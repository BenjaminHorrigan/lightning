% =============================================================================
% Biological Agent Quantity Thresholds
% Source: 42 CFR 73.4, 7 CFR 331.3, Australia Group Guidelines
% =============================================================================
% Defines quantity thresholds for select agents and biological toxins

% Tier 1 thresholds (very low due to extreme danger)
classified(S, "bwc_select_agents", "tier_1_threshold_exceeded", "Tier 1 quantity threshold exceeded") :-
    substance(S),
    tier_1(S, "yes"),
    quantity_mg(S, Amount),
    Amount > 100.

% BSL-4 pathogen thresholds
classified(S, "bwc_select_agents", "bsl_4_threshold_exceeded", "BSL-4 quantity threshold exceeded") :-
    substance(S),
    biosafety_level(S, "4"),
    quantity_mg(S, Amount),
    Amount > 1000.

% Biological toxin thresholds (lower than live agents)
classified(S, "bwc_select_agents", "toxin_threshold_exceeded", "Biological toxin quantity threshold exceeded") :-
    substance(S),
    pathogen_type(S, "toxin"),
    quantity_mg(S, Amount),
    Amount > 10.

% General select agent thresholds
classified(S, "bwc_select_agents", "select_agent_threshold_exceeded", "Select agent quantity threshold exceeded") :-
    substance(S),
    schedule(S, "hhs_select", "agent"),
    quantity_grams(S, Amount),
    Amount > 10.
classified(S, "bwc_select_agents", "select_agent_threshold_exceeded", "Select agent quantity threshold exceeded") :-
    substance(S),
    schedule(S, "usda_select", "agent"),
    quantity_grams(S, Amount),
    Amount > 10.

% Enhanced review for threshold exceedances
requires_human_review(S, "Tier 1 quantity threshold exceeded - enhanced security protocols required") :-
    classified(S, "bwc_select_agents", "tier_1_threshold_exceeded", _).

requires_human_review(S, "BSL-4 quantity threshold exceeded - maximum containment review required") :-
    classified(S, "bwc_select_agents", "bsl_4_threshold_exceeded", _).

requires_human_review(S, "Biological toxin threshold exceeded - dual-use assessment required") :-
    classified(S, "bwc_select_agents", "toxin_threshold_exceeded", _).

% Proliferation concerns based on thresholds
proliferation_concern(S, "weaponization_quantity") :-
    classified(S, "bwc_select_agents", "tier_1_threshold_exceeded", _).

proliferation_concern(S, "biological_weapons_stockpiling") :-
    classified(S, "bwc_select_agents", "select_agent_threshold_exceeded", _),
    tier_1(S, "yes").