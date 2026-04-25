% =============================================================================
% CWC Schedule 3 classification rules
% Source: CWC Annex on Chemicals — Schedule 3 (bulk industrial chemicals)
% =============================================================================

% Any substance on Schedule 3 is classified (informational)
classified(S, "cwc", "schedule_3", "Listed CWC Schedule 3 chemical") :-
    substance(S),
    schedule(S, "cwc", "3").

% Schedule 3 production thresholds (typically 30 tonnes/year)
classified(S, "cwc", "schedule_3_threshold", "Exceeds Schedule 3 production threshold (30t)") :-
    substance(S),
    schedule(S, "cwc", "3"),
    quantity(S, Amount, "kg"),
    Amount > 30000.

% Schedule 3 at small scale → dual-use, generally allowable
dual_use_item(S) :-
    classified(S, "cwc", "schedule_3", _),
    quantity(S, Amount, "kg"),
    Amount <= 30000.
