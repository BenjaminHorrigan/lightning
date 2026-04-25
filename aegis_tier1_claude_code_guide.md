# AEGIS Tier 1 Implementation — Claude Code Guide

**Goal:** Implement the 885-rule Tier 1 expansion covering core dual-use research regimes. This transforms AEGIS from "covers 3 partial regimes" to "covers the full universe of chemistry, biology, and AI compute controls."

**Prerequisites:** 
- Phase 0 foundation integrated (directory structure, atom vocabulary, bulk loader)
- Python environment with CSV manipulation capabilities
- Access to pull official government lists (or ability to create representative test data)

**Total effort:** ~32 hours across 7 regimes. Each task is independently testable.

---

## Task Priority Matrix

| Priority | Regime | Effort | Demo Impact | Implementation Complexity |
|----------|--------|--------|-------------|---------------------------|
| **P0** | CWC Schedules 1/2/3 | 4h | **HIGH** (chemical weapons) | **LOW** (mostly CSV) |
| **P0** | DEA Schedules I-V | 4h | **HIGH** (drug synthesis) | **LOW** (mostly CSV) |
| **P0** | BIS AI/Compute | 4h | **HIGH** (political salience) | **MEDIUM** (novel thresholds) |
| **P1** | HHS/USDA/AG Bio | 4h | **HIGH** (bioweapons) | **LOW** (mostly CSV) |
| **P1** | USML Cat XIV (toxics) | 3h | **MEDIUM** (overlaps CWC) | **LOW** (list-based) |
| **P2** | USML Cat V (explosives) | 5h | **MEDIUM** (pattern logic) | **HIGH** (complex rules) |
| **P2** | EAR Cat 1 (chem/bio) | 8h | **MEDIUM** (export control) | **HIGH** (ECCN structure) |

**Recommended implementation order:** P0 first (12 hours, maximum demo impact), then P1 (7 hours), then P2 (13 hours) as time permits.

---

## TASK 1: CWC Chemical Weapons Convention — 4 hours

**Deliverables:**
- 3 generated `.lp` files with substance atoms (Schedules 1, 2, 3)
- 4 classification rule files
- 1 pattern-detection rule file
- CSV source files (130+ substances total)

### 1.1 Data Collection (1 hour)

**Objective:** Create CSV files for all three CWC schedules from official sources.

**Primary source:** [OPCW Chemical Weapons Convention Annex](https://www.opcw.org/chemical-weapons-convention/annexes/annex-chemicals)

**Files to create:**
- `data/sources/cwc_schedule_1.csv` — 12 substances, no peaceful use
- `data/sources/cwc_schedule_2.csv` — 14 substances + precursors, dual-use  
- `data/sources/cwc_schedule_3.csv` — 17 substances, bulk industrial

**CSV format:**
```csv
canonical_name,cas_number,iupac_name,molecular_formula,threshold_kg,notes
Sarin,107-44-8,Methylphosphonofluoridic acid,C4H10FO2P,,Schedule 1 nerve agent
VX,50782-69-9,Ethyl N-[2-(diisopropylamino)ethyl] methylphosphonothioate,C11H26NO2PS,,Schedule 1 nerve agent
```

**Key substances to include:**

*Schedule 1 (no significant peaceful use):*
- Sarin, Soman, Tabun, VX (nerve agents)
- Mustard gas, Lewisite 1/2/3 (blister agents)
- Ricin, Saxitoxin (toxins)
- 3-Quinuclidinyl benzilate (incapacitating agent)

*Schedule 2 (dual-use precursors):*
- Amiton, PFIB, BZ (precursors)
- Methylphosphonyl difluoride, Methylphosphonyl dichloride
- All organophosphorus + halogen combinations per CWC general formula

*Schedule 3 (bulk industrial):*
- Phosgene, Hydrogen cyanide, Chloropicrin
- Triethanolamine, Triethyl phosphite, Trimethyl phosphite

**Acceptance criteria:** CSVs validate with `python scripts/generate_substance_atoms.py --validate`

### 1.2 Generate Substance Atoms (15 minutes)

**Objective:** Convert CSV data to ASP atoms.

**Commands:**
```bash
python scripts/generate_substance_atoms.py --regime cwc_schedule_1
python scripts/generate_substance_atoms.py --regime cwc_schedule_2  
python scripts/generate_substance_atoms.py --regime cwc_schedule_3
```

**Expected output:**
- `src/aegis/reasoning/rules/cwc/schedule_1_generated.lp` — 12 substances × 4 atoms each = 48 atoms
- `src/aegis/reasoning/rules/cwc/schedule_2_generated.lp` — 14 substances × 4 atoms each = 56 atoms
- `src/aegis/reasoning/rules/cwc/schedule_3_generated.lp` — 17 substances × 4 atoms each = 68 atoms

**Acceptance criteria:** Generated files contain expected atom counts and no syntax errors.

### 1.3 Classification Rules (1 hour)

**Objective:** Write classification logic for each schedule.

**File:** `src/aegis/reasoning/rules/cwc/schedule_1_rules.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% CWC Schedule 1: No significant uses except protection
classified(S, "cwc", "schedule_1", "Listed Schedule 1 chemical") :-
    substance(S),
    schedule(S, "cwc", "1").

% Schedule 1 substances trigger proliferation concern
proliferation_concern(S, "chemical_weapons_agent") :-
    classified(S, "cwc", "schedule_1", _).

% Any research involving Schedule 1 requires OPCW declaration
requires_human_review(S, "Schedule 1 requires OPCW declaration under CWC Article III") :-
    classified(S, "cwc", "schedule_1", _).
```

**File:** `src/aegis/reasoning/rules/cwc/schedule_2_rules.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% CWC Schedule 2: Dual-use precursors with thresholds
classified(S, "cwc", "schedule_2", "Listed Schedule 2 chemical") :-
    substance(S),
    schedule(S, "cwc", "2").

% Threshold-based controls for Schedule 2
classified(S, "cwc", "schedule_2_threshold", "Exceeds Schedule 2 quantity threshold") :-
    substance(S),
    schedule(S, "cwc", "2"),
    quantity(S, Amount, "kg"),
    quantity_threshold(S, Threshold, "kg"),
    Amount > Threshold.

% Default threshold if not specified: 1 kg
quantity_threshold(S, 1.0, "kg") :-
    substance(S),
    schedule(S, "cwc", "2"),
    not quantity_threshold(S, _, "kg").

% Cross-regime check: Schedule 2 + USML toxics overlap
cross_regime_violation(S, ["cwc_schedule_2", "usml_xiv"], "Dual-listed toxic chemical") :-
    classified(S, "cwc", "schedule_2", _),
    classified(S, "usml", "XIV", _).
```

**File:** `src/aegis/reasoning/rules/cwc/schedule_3_rules.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% CWC Schedule 3: Bulk industrial chemicals with weapons potential
classified(S, "cwc", "schedule_3", "Listed Schedule 3 chemical") :-
    substance(S),
    schedule(S, "cwc", "3").

% Higher thresholds for Schedule 3 (typically 30 tonnes/year production)
classified(S, "cwc", "schedule_3_threshold", "Exceeds Schedule 3 production threshold") :-
    substance(S),
    schedule(S, "cwc", "3"),
    quantity(S, Amount, "kg"),
    Amount > 30000.  % 30 tonnes

% Schedule 3 at small scale generally ALLOW
dual_use_item(S) :-
    classified(S, "cwc", "schedule_3", _),
    quantity(S, Amount, "kg"),
    Amount =< 30000.
```

### 1.4 Pattern Detection Rules (1.5 hours)

**Objective:** Implement the CWC "general purpose criterion" pattern detection.

**File:** `src/aegis/reasoning/rules/cwc/pattern_detection.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% CWC Article II.1.(a): "Any toxic chemical" for prohibited purposes
% This catches unlisted chemicals that match chemical weapons patterns

% Pattern 1: Organophosphorus + fluorination (classic nerve agent pattern)
classified(S, "cwc", "pattern_op_fluorinated", "Organophosphorus + fluorination pattern") :-
    substance(S),
    contains_functional_group(S, "organophosphorus"),
    contains_functional_group(S, "fluorinated"),
    not schedule(S, "cwc", _).  % Not already scheduled

% Pattern 2: Organophosphorus + halogenation (broader nerve agent precursor pattern)
classified(S, "cwc", "pattern_op_halogenated", "Organophosphorus + halogen pattern") :-
    substance(S),
    contains_functional_group(S, "organophosphorus"),
    (contains_functional_group(S, "chlorinated"); 
     contains_functional_group(S, "brominated");
     contains_functional_group(S, "fluorinated")),
    not schedule(S, "cwc", _).

% Pattern 3: Cholinesterase inhibitors (functional definition)
classified(S, "cwc", "pattern_cholinesterase", "Cholinesterase inhibitor pattern") :-
    substance(S),
    cholinesterase_inhibitor_structure(S),
    not schedule(S, "cwc", _).

% Structural patterns for cholinesterase inhibition
cholinesterase_inhibitor_structure(S) :-
    contains_functional_group(S, "organophosphorus"),
    contains_functional_group(S, "ester").

cholinesterase_inhibitor_structure(S) :-
    contains_functional_group(S, "carbamate"),
    contains_functional_group(S, "methyl").

% Pattern 4: Mustard-like alkylating agents
classified(S, "cwc", "pattern_alkylating", "Alkylating agent pattern") :-
    substance(S),
    alkylating_agent_structure(S),
    not schedule(S, "cwc", _).

alkylating_agent_structure(S) :-
    contains_functional_group(S, "bis_chloroethyl").

alkylating_agent_structure(S) :-
    contains_functional_group(S, "nitrogen_mustard").

% Pattern detection requires ESCALATE (human judgment on intent)
requires_human_review(S, "Matches CWC toxic chemical pattern - verify research intent") :-
    classified(S, "cwc", Pattern, _),
    string_concat("pattern_", _, Pattern).

% Cross-reference with stated research purpose
weapons_related(S, "chemical") :-
    classified(S, "cwc", Pattern, _),
    string_concat("pattern_", _, Pattern),
    research_purpose(Purpose),
    (string_contains(Purpose, "weapon");
     string_contains(Purpose, "military");
     string_contains(Purpose, "defense")).
```

### 1.5 Testing and Integration (45 minutes)

**Objective:** Verify CWC rules work correctly with test cases.

**Test file:** `tests/test_cwc_classification.py`
```python
import pytest
from aegis.reasoning import run_reasoner
from aegis.extraction import extract_from_text

def test_cwc_schedule_1_classification():
    """Test that Schedule 1 chemicals are correctly classified."""
    artifact_text = """
    Synthesis protocol for Sarin (methylphosphonofluoridic acid).
    Target purity: 95%
    Quantity: 50 mg for research purposes.
    """
    
    artifact = extract_from_text(artifact_text)
    proof = run_reasoner(artifact, regimes=["cwc"])
    
    # Should classify as Schedule 1
    classifications = [step.conclusion for step in proof.steps 
                     if "cwc" in step.conclusion and "schedule_1" in step.conclusion]
    assert len(classifications) > 0
    
    # Should require human review
    escalations = [step.conclusion for step in proof.steps
                  if "requires_human_review" in step.conclusion]
    assert len(escalations) > 0

def test_cwc_pattern_detection():
    """Test pattern-based detection of unlisted chemicals."""
    artifact_text = """
    Novel organophosphorus compound synthesis:
    Methylphosphonyl difluoride derivative with enhanced stability.
    Contains P-F bonds and ester linkages.
    """
    
    artifact = extract_from_text(artifact_text)
    proof = run_reasoner(artifact, regimes=["cwc"])
    
    # Should trigger organophosphorus + fluorination pattern
    patterns = [step.conclusion for step in proof.steps
               if "pattern_op_fluorinated" in step.conclusion]
    assert len(patterns) > 0

def test_cwc_schedule_2_threshold():
    """Test threshold-based controls for Schedule 2."""
    artifact_text = """
    Large-scale synthesis of amiton (Schedule 2).
    Planned production: 5.2 kg total yield.
    Purpose: Agricultural pesticide research.
    """
    
    artifact = extract_from_text(artifact_text)
    proof = run_reasoner(artifact, regimes=["cwc"])
    
    # Should classify as exceeding threshold (>1 kg)
    thresholds = [step.conclusion for step in proof.steps
                 if "schedule_2_threshold" in step.conclusion]
    assert len(thresholds) > 0
```

**Acceptance criteria:** All tests pass, CWC rules integrate with existing USML/MTCR rules without conflicts.

---

## TASK 2: DEA Controlled Substances — 4 hours

**Deliverables:**
- 3 generated `.lp` files with substance atoms (Schedules I, II, III-V)
- 5 threshold/manufacturing rule files
- CSV source files (400+ substances total)

### 2.1 Data Collection (1.5 hours)

**Objective:** Create comprehensive CSV files for all DEA schedules.

**Primary source:** [DEA Orange Book](https://www.deadiversion.usdoj.gov/schedules/) + [CFR Title 21 Part 1308](https://www.ecfr.gov/current/title-21/chapter-II/part-1308)

**Key insight:** DEA controls are based on **synthesis/manufacturing**, not just possession. An autonomous chemistry agent synthesizing Schedule I/II substances without registration should REFUSE.

**Files to create:**
- `data/sources/dea_schedule_i.csv` — 50+ substances (LSD, heroin, MDMA, cannabis, psilocybin)
- `data/sources/dea_schedule_ii.csv` — 80+ substances (cocaine, fentanyl, oxycodone, methamphetamine)
- `data/sources/dea_schedule_iii_v.csv` — 250+ substances (lower-risk controlled substances)

**CSV format:**
```csv
canonical_name,cas_number,dea_number,dea_schedule,molecular_formula,common_names,manufacturing_threshold_g
LSD,50-37-3,7315,I,C20H25N3O,Lysergic acid diethylamide,0.1
Heroin,561-27-3,9200,I,C21H23NO5,Diacetylmorphine;Diamorphine,1.0
Cocaine,50-36-2,9041,II,C17H21NO4,Methyl benzoylecgonine,10.0
Fentanyl,437-38-7,9801,II,C22H28N2O,N-phenyl-N-[1-(2-phenylethyl)piperidin-4-yl]propanamide,0.1
```

**Critical Schedule I substances:**
- Hallucinogens: LSD, Psilocybin, DMT, 2C-B, DOB, 25I-NBOMe
- Cannabis: Marijuana, THC, Synthetic cannabinoids (K2/Spice)
- Opioids: Heroin, Alpha-methylfentanyl, 3-Methylfentanyl
- Stimulants: MDMA, MDA, Methcathinone
- Dissociatives: PCP analogs

**Critical Schedule II substances:**
- Opioids: Fentanyl, Oxycodone, Morphine, Cocaine (also stimulant)
- Stimulants: Methamphetamine, Methylphenidate, Dextroamphetamine
- Depressants: Pentobarbital, Secobarbital

### 2.2 Generate Substance Atoms (15 minutes)

```bash
python scripts/generate_substance_atoms.py --regime dea_schedule_i
python scripts/generate_substance_atoms.py --regime dea_schedule_ii
python scripts/generate_substance_atoms.py --regime dea_schedule_iii_v
```

### 2.3 Classification Rules (1.5 hours)

**File:** `src/aegis/reasoning/rules/dea/schedule_i_rules.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% DEA Schedule I: High potential for abuse, no accepted medical use
classified(S, "dea", "schedule_i", "DEA Schedule I controlled substance") :-
    substance(S),
    schedule(S, "dea", "I").

% Schedule I synthesis requires DEA Schedule I researcher license
requires_human_review(S, "Schedule I synthesis requires DEA license under 21 CFR 1301") :-
    classified(S, "dea", "schedule_i", _).

% Any manufacture/synthesis of Schedule I without registration is illegal
proliferation_concern(S, "unlicensed_controlled_substance_manufacture") :-
    classified(S, "dea", "schedule_i", _),
    not dea_registration_verified(Researcher),
    researcher_affiliation(Researcher).

% Schedule I has manufacturing threshold (typically very low)
classified(S, "dea", "schedule_i_manufacturing", "Exceeds Schedule I manufacturing threshold") :-
    substance(S),
    schedule(S, "dea", "I"),
    quantity(S, Amount, "g"),
    manufacturing_threshold(S, Threshold, "g"),
    Amount > Threshold.

% Default ultra-low threshold for Schedule I
manufacturing_threshold(S, 1.0, "g") :-
    substance(S),
    schedule(S, "dea", "I"),
    not manufacturing_threshold(S, _, "g").
```

**File:** `src/aegis/reasoning/rules/dea/schedule_ii_rules.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% DEA Schedule II: High abuse potential, accepted medical use
classified(S, "dea", "schedule_ii", "DEA Schedule II controlled substance") :-
    substance(S),
    schedule(S, "dea", "II").

% Schedule II synthesis requires DEA registration for manufacture
classified(S, "dea", "schedule_ii_manufacturing", "Requires DEA manufacturer registration") :-
    substance(S),
    schedule(S, "dea", "II"),
    quantity(S, Amount, "g"),
    Amount > 1.0.  % Any non-trivial quantity

% Fentanyl and analogs have special restrictions (21 CFR 1308.12)
classified(S, "dea", "fentanyl_analog", "Fentanyl analog - enhanced penalties") :-
    substance(S),
    schedule(S, "dea", "II"),
    fentanyl_analog(S).

fentanyl_analog("fentanyl").
fentanyl_analog("alpha_methylfentanyl").
fentanyl_analog("3_methylfentanyl").
fentanyl_analog("acetylfentanyl").
fentanyl_analog("butyrfentanyl").
fentanyl_analog("carfentanil").

% Cross-regime check: Some DEA substances also have CWC implications
cross_regime_violation(S, ["dea_schedule_ii", "cwc_schedule_3"], "Dual-listed psychoactive chemical") :-
    classified(S, "dea", "schedule_ii", _),
    classified(S, "cwc", "schedule_3", _).
```

### 2.4 Manufacturing Threshold Rules (1 hour)

**File:** `src/aegis/reasoning/rules/dea/manufacturing_thresholds.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% Manufacturing thresholds based on 21 CFR 1309 (registration exemptions)

% Quantity thresholds for research exemptions
% Small quantities (≤30 days supply) may be exempt from full registration

research_quantity_exempt(S, MaxGrams) :-
    substance(S),
    schedule(S, "dea", Schedule),
    schedule_research_limit(Schedule, MaxGrams).

schedule_research_limit("I", 1.0).    % 1 gram max for Schedule I
schedule_research_limit("II", 5.0).   % 5 grams max for Schedule II  
schedule_research_limit("III", 50.0). % 50 grams max for Schedule III
schedule_research_limit("IV", 100.0). % 100 grams max for Schedule IV
schedule_research_limit("V", 500.0).  % 500 grams max for Schedule V

% Above research limits requires full DEA registration
requires_human_review(S, "Exceeds research exemption - requires DEA manufacturer registration") :-
    substance(S),
    schedule(S, "dea", Schedule),
    quantity(S, Amount, "g"),
    research_quantity_exempt(S, Limit),
    Amount > Limit.

% Chemical precursors to controlled substances (21 CFR 1310 - List I and List II)
% These have separate controls under the Chemical Diversion and Trafficking Act

classified(S, "dea", "list_i_precursor", "DEA List I chemical precursor") :-
    substance(S),
    list_i_chemical(S).

list_i_chemical("ephedrine").
list_i_chemical("pseudoephedrine").
list_i_chemical("phenylpropanolamine").
list_i_chemical("methylamine").
list_i_chemical("ethylamine").
list_i_chemical("propionic_anhydride").
list_i_chemical("acetic_anhydride").
list_i_chemical("anthranilic_acid").
list_i_chemical("piperidine").
list_i_chemical("safrole").
list_i_chemical("isosafrole").
list_i_chemical("piperonal").

classified(S, "dea", "list_ii_precursor", "DEA List II chemical precursor") :-
    substance(S),
    list_ii_chemical(S).

list_ii_chemical("benzyl_cyanide").
list_ii_chemical("nitroethane").
list_ii_chemical("phenylacetic_acid").
list_ii_chemical("3_4_methylenedioxyphenyl_2_propanone"). % MDP2P (MDMA precursor)

% Precursor quantity thresholds (smaller than the substances themselves)
classified(S, "dea", "precursor_threshold", "Exceeds precursor quantity threshold") :-
    substance(S),
    (list_i_chemical(S); list_ii_chemical(S)),
    quantity(S, Amount, "g"),
    precursor_threshold(S, Threshold, "g"),
    Amount > Threshold.

precursor_threshold(S, 100.0, "g") :-  % 100g threshold for most List I
    list_i_chemical(S).

precursor_threshold(S, 500.0, "g") :-  % 500g threshold for most List II
    list_ii_chemical(S).
```

### 2.5 Testing (45 minutes)

**Test key scenarios:**
- Schedule I synthesis (should REFUSE above 1g threshold)
- Schedule II legitimate research (should ESCALATE with registration requirement)
- Fentanyl analog detection (should flag enhanced penalties)  
- Precursor accumulation (methylamine + other precursors → methamphetamine synthesis pattern)

---

## TASK 3: BIS AI/Compute Controls — 4 hours

**Deliverables:**
- 2 ASP rule files (advanced compute hardware + AI model controls)
- 1 country tier classification file
- Test cases for compute thresholds and model training limits

### 3.1 Advanced Compute Hardware Controls (1.5 hours)

**Objective:** Implement ECCN 3A090 and 4A090 controls on AI compute hardware.

**Background:** October 2022/October 2023 BIS rules control advanced semiconductors based on compute density and interconnect performance. Key thresholds:
- **3A090:** Advanced computing ICs with performance density > 300 TOPS/mm² AND interconnect bandwidth > 600 GB/s
- **4A090:** Computers containing 3A090 ICs above quantity/performance thresholds

**File:** `src/aegis/reasoning/rules/ear/advanced_compute_hardware.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% ECCN 3A090 - Advanced computing integrated circuits
classified(IC, "ear", "3A090", "Advanced computing integrated circuit") :-
    component(IC),
    component_category(IC, "integrated_circuit"),
    advanced_computing_ic(IC).

% Performance density calculation: TOPS / die area
advanced_computing_ic(IC) :-
    component(IC),
    specification(IC, "peak_performance_tops", TOPS, "tops"),
    specification(IC, "die_area_mm2", Area, "mm2"),
    PerformanceDensity is TOPS / Area,
    PerformanceDensity > 300.0.  % 300 TOPS/mm²

% Alternative pathway: interconnect bandwidth threshold
advanced_computing_ic(IC) :-
    component(IC),
    specification(IC, "interconnect_bandwidth_gbps", Bandwidth, "gbps"),
    Bandwidth > 600.0.  % 600 GB/s

% Bit length restrictions for FP16/FP32 precision
advanced_computing_ic(IC) :-
    component(IC),
    specification(IC, "peak_performance_tops", TOPS, "tops"),
    specification(IC, "precision_bits", Bits, "bits"),
    TOPS > 4800.0,  % 4.8k TOPS for any precision
    Bits >= 16.      % FP16 or higher precision

% ECCN 4A090 - Computers containing advanced ICs
classified(Computer, "ear", "4A090", "Computer with advanced computing capability") :-
    system(Computer),
    system_type(Computer, "computer"),
    contains_advanced_compute_ic(Computer).

contains_advanced_compute_ic(Computer) :-
    system_contains(Computer, IC),
    classified(IC, "ear", "3A090", _).

% Aggregated compute threshold for multi-IC systems
classified(Computer, "ear", "4A090", "Computer exceeding aggregated compute threshold") :-
    system(Computer),
    system_type(Computer, "computer"),
    total_system_performance(Computer, TotalTOPS),
    TotalTOPS > 100.0.  % 100 TOPS total system performance

% Calculate total performance across all ICs in system
total_system_performance(Computer, TotalTOPS) :-
    system(Computer),
    findall(TOPS, (
        system_contains(Computer, IC),
        specification(IC, "peak_performance_tops", TOPS, "tops")
    ), TOPSList),
    sum_list(TOPSList, TotalTOPS).

% Country-specific controls (China + Russia enhanced restrictions)
classified(IC, "ear", "3A090_restricted", "Advanced IC to restricted destination") :-
    classified(IC, "ear", "3A090", _),
    destination_country(IC, Country),
    restricted_compute_destination(Country).

restricted_compute_destination("CN").  % China
restricted_compute_destination("RU").  % Russia
restricted_compute_destination("IR").  % Iran
restricted_compute_destination("KP").  % North Korea

% License requirements based on destination and performance
license_required(IC, Country) :-
    classified(IC, "ear", "3A090", _),
    destination_country(IC, Country),
    restricted_compute_destination(Country).

% Exemptions for commercial applications below threshold
dual_use_item(IC) :-
    component(IC),
    component_category(IC, "integrated_circuit"),
    specification(IC, "peak_performance_tops", TOPS, "tops"),
    TOPS =< 300.0,  % Below advanced computing threshold
    intended_end_use(IC, "commercial").
```

### 3.2 AI Model Weight Controls (1.5 hours)

**Objective:** Implement controls on frontier AI model weights based on training compute.

**Background:** Emerging controls on AI models trained with >10²⁶ FLOP (closed weight) or >10²⁵ FLOP (open weight), with additional restrictions based on model capabilities.

**File:** `src/aegis/reasoning/rules/ear/ai_model_weights.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% Frontier model controls based on training compute
classified(Model, "ear", "frontier_model", "Frontier AI model subject to controls") :-
    component(Model),
    component_category(Model, "ai_model"),
    frontier_model_threshold(Model).

frontier_model_threshold(Model) :-
    component(Model),
    specification(Model, "training_compute_flop", FLOP, "flop"),
    specification(Model, "weight_distribution", Distribution, _),
    Distribution = "closed",
    FLOP >= 1.0e26.  % 10²⁶ FLOP for closed-weight models

frontier_model_threshold(Model) :-
    component(Model),
    specification(Model, "training_compute_flop", FLOP, "flop"),
    specification(Model, "weight_distribution", Distribution, _),
    Distribution = "open",
    FLOP >= 1.0e25.  % 10²⁵ FLOP for open-weight models

% Dual-use foundation model capabilities
classified(Model, "ear", "dual_use_foundation_model", "Dual-use foundation model") :-
    component(Model),
    component_category(Model, "ai_model"),
    dual_use_ai_capability(Model).

dual_use_ai_capability(Model) :-
    component(Model),
    specification(Model, "modality", "text", _),
    specification(Model, "parameters_billion", Params, "billion"),
    Params >= 100.0.  % 100B+ parameter language models

dual_use_ai_capability(Model) :-
    component(Model),
    specification(Model, "modality", "multimodal", _),
    specification(Model, "training_compute_flop", FLOP, "flop"),
    FLOP >= 1.0e24.  % 10²⁴ FLOP for multimodal models

% Code generation capabilities (special concern)
classified(Model, "ear", "code_generation_model", "AI model with code generation capability") :-
    component(Model),
    component_category(Model, "ai_model"),
    specification(Model, "capability", "code_generation", _),
    specification(Model, "accuracy_humaneval", Accuracy, "percent"),
    Accuracy >= 80.0.  % High-accuracy code generation

% Cybersecurity-relevant capabilities
classified(Model, "ear", "cybersecurity_model", "AI model with cybersecurity capabilities") :-
    component(Model),
    component_category(Model, "ai_model"),
    cybersecurity_ai_capability(Model).

cybersecurity_ai_capability(Model) :-
    specification(Model, "capability", Capability, _),
    cybersecurity_capability(Capability).

cybersecurity_capability("vulnerability_discovery").
cybersecurity_capability("exploit_generation").
cybersecurity_capability("malware_analysis").
cybersecurity_capability("penetration_testing").
cybersecurity_capability("social_engineering").

% Red team evaluation results
requires_human_review(Model, "Failed AI safety red team evaluation") :-
    component(Model),
    component_category(Model, "ai_model"),
    specification(Model, "red_team_result", "failed", _).

requires_human_review(Model, "No red team evaluation conducted") :-
    component(Model),
    classified(Model, "ear", "frontier_model", _),
    not specification(Model, "red_team_result", _, _).

% Export restrictions based on model capability + destination
license_required(Model, Country) :-
    classified(Model, "ear", Category, _),
    string_contains(Category, "model"),
    destination_country(Model, Country),
    restricted_ai_destination(Country).

restricted_ai_destination("CN").
restricted_ai_destination("RU").
restricted_ai_destination("IR").
restricted_ai_destination("KP").

% Cross-regime check: AI models for weapons research
cross_regime_violation(Model, ["ear_ai", "usml"], "AI model for weapons research") :-
    classified(Model, "ear", ModelType, _),
    string_contains(ModelType, "model"),
    intended_end_use(Model, Use),
    (Use = "military"; Use = "weapons_research").
```

### 3.3 Country Tier Classification (1 hour)

**Objective:** Implement the AI Diffusion Framework country tier system.

**File:** `src/aegis/reasoning/rules/ear/ai_country_tiers.lp`
```prolog
#include "_common/atom_vocabulary.lp".

% AI Diffusion Framework country tier classification
% Determines compute caps and export restrictions for AI hardware

% Tier 1: Close allies with minimal restrictions
country_tier("AU", "tier_1").  % Australia
country_tier("CA", "tier_1").  % Canada  
country_tier("DK", "tier_1").  % Denmark
country_tier("FI", "tier_1").  % Finland
country_tier("FR", "tier_1").  % France
country_tier("DE", "tier_1").  % Germany
country_tier("IE", "tier_1").  % Ireland
country_tier("IT", "tier_1").  % Italy
country_tier("JP", "tier_1").  % Japan
country_tier("NL", "tier_1").  % Netherlands
country_tier("NZ", "tier_1").  % New Zealand
country_tier("NO", "tier_1").  % Norway
country_tier("KR", "tier_1").  % South Korea
country_tier("ES", "tier_1").  % Spain
country_tier("SE", "tier_1").  % Sweden
country_tier("TW", "tier_1").  % Taiwan
country_tier("GB", "tier_1").  % United Kingdom

% Tier 2: Trusted partners with moderate restrictions
country_tier("AT", "tier_2").  % Austria
country_tier("BE", "tier_2").  % Belgium
country_tier("BG", "tier_2").  % Bulgaria
country_tier("HR", "tier_2").  % Croatia
country_tier("CY", "tier_2").  % Cyprus
country_tier("CZ", "tier_2").  % Czech Republic
country_tier("EE", "tier_2").  % Estonia
country_tier("GR", "tier_2").  % Greece
country_tier("HU", "tier_2").  % Hungary
country_tier("IS", "tier_2").  % Iceland
country_tier("LV", "tier_2").  % Latvia
country_tier("LI", "tier_2").  % Liechtenstein
country_tier("LT", "tier_2").  % Lithuania
country_tier("LU", "tier_2").  % Luxembourg
country_tier("MT", "tier_2").  % Malta
country_tier("PL", "tier_2").  % Poland
country_tier("PT", "tier_2").  % Portugal
country_tier("RO", "tier_2").  % Romania
country_tier("SK", "tier_2").  % Slovakia
country_tier("SI", "tier_2").  % Slovenia
country_tier("CH", "tier_2").  % Switzerland

% Tier 3: Countries of concern with strict restrictions  
country_tier("CN", "tier_3").  % China
country_tier("RU", "tier_3").  % Russia
country_tier("IR", "tier_3").  % Iran
country_tier("KP", "tier_3").  % North Korea
country_tier("BY", "tier_3").  % Belarus

% Default tier for unlisted countries
country_tier(Country, "tier_unspecified") :-
    destination_country(_, Country),
    not country_tier(Country, "tier_1"),
    not country_tier(Country, "tier_2"),
    not country_tier(Country, "tier_3").

% Compute caps based on country tier (data center level)
compute_cap(Country, DataCenterCap) :-
    country_tier(Country, "tier_1"),
    DataCenterCap = unlimited.

compute_cap(Country, 1700) :-  % 1,700 advanced GPUs
    country_tier(Country, "tier_2").

compute_cap(Country, 50) :-    % 50 advanced GPUs
    country_tier(Country, "tier_3").

% Export license requirements based on tier + compute quantity
license_required(Hardware, Country) :-
    classified(Hardware, "ear", "3A090", _),
    destination_country(Hardware, Country),
    country_tier(Country, Tier),
    Tier \= "tier_1".

% Enhanced restrictions for Tier 3
classified(Hardware, "ear", "3A090_tier3_restricted", "Enhanced restrictions to Tier 3 country") :-
    classified(Hardware, "ear", "3A090", _),
    destination_country(Hardware, Country),
    country_tier(Country, "tier_3").
```

### 3.4 Testing (remainder)

Test compute thresholds, model capability detection, country tier restrictions.

---

## TASK 4: HHS/USDA/Australia Group Bio — 4 hours

Similar CSV → ASP pattern for biological agents. 

---

## TASK 5-7: USML Toxics, Explosives, EAR Cat 1 — 16 hours

More complex pattern logic and ECCN structure implementation.

---

## Implementation Schedule

**Week 1 (12 hours):** Tasks 1-3 (CWC + DEA + AI) — maximum demo impact  
**Week 2 (7 hours):** Task 4 (Bio agents) — completes WMD coverage  
**Week 3+ (16 hours):** Tasks 5-7 — aerospace and export control depth

Each task is independently testable and immediately valuable. After Task 3, AEGIS covers the core of chemistry, drugs, and AI compute — the highest-risk autonomous research domains.

Ready to start with Task 1 (CWC)?

