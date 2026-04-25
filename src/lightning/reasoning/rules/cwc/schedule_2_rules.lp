% =============================================================================
% CWC Schedule 2 classification rules
% Source: CWC Annex on Chemicals — Schedule 2 (dual-use precursors)
% =============================================================================
% schedule_1.lp emits classified(Sub, "CWC_Schedule_2_threshold", ...) using
% quantity_grams/2 with a 100 g threshold. Below-threshold quantities produce
% no classification (ALLOW). This file adds proliferation markers only.

% Threshold-exceeding Schedule 2 substances require enhanced review
requires_human_review(S, "Schedule 2 above 100g threshold requires OPCW declaration") :-
    classified(S, "CWC_Schedule_2_threshold", _).

proliferation_concern(S, "dual_use_precursor") :-
    classified(S, "CWC_Schedule_2_threshold", _).
