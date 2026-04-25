% =============================================================================
% DEA Schedule II classification rules
% Source: 21 CFR 1308.12 (Controlled Substances Act, Schedule II)
% =============================================================================
% Schedule II = high abuse potential, accepted medical use (prescription only).
% Manufacture requires DEA registration; fentanyl analogs have enhanced penalties.

classified(S, "dea", "schedule_ii", "DEA Schedule II controlled substance") :-
    substance(S),
    schedule(S, "dea", "II").

% Any non-trivial Schedule II quantity → manufacturer registration required
classified(S, "dea", "schedule_ii_manufacturing", "Schedule II quantity requires DEA manufacturer registration") :-
    substance(S),
    schedule(S, "dea", "II"),
    quantity(S, Amount, "g"),
    Amount > 1.

% Fentanyl-class substances get an extra classification for enhanced penalties
% (21 USC 841(b)(1)(A)/(B) thresholds for fentanyl analogs are far stricter)
fentanyl_analog("fentanyl").
fentanyl_analog("acetylfentanyl").
fentanyl_analog("butyrfentanyl").
fentanyl_analog("carfentanil").
fentanyl_analog("alpha_methylfentanyl").
fentanyl_analog("3_methylfentanyl").

classified(S, "dea", "fentanyl_analog", "Fentanyl analog — enhanced penalties under 21 USC 841") :-
    substance(S),
    schedule(S, "dea", "II"),
    fentanyl_analog(S).

requires_human_review(S, "Schedule II synthesis requires DEA manufacturer registration") :-
    classified(S, "dea", "schedule_ii_manufacturing", _).
