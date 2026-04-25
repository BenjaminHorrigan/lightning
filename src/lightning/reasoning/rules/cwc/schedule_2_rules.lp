% =============================================================================
% CWC Schedule 2 classification rules
% Source: CWC Annex on Chemicals — Schedule 2 (dual-use precursors)
% =============================================================================

% Any substance on Schedule 2 is classified
classified(S, "cwc", "schedule_2", "Listed CWC Schedule 2 chemical") :-
    substance(S),
    schedule(S, "cwc", "2").

% Threshold-exceeding Schedule 2 substances trigger an additional classification
classified(S, "cwc", "schedule_2_threshold", "Exceeds Schedule 2 quantity threshold") :-
    substance(S),
    schedule(S, "cwc", "2"),
    quantity(S, Amount, "kg"),
    quantity_threshold(S, Threshold, "kg"),
    Amount > Threshold.

% Default threshold of 1 kg if not otherwise specified
quantity_threshold(S, 1, "kg") :-
    substance(S),
    schedule(S, "cwc", "2"),
    not _has_explicit_threshold(S).

_has_explicit_threshold(S) :- quantity_threshold(S, _, "kg").
