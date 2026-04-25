% =============================================================================
% DEA Schedule I classification rules
% Source: 21 CFR 1308.11 (Controlled Substances Act, Schedule I)
% =============================================================================
% Schedule I = high abuse potential, no accepted medical use.
% Synthesis without DEA Schedule I researcher license is illegal under
% 21 CFR 1301.

classified(S, "dea", "schedule_i", "DEA Schedule I controlled substance") :-
    substance(S),
    schedule(S, "dea", "I").

% Schedule I synthesis always requires human review (license verification)
requires_human_review(S, "Schedule I synthesis requires DEA Schedule I researcher license (21 CFR 1301)") :-
    classified(S, "dea", "schedule_i", _).

% Schedule I quantity threshold (1 g default; very low because zero medical use)
classified(S, "dea", "schedule_i_manufacturing", "Exceeds Schedule I manufacturing threshold (1g)") :-
    substance(S),
    schedule(S, "dea", "I"),
    quantity(S, Amount, "g"),
    Amount > 1.

proliferation_concern(S, "unlicensed_controlled_substance_manufacture") :-
    classified(S, "dea", "schedule_i_manufacturing", _).
