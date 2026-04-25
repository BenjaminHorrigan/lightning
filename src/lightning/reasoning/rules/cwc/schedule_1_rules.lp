% =============================================================================
% CWC Schedule 1 classification rules
% Source: CWC Annex on Chemicals — Schedule 1 (no significant peaceful use)
% =============================================================================
% Operates on the standard atom vocabulary populated by
% schedule_1_generated.lp (bulk-loaded from data/sources/cwc_schedule_1.csv).

% Any substance on Schedule 1 is classified
classified(S, "cwc", "schedule_1", "Listed CWC Schedule 1 chemical") :-
    substance(S),
    schedule(S, "cwc", "1").

% Schedule 1 substances trigger proliferation concern
proliferation_concern(S, "chemical_weapons_agent") :-
    classified(S, "cwc", "schedule_1", _).

% Any research involving Schedule 1 requires OPCW declaration (Article III)
requires_human_review(S, "Schedule 1 requires OPCW declaration under CWC Article III") :-
    classified(S, "cwc", "schedule_1", _).
