% ============================================================================
% CWC — Chemical Weapons Convention — Schedules 1/2/3
% Source: CWC Annex on Chemicals (OPCW), 22 U.S.C. 6701 et seq. (US CWCIA)
% ============================================================================
% Five-section layout per lightning_RULE_EXPANSION.md Phase C template.
%
% v1 SCOPE: named-substance matching on Schedules 1/2/3, plus a precursor
% list derived from the Schedule 1 Annex. Quantity threshold for Schedule 2
% uses quantity_grams/2 emitted by the engine's unit-conversion layer.
%
% DEFERRED to v2:
%   - Structural matching via rdkit SMARTS patterns (requires Python bridge
%     and the rdkit optional dep; out-of-scope for the hackathon demo).
%   - Precursor-chain proximity (requires reaction_product_of/3 from the
%     extractor; not implemented — would be a dangling reference).

% ----------------------------------------------------------------------------
% Section 1 — Taxonomy
% ----------------------------------------------------------------------------
% Schedule 1 — listed toxic chemicals and their direct precursors
schedule_1_chemical("tabun").
schedule_1_chemical("sarin").
schedule_1_chemical("soman").
schedule_1_chemical("vx").
schedule_1_chemical("novichok_a232").
schedule_1_chemical("novichok_a234").
schedule_1_chemical("sulfur_mustard").
schedule_1_chemical("nitrogen_mustard_hn1").
schedule_1_chemical("nitrogen_mustard_hn2").
schedule_1_chemical("nitrogen_mustard_hn3").
schedule_1_chemical("lewisite_1").
schedule_1_chemical("saxitoxin").
schedule_1_chemical("ricin").

% Schedule 1 precursors enumerated in the CWC Annex
schedule_1_precursor("methylphosphonic_dichloride").
schedule_1_precursor("methylphosphonic_difluoride").
schedule_1_precursor("pinacolyl_alcohol").
schedule_1_precursor("o_ethyl_2_diisopropylaminoethyl_methylphosphonite").

% Schedule 2 — dual-use chemicals subject to declaration above threshold
schedule_2_chemical("amiton").
schedule_2_chemical("pfib").
schedule_2_chemical("bz").
schedule_2_chemical("thiodiglycol").

% Schedule 3 — large-volume industrial chemicals with CW potential
schedule_3_chemical("phosgene").
schedule_3_chemical("cyanogen_chloride").
schedule_3_chemical("hydrogen_cyanide").
schedule_3_chemical("chloropicrin").
schedule_3_chemical("triethanolamine").

% ----------------------------------------------------------------------------
% Section 2 — Thresholds
% ----------------------------------------------------------------------------
% Schedule 2 declarations apply above 100 g (CWCIA Part VI). Below threshold,
% Schedule 2 substances are not themselves subject to classification here.
classified(Sub, "CWC_Schedule_2_threshold", "CWC Schedule 2, Article VI") :-
    substance(Sub),
    schedule_2_chemical(Sub),
    quantity_grams(Sub, Q),
    Q > 100.

% ----------------------------------------------------------------------------
% Section 3 — Inheritance (n/a for chemicals; handled by substructure
%                          matching in v2)
% ----------------------------------------------------------------------------

% ----------------------------------------------------------------------------
% Section 4 — Exclusions (handled at the decision layer via quantity<=threshold
%                         on Schedule 2; Schedule 1 has no release at this
%                         encoding depth)
% ----------------------------------------------------------------------------

% ----------------------------------------------------------------------------
% Section 5 — Classification output
% ----------------------------------------------------------------------------
% Direct Schedule 1 match — always controlled regardless of quantity.
classified(Sub, "CWC_Schedule_1", "CWC Schedule 1") :-
    substance(Sub),
    schedule_1_chemical(Sub).

% Schedule 1 precursor match — also always controlled.
classified(Sub, "CWC_Schedule_1_precursor", "CWC Schedule 1, Part B (precursors)") :-
    substance(Sub),
    schedule_1_precursor(Sub).

% Schedule 3 direct match — applies to named chemicals regardless of quantity.
classified(Sub, "CWC_Schedule_3", "CWC Schedule 3") :-
    substance(Sub),
    schedule_3_chemical(Sub).

#show classified/3.
