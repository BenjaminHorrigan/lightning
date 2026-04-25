% ============================================================================
% Select Agents — HHS / USDA
% Sources: 42 CFR 73 (HHS), 7 CFR 331 (USDA plant), 9 CFR 121 (USDA animal)
% ============================================================================
% Five-section layout per aegis_RULE_EXPANSION.md Phase C template.
%
% Toxin thresholds in the CFR are stated in milligrams (some below 1 mg).
% Clingo's integer sort rejects floats like 0.5, so we encode thresholds in
% MICROGRAMS (ug) throughout. The engine emits quantity facts in both mg
% and grams from Substance.quantity + unit — for toxin threshold rules we
% multiply mg by 1000 on the rule side.

% ----------------------------------------------------------------------------
% Section 1 — Taxonomy
% ----------------------------------------------------------------------------
% HHS Select Agents (42 CFR 73.3)
hhs_select_agent("bacillus_anthracis").
hhs_select_agent("yersinia_pestis").
hhs_select_agent("francisella_tularensis").
hhs_select_agent("ebolavirus").
hhs_select_agent("marburgvirus").
hhs_select_agent("variola_major").
hhs_select_agent("variola_minor").
hhs_select_agent("lassa_fever_virus").

% USDA Select Agents (7 CFR 331, 9 CFR 121)
usda_select_agent("foot_and_mouth_disease_virus").
usda_select_agent("rinderpest_virus").
usda_select_agent("classical_swine_fever_virus").
usda_select_agent("african_swine_fever_virus").

% Overlap select agents (both HHS and USDA jurisdiction)
overlap_select_agent("bacillus_anthracis").
overlap_select_agent("brucella_abortus").
overlap_select_agent("burkholderia_mallei").
overlap_select_agent("burkholderia_pseudomallei").

% HHS Select Toxins — thresholds in MICROGRAMS (42 CFR 73.3(d))
% Values scaled from the regulation's milligram thresholds.
hhs_select_toxin("botulinum_toxin", 500).        % 0.5 mg threshold
hhs_select_toxin("ricin", 1000000).              % 1000 mg threshold
hhs_select_toxin("saxitoxin", 500000).           % 500 mg threshold
hhs_select_toxin("tetrodotoxin", 500000).        % 500 mg threshold
hhs_select_toxin("abrin", 1000000).              % 1000 mg threshold

% ----------------------------------------------------------------------------
% Section 2 — Thresholds (toxin quantities)
% ----------------------------------------------------------------------------
% Convert emitted quantity_mg/2 to micrograms by multiplying by 1000, then
% compare against the µg threshold. Clingo's integer arithmetic handles this
% cleanly because the threshold is always an integer µg count.
classified(Sub, "SELECT_TOXIN_THRESHOLD", "42 CFR 73.3(d)") :-
    substance(Sub),
    hhs_select_toxin(Sub, ThresholdUg),
    quantity_mg(Sub, Mg),
    Mg * 1000 > ThresholdUg.

% ----------------------------------------------------------------------------
% Section 3 — Inheritance (n/a at this depth; organism lineage is v2)
% ----------------------------------------------------------------------------

% ----------------------------------------------------------------------------
% Section 4 — Exclusions: sub-threshold toxin quantities are released
% ----------------------------------------------------------------------------
released_from_control(Sub) :-
    substance(Sub),
    hhs_select_toxin(Sub, ThresholdUg),
    quantity_mg(Sub, Mg),
    Mg * 1000 <= ThresholdUg.

% ----------------------------------------------------------------------------
% Section 5 — Classification output
% ----------------------------------------------------------------------------
% Direct organism match — HHS jurisdiction
classified(Sub, "SELECT_AGENT_HHS", "42 CFR 73.3") :-
    substance(Sub),
    hhs_select_agent(Sub),
    not released_from_control(Sub).

% Direct organism match — USDA jurisdiction
classified(Sub, "SELECT_AGENT_USDA", "9 CFR 121.3") :-
    substance(Sub),
    usda_select_agent(Sub),
    not released_from_control(Sub).

% Overlap marker: surfaces when both HHS and USDA jurisdictions apply.
classified(Sub, "SELECT_AGENT_OVERLAP", "42 CFR 73.4 / 9 CFR 121.4") :-
    substance(Sub),
    overlap_select_agent(Sub),
    not released_from_control(Sub).

#show classified/3.
