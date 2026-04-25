% =============================================================================
% USML Category XIV Toxics Classification Rules
% Source: 22 CFR 121.1 Category XIV (ITAR)
% =============================================================================
% Classifies toxic chemical agents, biological toxins, and associated equipment
% under USML Category XIV export controls

% Core USML Category XIV classification
classified(S, "usml", "cat_xiv_toxic", "USML Category XIV - Toxic Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    usml_category(S, "XIV").

% Control level classifications
classified(S, "usml", "cat_xiv_prohibited", "USML Category XIV - Prohibited Toxic Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    control_level(S, "prohibited").

classified(S, "usml", "cat_xiv_controlled", "USML Category XIV - Controlled Toxic Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    control_level(S, "controlled").

% Agent type classifications
classified(S, "usml", "chemical_warfare_agent", "Chemical Warfare Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    item_type(S, "chemical_agent"),
    control_level(S, "prohibited").

classified(S, "usml", "biological_toxin_weapon", "Biological Toxin Weapon Material") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    item_type(S, "biological_toxin").

classified(S, "usml", "riot_control_agent", "Riot Control Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    (lethal_dose(S, "riot_control_agent"); lethal_dose(S, "incapacitating_agent")).

% Lethality-based classifications
classified(S, "usml", "extremely_lethal_agent", "Extremely Lethal Toxic Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    lethal_dose(S, LD),
    (LD = "LD50_0.001mg_per_kg"; LD = "LD50_0.01mg_per_kg").

classified(S, "usml", "highly_lethal_agent", "Highly Lethal Toxic Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    lethal_dose(S, LD),
    (LD = "LD50_0.05mg_per_kg"; LD = "LD50_0.1mg_per_kg").

% Nerve agent classifications
classified(S, "usml", "nerve_agent", "Nerve Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    (canonical_name(S, "sarin"); canonical_name(S, "soman"); canonical_name(S, "tabun"); canonical_name(S, "vx")).

classified(S, "usml", "novichok_agent", "Novichok Nerve Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    (canonical_name(S, "novichok_a_230"); canonical_name(S, "novichok_a_232")).

% Blister agent classifications
classified(S, "usml", "blister_agent", "Blister Agent") :-
    substance(S),
    schedule(S, "usml_cat_xiv", "controlled"),
    (canonical_name(S, "mustard_gas"); canonical_name(S, "nitrogen_mustard");
     canonical_name(S, "lewisite_1"); canonical_name(S, "lewisite_2"); canonical_name(S, "lewisite_3")).

% Proliferation concerns
proliferation_concern(S, "chemical_weapons_program") :-
    classified(S, "usml", "chemical_warfare_agent", _).

proliferation_concern(S, "biological_weapons_program") :-
    classified(S, "usml", "biological_toxin_weapon", _).

proliferation_concern(S, "advanced_nerve_agent") :-
    classified(S, "usml", "novichok_agent", _).

proliferation_concern(S, "weapons_of_mass_destruction") :-
    classified(S, "usml", "extremely_lethal_agent", _).

% Human review requirements
requires_human_review(S, "Category XIV prohibited agent requires State Department license") :-
    classified(S, "usml", "cat_xiv_prohibited", _).

requires_human_review(S, "Chemical warfare agent requires enhanced security review") :-
    classified(S, "usml", "chemical_warfare_agent", _).

requires_human_review(S, "Novichok agent requires national security consultation") :-
    classified(S, "usml", "novichok_agent", _).

requires_human_review(S, "Biological toxin weapon material requires dual-use assessment") :-
    classified(S, "usml", "biological_toxin_weapon", _).

requires_human_review(S, "Extremely lethal agent requires WMD proliferation review") :-
    classified(S, "usml", "extremely_lethal_agent", _).