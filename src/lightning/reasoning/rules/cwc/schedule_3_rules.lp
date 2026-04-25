% =============================================================================
% CWC Schedule 3 classification rules
% Source: CWC Annex on Chemicals — Schedule 3 (bulk industrial chemicals)
% =============================================================================
% schedule_1.lp emits classified(Sub, "CWC_Schedule_3", ...) for named
% Schedule 3 chemicals. This file adds proliferation markers only.

proliferation_concern(S, "industrial_chemical_cw_potential") :-
    classified(S, "CWC_Schedule_3", _).

requires_human_review(S, "Schedule 3 chemical requires end-use verification") :-
    classified(S, "CWC_Schedule_3", _).
