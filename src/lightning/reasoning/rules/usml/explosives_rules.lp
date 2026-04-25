% =============================================================================
% USML Explosives Classification Rules
% Source: 22 CFR 121.1 Categories IV and V (ITAR)
% =============================================================================
% Classifies military explosives, warheads, and explosive devices under
% USML Categories IV and V export controls

% Core USML explosives classification
classified(S, "usml", "cat_iv_explosive", "USML Category IV - Military Explosive") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    usml_category(S, "IV"),
    item_type(S, "explosive").

classified(S, "usml", "cat_v_warhead", "USML Category V - Warhead System") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    usml_category(S, "V"),
    item_type(S, "warhead").

% Explosive type classifications
classified(S, "usml", "secondary_explosive", "Secondary Military Explosive") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    explosive_type(S, "secondary").

classified(S, "usml", "system_level_explosive", "System-Level Explosive Device") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    explosive_type(S, "system").

% Sensitivity-based classifications
classified(S, "usml", "high_sensitivity_explosive", "High Sensitivity Explosive") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    (sensitivity(S, "high"); sensitivity(S, "very_high")).

classified(S, "usml", "insensitive_munition", "Insensitive Munition Explosive") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    (sensitivity(S, "low"); sensitivity(S, "very_low")).

% Advanced explosive classifications
classified(S, "usml", "advanced_explosive", "Advanced Military Explosive") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    (canonical_name(S, "tatb"); canonical_name(S, "cl_20"); canonical_name(S, "hmx")).

classified(S, "usml", "plastic_explosive", "Military Plastic Explosive") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    (canonical_name(S, "c4_explosive"); canonical_name(S, "semtex");
     canonical_name(S, "pbxn_109"); canonical_name(S, "pbxn_5")).

% Warhead type classifications
classified(S, "usml", "shaped_charge_warhead", "Shaped Charge Warhead") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    explosive_type(S, "shaped_charge").

classified(S, "usml", "blast_fragmentation_warhead", "Blast-Fragmentation Warhead") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    explosive_type(S, "blast_frag").

classified(S, "usml", "penetrator_warhead", "Penetrator Warhead") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    explosive_type(S, "penetrator").

classified(S, "usml", "cluster_munition", "Cluster Munition Warhead") :-
    substance(S),
    schedule(S, "usml_explosives", "controlled"),
    explosive_type(S, "submunition").

% Proliferation concerns
proliferation_concern(S, "improvised_explosive_device") :-
    classified(S, "usml", "plastic_explosive", _).

proliferation_concern(S, "advanced_warhead_technology") :-
    classified(S, "usml", "cat_v_warhead", _).

proliferation_concern(S, "high_performance_explosive") :-
    classified(S, "usml", "advanced_explosive", _).

proliferation_concern(S, "anti_armor_capability") :-
    classified(S, "usml", "shaped_charge_warhead", _).

proliferation_concern(S, "area_denial_weapon") :-
    classified(S, "usml", "cluster_munition", _).

% Human review requirements
requires_human_review(S, "Category IV explosive requires State Department munitions license") :-
    classified(S, "usml", "cat_iv_explosive", _).

requires_human_review(S, "Category V warhead requires State Department munitions license") :-
    classified(S, "usml", "cat_v_warhead", _).

requires_human_review(S, "Advanced explosive technology requires enhanced security review") :-
    classified(S, "usml", "advanced_explosive", _).

requires_human_review(S, "Military plastic explosive requires terrorism risk assessment") :-
    classified(S, "usml", "plastic_explosive", _).

requires_human_review(S, "Cluster munition warhead requires humanitarian law review") :-
    classified(S, "usml", "cluster_munition", _).