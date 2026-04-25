# AEGIS Phase 0 — Rule Foundation

**Deliverable:** Refactored directory structure + standard atom vocabulary + 
specially designed doctrine + CSV bulk loader.

**Time to integrate:** ~2 hours. **Output:** Ability to bulk-add list-based 
regimes efficiently.

---

## What's in this package

```
aegis_rule_expansion_phase0/
├── README.md                          # This file
├── src/aegis/reasoning/rules/         # New directory structure
│   └── _common/
│       ├── atom_vocabulary.lp         # Standard atoms across all regimes
│       └── specially_designed.lp     # 22 CFR 120.41 cross-cutting doctrine
├── scripts/
│   └── generate_substance_atoms.py   # CSV → ASP bulk loader
└── data/sources/                     # Placeholder for CSV files
    └── (empty — you'll populate this)
```

---

## Integration steps

### Step 1: Directory refactor (30 minutes)

The existing AEGIS rules are probably in `src/aegis/reasoning/rules/` as flat 
`.lp` files. The new structure organizes by regime:

**Before (current structure):**
```
src/aegis/reasoning/rules/
├── usml_cat_iv.lp              # EXISTING
├── mtcr.lp                     # EXISTING  
├── cwc_partial.lp              # EXISTING
└── (other files...)
```

**After (Phase 0 structure):**
```
src/aegis/reasoning/rules/
├── _common/
│   ├── atom_vocabulary.lp      # NEW — copy from package
│   └── specially_designed.lp  # NEW — copy from package  
├── usml/
│   └── cat_iv_propellants.lp   # MOVED — see Step 2
├── mtcr/
│   └── category_1.lp           # MOVED — see Step 2
├── cwc/
│   └── schedule_2.lp           # MOVED — see Step 2
├── ear/                        # NEW — empty for now
├── bwc_select_agents/         # NEW — empty for now
├── nuclear/                   # NEW — empty for now
├── dea/                       # NEW — empty for now
├── wassenaar/                 # NEW — empty for now
└── cross_regime/              # NEW — empty for now
```

**Action:**
1. Copy the package's `src/aegis/reasoning/rules/` structure into your AEGIS codebase
2. Move existing `.lp` files into appropriate subdirectories (see Step 2)
3. Update your reasoning engine to load from subdirectories

### Step 2: Migrate existing rules (45 minutes)

Your existing rule files need minor updates to use the standard atom vocabulary 
and fit the new directory structure.

#### 2a. Update existing USML Cat IV file

**Original file:** `src/aegis/reasoning/rules/usml_cat_iv.lp`  
**New location:** `src/aegis/reasoning/rules/usml/cat_iv_propellants.lp`

Add to the top of the file:
```prolog
#include "_common/atom_vocabulary.lp".
```

No other changes needed — your existing atoms should be compatible with the 
standard vocabulary.

#### 2b. Update existing MTCR file  

**Original file:** `src/aegis/reasoning/rules/mtcr.lp`  
**New location:** `src/aegis/reasoning/rules/mtcr/category_1.lp`

Add to the top:
```prolog
#include "_common/atom_vocabulary.lp".
```

#### 2c. Update existing CWC file

**Original file:** `src/aegis/reasoning/rules/cwc_partial.lp`  
**New location:** `src/aegis/reasoning/rules/cwc/schedule_2.lp`

Add to the top:
```prolog
#include "_common/atom_vocabulary.lp".
```

### Step 3: Update reasoning engine (30 minutes)

Your reasoning engine currently loads `.lp` files from a flat directory. 
Update it to load from subdirectories recursively.

**Before (pseudocode):**
```python
rule_files = glob("src/aegis/reasoning/rules/*.lp")
```

**After:**
```python
rule_files = glob("src/aegis/reasoning/rules/**/*.lp", recursive=True)
```

Make sure it loads `_common/*.lp` files first, then regime-specific files.

### Step 4: Install bulk loader (15 minutes)

Copy `scripts/generate_substance_atoms.py` to your project root. Test it:

```bash
cd your_aegis_project/
python scripts/generate_substance_atoms.py --create-samples
python scripts/generate_substance_atoms.py --validate
```

This creates sample CSV files in `data/sources/` and validates the configuration.

---

## Testing the Phase 0 foundation

After integration, test that everything still works:

```bash
# Your existing test command
python -m pytest tests/test_reasoning.py

# Or however you currently test rule loading
```

The specially designed doctrine won't activate until you have `classified(..., "usml", ..., ...)` 
atoms and `parent_system(Component, System)` facts. That comes in Phase 1.

---

## Next: Phase 1 implementation

With Phase 0 complete, you can efficiently add new regimes. Example for CWC Schedule 1:

### 1. Create CSV data file

`data/sources/cwc_schedule_1.csv`:
```csv
canonical_name,cas_number,iupac_name,molecular_formula
Sarin,107-44-8,Methylphosphonofluoridic acid,C4H10FO2P
VX,50782-69-9,Ethyl N-[2-(diisopropylamino)ethyl] methylphosphonothioate,C11H26NO2PS
Mustard gas,505-60-2,Bis(2-chloroethyl) sulfide,C4H8Cl2S
```

### 2. Generate atoms

```bash
python scripts/generate_substance_atoms.py --regime cwc_schedule_1
```

This creates `src/aegis/reasoning/rules/cwc/schedule_1_generated.lp` with:
```prolog
#include "_common/atom_vocabulary.lp".

substance("sarin").
schedule("sarin", "cwc", "1").
cas_number("sarin", "107-44-8").
molecular_formula("sarin", "C4H10FO2P").

substance("vx").
schedule("vx", "cwc", "1").
cas_number("vx", "50782-69-9").
molecular_formula("vx", "C11H26NO2PS").

% ... etc
```

### 3. Add classification rule

Create `src/aegis/reasoning/rules/cwc/schedule_1_rules.lp`:
```prolog
#include "_common/atom_vocabulary.lp".

% CWC Schedule 1 classification rule
classified(S, "cwc", "schedule_1", "Listed Schedule 1 chemical") :-
    substance(S),
    schedule(S, "cwc", "1").

% CWC Schedule 1 substances have no significant peaceful use
% Any research involving them requires OPCW declaration
proliferation_concern(S, "chemical_weapons_precursor") :-
    classified(S, "cwc", "schedule_1", _).
```

Total time to add a full regime: **~1 hour** (CSV creation + generation + rule writing).

---

## Phase 1 priority order

Based on the coverage plan, implement these regimes first:

1. **CWC Schedules 1, 2 (full), 3** — bulk load + 4 pattern rules (4 hours)
2. **DEA CSA Schedules I–V** — bulk load + 5 manufacturing thresholds (4 hours)  
3. **USML Cat XIV (toxicological)** — many overlap with CWC (3 hours)
4. **USML Cat V (explosives)** — substantial pattern logic (5 hours)
5. **EAR Cat 1 (chem/bio/microorganisms)** — bulk load + ECCN structure (8 hours)
6. **HHS + USDA Select Agents + Australia Group bio** — bulk load (4 hours)
7. **BIS AI/Compute (3A090, 4A090, model weights)** — small but novel (4 hours)

Phase 1 total: ~32 hours for complete chem/bio/AI-compute coverage.

---

## Bulk loader regime configurations

The script supports these regimes out of the box:

| Regime | CSV file | Output file |
|--------|----------|-------------|
| `cwc_schedule_1` | `data/sources/cwc_schedule_1.csv` | `cwc/schedule_1_generated.lp` |
| `cwc_schedule_2` | `data/sources/cwc_schedule_2.csv` | `cwc/schedule_2_generated.lp` |
| `cwc_schedule_3` | `data/sources/cwc_schedule_3.csv` | `cwc/schedule_3_generated.lp` |
| `dea_schedule_i` | `data/sources/dea_schedule_i.csv` | `dea/schedule_i_generated.lp` |
| `dea_schedule_ii` | `data/sources/dea_schedule_ii.csv` | `dea/schedule_ii_generated.lp` |
| `hhs_select_agents` | `data/sources/hhs_select_agents.csv` | `bwc_select_agents/hhs_select_agents_generated.lp` |
| `usda_select_agents` | `data/sources/usda_select_agents.csv` | `bwc_select_agents/usda_select_agents_generated.lp` |
| `australia_group_bio` | `data/sources/australia_group_biological.csv` | `bwc_select_agents/australia_group_bio_generated.lp` |
| `bis_entity_list` | `data/sources/bis_entity_list.csv` | `ear/bis_entity_list_generated.lp` |

To add a new regime, edit the `REGIME_CONFIGS` dictionary in the script.

---

## CSV data sources

Where to get the official lists:

- **CWC Schedules:** [OPCW website](https://www.opcw.org/chemical-weapons-convention/annexes/annex-chemicals) 
- **DEA Controlled Substances:** [DEA Orange Book](https://www.deadiversion.usdoj.gov/schedules/)
- **HHS Select Agents:** [42 CFR 73](https://www.ecfr.gov/current/title-42/chapter-I/subchapter-F/part-73)
- **USDA Select Agents:** [9 CFR 121](https://www.ecfr.gov/current/title-9/chapter-I/subchapter-D/part-121)
- **Australia Group:** [AG Guidelines](https://australiagroup.net/en/guidelines.html)
- **BIS Entity List:** [BIS website](https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list)

The bulk loader handles format variations (CSV/Excel exports, different column names) 
and normalizes everything to the standard atom vocabulary.

---

## Questions?

If you hit issues during integration:

1. **Directory structure problems:** Make sure your reasoning engine can handle 
   subdirectories and `#include` directives.

2. **Atom compatibility:** Your existing atoms should work with the standard 
   vocabulary. If not, the vocabulary can be extended.

3. **Bulk loader errors:** Run with `--validate` to check configurations, or 
   `--create-samples` to see expected CSV format.

The Phase 0 foundation supports ~915 rules across 10.5 days of implementation. 
Once in place, adding a new regime becomes mostly data import rather than 
hand-coding ASP rules.

Ready for Phase 1?
