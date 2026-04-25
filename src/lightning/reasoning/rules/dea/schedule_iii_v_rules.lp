% =============================================================================
% DEA Schedules III/IV/V classification rules
% Source: 21 CFR 1308.13 (III), 1308.14 (IV), 1308.15 (V)
% =============================================================================
% Lower-risk controlled substances. Each schedule has its own threshold and
% review requirements.

classified(S, "dea", "schedule_iii", "DEA Schedule III controlled substance") :-
    substance(S),
    schedule(S, "dea", "III").

classified(S, "dea", "schedule_iv", "DEA Schedule IV controlled substance") :-
    substance(S),
    schedule(S, "dea", "IV").

classified(S, "dea", "schedule_v", "DEA Schedule V controlled substance") :-
    substance(S),
    schedule(S, "dea", "V").

% Schedule III/IV/V: synthesis still requires DEA registration but human review
% is informational rather than a blocker on small quantities.
requires_human_review(S, "Schedule III–V manufacture requires DEA registration") :-
    substance(S),
    schedule(S, "dea", "III").
requires_human_review(S, "Schedule III–V manufacture requires DEA registration") :-
    substance(S),
    schedule(S, "dea", "IV").
requires_human_review(S, "Schedule III–V manufacture requires DEA registration") :-
    substance(S),
    schedule(S, "dea", "V").
