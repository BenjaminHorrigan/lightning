# LIGHTNING Rule Engine Expansion Tasks

**For Claude Code to execute.** Assumes Phases 1-3 of the original handoff are complete and the system runs end-to-end.

## Status entering this task

- USML Category IV: ~70% (paragraphs a/d/h/h(1) done, specially-designed core done)
- CWC / MTCR / Select Agents: ~20% each (named-match stubs only)

## Goal

- Get USML to ~95% (credible under expert scrutiny)
- Lay down consistent extension skeletons for CWC, MTCR, Select Agents
- Establish one repeatable rule-authoring pattern across all regimes

## Critical invariants

1. Every KB file must end with `#show classified/3.` The engine expects that predicate.
2. Never delete existing rules; extend only.
3. Every citation in `citations.json` must reference a real CFR paragraph.
4. When a new rule references a fact type the extractor doesn't produce, update the extractor schema, prompt, and engine fact-emission in the same phase. Never leave dangling references.
5. Test each phase by running the existing golden test suite; add new tests before adding new rules.

---

## Phase A — Finish USML Category IV

Edit `src/lightning/knowledge_base/usml_cat_iv.lp` and `src/lightning/knowledge_base/citations.json`.

### A.1 Paragraph (b): launch vehicle sub-articles

```prolog
category_iv_b("solid_rocket_motor").
category_iv_b("liquid_rocket_engine").
category_iv_b("hybrid_rocket_motor").
category_iv_b("ramjet").
category_iv_b("scramjet").
category_iv_b("stage").
category_iv_b("interstage").
category_iv_b("payload_fairing").

classified(Component, "USML_IV_b", "22 CFR 121.1 Category IV(b)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_b(Cat).
```

Add matching `citations.json` entry with real CFR reference.

### A.2 Paragraph (c): launch-support equipment with NFPA 1122 release

The NFPA 1122 consumer-hobby exclusion is explicit in the regulation and demonstrates release-paragraph reasoning.

```prolog
category_iv_c("transporter_erector_launcher").
category_iv_c("launch_stand").
category_iv_c("umbilical_tower").
category_iv_c("launch_control_system").
category_iv_c("propellant_loading_equipment").

released_from_control(Component) :-
    component(Component),
    attribute(Component, "hobby_rocket_nfpa_1122").

classified(Component, "USML_IV_c", "22 CFR 121.1 Category IV(c)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_c(Cat),
    not released_from_control(Component).
```

### A.3 Paragraph (f): test and production equipment — HIGH PRIORITY

The most likely judge pop-quiz topic for a rocket-focused demo.

```prolog
category_iv_f_production("filament_winding_machine").
category_iv_f_production("isostatic_press_rocket").
category_iv_f_production("rocket_motor_test_stand").
category_iv_f_production("engine_test_cell").
category_iv_f_production("propellant_mixer_industrial").
category_iv_f_production("nozzle_forming_equipment").
category_iv_f_production("vacuum_chamber_spacecraft_testing").

classified(Component, "USML_IV_f", "22 CFR 121.1 Category IV(f)") :-
    component(Component),
    component_category(Component, Cat),
    category_iv_f_production(Cat),
    specially_designed(Component).

% Inherited control: test equipment whose parent is a Category IV system
classified(Component, "USML_IV_f", "22 CFR 121.1 Category IV(f)") :-
    component(Component),
    component_category(Component, "test_equipment"),
    parent_system(Component, System),
    usml_controlled_end_item(System).
```

### A.4 Paragraph (g): DoD-funded developmental

```prolog
classified(Component, "USML_IV_g", "22 CFR 121.1 Category IV(g)") :-
    component(Component),
    attribute(Component, "dod_funded_development").
```

### A.5 Expand paragraph (h) component list

Add to the existing category_iv_h_component facts:

```prolog
category_iv_h_component("rocket_motor_case").
category_iv_h_component("flange_motor_case").
category_iv_h_component("flange_seal_motor_case").
category_iv_h_component("end_dome_motor_case").
category_iv_h_component("inertial_measurement_unit").
category_iv_h_component("thrust_chamber_regen_cooled").
category_iv_h_component("ablative_liner").
category_iv_h_component("reentry_vehicle_heat_shield").
category_iv_h_component("penetration_aid").
category_iv_h_component("decoy_reentry").
category_iv_h_component("submunition_dispenser").
```

### A.6 MTCR marking — bridges USML to MTCR regime

```prolog
mtcr_marked("rocket").
mtcr_marked("space_launch_vehicle").
mtcr_marked("ballistic_missile").
mtcr_marked("cruise_missile").
mtcr_marked("rocket_motor_case").
mtcr_marked("solid_rocket_motor").
mtcr_marked("liquid_rocket_engine").

mtcr_controlled(Component) :-
    classified(Component, _, _),
    component_category(Component, Cat),
    mtcr_marked(Cat).

#show mtcr_controlled/1.
```

### A.7 IV(a)(2) numerical threshold

```prolog
classified(System, "USML_IV_a_2", "22 CFR 121.1 Category IV(a)(2)") :-
    system(System),
    performance(System, "payload_kg", Payload),
    performance(System, "range_km", Range),
    Payload >= 500,
    Range >= 300.
```

### A.8 Complete 120.41(b) release paragraphs

Add release (b)(2) and (b)(4) to supplement the existing (1), (3), (5):

```prolog
% 120.41(b)(2) developed with knowledge of both USML and non-USML use
released_from_control(Component) :-
    attribute(Component, "developed_for_both_usml_and_non_usml"),
    attribute(Component, "general_commercial_availability").

% 120.41(b)(4) developed with knowledge of only non-USML use
released_from_control(Component) :-
    attribute(Component, "developed_only_non_usml"),
    not parent_system(Component, _).
```

### A.9 Propellant expansion for IV(h)(1)

```prolog
controlled_propellant("nitromethane").
controlled_propellant("ammonium_perchlorate").
controlled_propellant("hmx").
controlled_propellant("rdx").
controlled_propellant("cl_20").
controlled_propellant("gap").
controlled_propellant("htpb_bound_propellant").
```

### A.10 Technical data provision IV(i)

```prolog
technical_data_artifact(Artifact) :-
    artifact_attribute(Artifact, "technical_data").

classified(Artifact, "USML_IV_i", "22 CFR 121.1 Category IV(i); 22 CFR 120.10") :-
    technical_data_artifact(Artifact),
    classified_subject_matter(Artifact, Subject),
    classified(Subject, _, _).
```

### A.11 Add all new citations to citations.json

Add entries for USML_IV_b, USML_IV_c, USML_IV_f, USML_IV_g, USML_IV_i following the existing pattern. Use real CFR references. Do not invent.

---

## Phase B — Extractor schema update

New rules reference facts the extractor does not currently produce. Must be done in the same PR as Phase A rules.

### B.1 Add `attributes` to Component model

In `src/lightning/models.py`:

```python
attributes: list[str] = Field(
    default_factory=list,
    description="Provenance flags: 'dod_funded_development', 'general_commercial_availability', 'hobby_rocket_nfpa_1122', 'developed_for_both_usml_and_non_usml', 'developed_only_non_usml'"
)
```

### B.2 Emit attribute facts from engine

In `src/lightning/reasoning/engine.py::artifact_to_facts`, after existing Component handling:

```python
for attr in comp.attributes:
    facts.append(f'attribute("{name}", "{_sanitize(attr)}").')
```

Also emit system-level performance when a component's specifications describe its parent system:

```python
if comp.parent_system:
    parent = _sanitize(comp.parent_system)
    for spec in comp.specifications:
        facts.append(
            f'performance("{parent}", "{_sanitize(spec.parameter)}", {spec.value}).'
        )
```

### B.3 Extraction prompt additions

Append to both `protocol.py` and `design.py` prompts:

```
Additionally, extract provenance attributes only when clearly stated:
- "dod_funded_development" when DoD contract or program is named
- "general_commercial_availability" when commercial equivalent is explicitly asserted
- "hobby_rocket_nfpa_1122" when NFPA 1122 compliance is referenced
- "developed_for_both_usml_and_non_usml" when dual-development history stated
- "developed_only_non_usml" when commercial-only development stated

Do NOT infer from weak signals. Leave empty when unclear.

For systems, extract performance metrics:
- range_km (maximum flight range, kilometers)
- payload_kg (payload mass capability, kilograms)
These attach to systems, not components.
```

### B.4 Add regression test

Create `examples/model_rocket_release.md` — artifact explicitly references NFPA 1122 compliance. Expected decision: ALLOW (release paragraph fires). This validates the release logic.

---

## Phase C — Stub-pattern extensions for other regimes

Each regime follows the same five-section pattern. Apply this template consistently so future expansion is mechanical.

### The five sections every regime file should have

1. **Taxonomy facts** — objects the regime knows about
2. **Threshold rules** — numerical cutoffs
3. **Inheritance rules** — parts-of-whole reasoning
4. **Exclusion rules** — when otherwise-controlled items are released
5. **Classification output rules** — producing `classified/3` atoms

Every file ends with `#show classified/3.`

### C.1 CWC Schedule 1 expansion — `cwc_sched1.lp`

```prolog
% Taxonomy
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

schedule_2_chemical("amiton").
schedule_2_chemical("pfib").

schedule_3_chemical("phosgene").
schedule_3_chemical("cyanogen_chloride").
schedule_3_chemical("hydrogen_cyanide").
schedule_3_chemical("chloropicrin").

% Structural match (facts injected from Python via rdkit SMARTS)
classified(Sub, "CWC_Schedule_1_structural", "CWC Schedule 1") :-
    substance(Sub),
    cwc_substructure_match(Sub, _Family).

% Quantity threshold for Schedule 2 declarations (Article VI)
classified(Sub, "CWC_Schedule_2_threshold", "CWC Schedule 2, Article VI") :-
    substance(Sub),
    schedule_2_chemical(Sub),
    quantity_grams(Sub, Q),
    Q > 100.

% Precursor proximity (N reaction steps from Schedule 1)
precursor_to_schedule_1(Reagent, 1) :-
    substance(Reagent),
    reaction_product_of(Target, Reagent, _),
    schedule_1_chemical(Target).

precursor_to_schedule_1(Reagent, 2) :-
    substance(Reagent),
    reaction_product_of(Intermediate, Reagent, _),
    precursor_to_schedule_1(Intermediate, 1).

escalate_cwc_precursor_proximity(Sub, N) :-
    precursor_to_schedule_1(Sub, N),
    N <= 2.

#show classified/3.
#show escalate_cwc_precursor_proximity/2.
```

**Python companion work:** create `src/lightning/reasoning/chemistry.py` with rdkit SMARTS patterns for tabun, sarin, VX, mustard, lewisite families. Called from `engine.py` before clingo invocation to inject `cwc_substructure_match/2` facts. Optional for v1 but essential for making the stub credible.

### C.2 MTCR expansion — `mtcr.lp`

```prolog
% Category I complete systems
classified(System, "MTCR_Category_I", "MTCR Annex Category I") :-
    system(System),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P >= 500, R >= 300.

classified(System, "MTCR_Category_I_UAV", "MTCR Annex Category I (UAVs)") :-
    system(System),
    system_type(System, "uav"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P >= 500, R >= 300.

% Category II components
category_ii_component("rocket_engine").
category_ii_component("rocket_motor").
category_ii_component("composite_motor_case").
category_ii_component("re_entry_vehicle").
category_ii_component("guidance_equipment").
category_ii_component("thrust_vector_control_mtcr").
category_ii_component("propellant_production_equipment").

classified(Component, "MTCR_Category_II", "MTCR Annex Category II") :-
    component(Component),
    component_category(Component, Cat),
    category_ii_component(Cat),
    specially_designed(Component).

% Sub-threshold systems capable of WMD delivery
classified(System, "MTCR_Category_II_sub_threshold",
           "MTCR Annex Category II (sub-threshold)") :-
    system(System),
    system_type(System, Type),
    (Type = "rocket" ; Type = "missile" ; Type = "uav"),
    performance(System, "payload_kg", P),
    performance(System, "range_km", R),
    P < 500, R >= 300, P >= 300.

#show classified/3.
```

### C.3 Select Agents expansion — `select.lp`

```prolog
% HHS Select Agents (42 CFR 73)
hhs_select_agent("bacillus_anthracis").
hhs_select_agent("yersinia_pestis").
hhs_select_agent("francisella_tularensis").
hhs_select_agent("ebolavirus").
hhs_select_agent("marburgvirus").
hhs_select_agent("variola_major").
hhs_select_agent("variola_minor").
hhs_select_agent("lassa_fever_virus").

% HHS Select Toxins with quantity thresholds (42 CFR 73.3)
hhs_select_toxin("botulinum_toxin", 0.5).        % mg threshold
hhs_select_toxin("ricin", 1000).                 % mg threshold
hhs_select_toxin("saxitoxin", 500).              % mg threshold
hhs_select_toxin("tetrodotoxin", 500).           % mg threshold
hhs_select_toxin("abrin", 1000).                 % mg threshold

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

% Classification: direct organism match
classified(Sub, "SELECT_AGENT_HHS", "42 CFR 73.3") :-
    substance(Sub),
    hhs_select_agent(Sub).

classified(Sub, "SELECT_AGENT_USDA", "9 CFR 121.3") :-
    substance(Sub),
    usda_select_agent(Sub).

% Toxin threshold classification
classified(Sub, "SELECT_TOXIN_THRESHOLD", "42 CFR 73.3(d)") :-
    substance(Sub),
    hhs_select_toxin(Sub, ThresholdMg),
    quantity_mg(Sub, Q),
    Q > ThresholdMg.

% Sub-threshold toxin quantities are exempt
released_from_control(Sub) :-
    hhs_select_toxin(Sub, ThresholdMg),
    quantity_mg(Sub, Q),
    Q <= ThresholdMg.

#show classified/3.
```

**Python companion work:** taxonomic rollup (species → genus → controlled lineage) requires an organism ontology. Mark as v2 TODO; use direct-name matching for v1.

---

## Implementation order

Do phases in this exact sequence. Each is a separate commit:

1. **Phase A.1–A.11** — USML Category IV rule additions + citations
2. **Phase B.1–B.4** — Extractor schema update + prompt changes + regression test
3. **Run golden test suite.** Fix any regressions before proceeding.
4. **Phase C.1** — CWC Schedule 1 expansion (without rdkit integration)
5. **Phase C.2** — MTCR expansion
6. **Phase C.3** — Select Agents expansion
7. **Run full test suite again.** All should still pass; new escalation/classification cases should trigger as expected.
8. **(Optional, if time)** Create `src/lightning/reasoning/chemistry.py` with rdkit SMARTS patterns for CWC structural matching.

## Validation checkpoints

After Phase A+B:
- Existing `examples/itar_turbopump_spec.md` still produces REFUSE with USML_IV_h classification
- New `examples/model_rocket_release.md` produces ALLOW via release paragraph
- A new synthetic test case with payload=600 kg and range=400 km triggers USML_IV_a_2 classification

After Phase C:
- The existing benign Suzuki coupling still produces ALLOW (no false positives from new rules)
- All stub regime files still parse and solve without syntax errors
- `mtcr_controlled/1` atoms appear in the proof tree when a USML-classified item has an MTCR marking

## What this delivers

- **USML Category IV at ~95%** — covers a, b, c, d, f, g, h (with extended component list), h(1), i, and full specially-designed release logic
- **MTCR as genuinely-working secondary regime** — not just a stub; real threshold reasoning
- **CWC and Select Agents with production structure** — every rule author after this follows the same pattern
- **Credible narrative** — "LIGHTNING covers USML Category IV at 95% coverage and provides threshold-based reasoning for MTCR. Full CWC structural matching and Select Agents taxonomic rollup are planned for v2. Our architecture extends to new regimes with roughly one day of knowledge engineering per category."

That narrative survives a Q&A with someone who actually does this work for a living. The previous version did not.
