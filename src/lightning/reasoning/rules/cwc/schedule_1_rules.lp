% =============================================================================
% CWC Schedule 1 classification rules
% Source: CWC Annex on Chemicals — Schedule 1 (no significant peaceful use)
% =============================================================================
% schedule_1.lp emits classified/3 atoms with the authoritative labels.
% This file adds proliferation and review markers that reference those atoms.

% Schedule 1 substances trigger proliferation concern
proliferation_concern(S, "chemical_weapons_agent") :-
    classified(S, "CWC_Schedule_1", _).

% Any research involving Schedule 1 requires OPCW declaration (Article III)
requires_human_review(S, "Schedule 1 requires OPCW declaration under CWC Article III") :-
    classified(S, "CWC_Schedule_1", _).
