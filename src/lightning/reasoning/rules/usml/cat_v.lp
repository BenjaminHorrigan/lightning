% ============================================================================
% USML Category V — Explosives, Energetic Materials, Propellants,
% Incendiary Agents, and Their Precursors
% Source: 22 CFR 121.1, Category V
% ============================================================================

% ============================================================================
% Category V(a) — Explosives and explosive devices
% 22 CFR 121.1 Category V(a)
% ============================================================================

category_v_a_item("shaped_charge").
category_v_a_item("demolition_charge").
category_v_a_item("demolition_block").
category_v_a_item("satchel_charge").
category_v_a_item("bangalore_torpedo").
category_v_a_item("cratering_charge").
category_v_a_item("military_explosive_device").
category_v_a_item("mine_land").
category_v_a_item("mine_naval").
category_v_a_item("mine_antitank").
category_v_a_item("mine_antipersonnel").
category_v_a_item("claymore_mine").
category_v_a_item("antipersonnel_device").

classified(C, "USML_V_a", "22 CFR 121.1 Category V(a)") :-
    component(C),
    component_category(C, Cat),
    category_v_a_item(Cat).

% ============================================================================
% Category V(b) — Military explosives (high explosives)
% 22 CFR 121.1 Category V(b)
% ============================================================================

% Named military explosive substances
military_explosive_substance("tnt").
military_explosive_substance("trinitrotoluene").
military_explosive_substance("petn").
military_explosive_substance("pentaerythritol_tetranitrate").
military_explosive_substance("tatb").
military_explosive_substance("triaminotrinitrobenzene").
military_explosive_substance("dnnc").
military_explosive_substance("hmx").
military_explosive_substance("octogen").
military_explosive_substance("rdx").
military_explosive_substance("hexogen").
military_explosive_substance("cyclonite").
military_explosive_substance("tetryl").
military_explosive_substance("composition_b").
military_explosive_substance("composition_c4").
military_explosive_substance("octol").
military_explosive_substance("pbx_explosive").
military_explosive_substance("lx_explosive").
military_explosive_substance("explosive_d").
military_explosive_substance("amatol").
military_explosive_substance("minol").
military_explosive_substance("torpex").
military_explosive_substance("tritonal").
military_explosive_substance("cl_20").
military_explosive_substance("hniw").
military_explosive_substance("dnnc_explosive").
military_explosive_substance("fox_7").
military_explosive_substance("insensitive_high_explosive").

classified(S, "USML_V_b", "22 CFR 121.1 Category V(b)") :-
    substance(S),
    military_explosive_substance(S).

% CAS-based matching to defeat name obfuscation
military_explosive_cas("118-96-7").    % TNT
military_explosive_cas("78-11-5").     % PETN
military_explosive_cas("3058-38-6").   % TATB
military_explosive_cas("2691-41-0").   % HMX
military_explosive_cas("121-82-4").    % RDX
military_explosive_cas("479-45-8").    % Tetryl
military_explosive_cas("135285-90-4").% CL-20/HNIW

classified(S, "USML_V_b", "22 CFR 121.1 Category V(b) [CAS match]") :-
    substance(S),
    cas_number(S, CAS),
    military_explosive_cas(CAS).

% ============================================================================
% Category V(c) — Detonators, initiators, and fuzes
% 22 CFR 121.1 Category V(c)
% ============================================================================

category_v_c_item("electric_detonator").
category_v_c_item("nonelectric_detonator").
category_v_c_item("blasting_cap_military").
category_v_c_item("detonating_cord").
category_v_c_item("det_cord").
category_v_c_item("primacord").
category_v_c_item("shock_tube").
category_v_c_item("initiator_explosive").
category_v_c_item("pyrotechnic_initiator").
category_v_c_item("exploding_bridgewire_detonator").
category_v_c_item("slapper_detonator").
category_v_c_item("exploding_foil_initiator").
category_v_c_item("semiconductor_bridge_initiator").
category_v_c_item("fuze_military_explosive").
category_v_c_item("safe_arm_fire_device").
category_v_c_item("electronic_safe_arm_fire").

classified(C, "USML_V_c", "22 CFR 121.1 Category V(c)") :-
    component(C),
    component_category(C, Cat),
    category_v_c_item(Cat).

% Substance-level: primary explosives used as initiating materials
primary_explosive_substance("lead_azide").
primary_explosive_substance("lead_styphnate").
primary_explosive_substance("mercury_fulminate").
primary_explosive_substance("diazodinitrophenol").
primary_explosive_substance("tetracene_initiating").
primary_explosive_substance("silver_azide").
primary_explosive_substance("copper_azide").

classified(S, "USML_V_c", "22 CFR 121.1 Category V(c)") :-
    substance(S),
    primary_explosive_substance(S).

% ============================================================================
% Category V(d) — Incendiary agents and devices
% 22 CFR 121.1 Category V(d)
% ============================================================================

category_v_d_item("thermite_military").
category_v_d_item("thermate").
category_v_d_item("napalm").
category_v_d_item("napalm_b").
category_v_d_item("white_phosphorus_munition").
category_v_d_item("incendiary_bomb").
category_v_d_item("fire_bomb").
category_v_d_item("incendiary_grenade").
category_v_d_item("magnesium_incendiary").
category_v_d_item("incendiary_device_military").

classified(C, "USML_V_d", "22 CFR 121.1 Category V(d)") :-
    component(C),
    component_category(C, Cat),
    category_v_d_item(Cat).

% Incendiary substances
incendiary_substance("white_phosphorus").
incendiary_substance("thermite").
incendiary_substance("thermate_composition").
incendiary_substance("napalm_thickener").

classified(S, "USML_V_d", "22 CFR 121.1 Category V(d)") :-
    substance(S),
    incendiary_substance(S).

% White phosphorus CAS
classified(S, "USML_V_d", "22 CFR 121.1 Category V(d) [CAS match]") :-
    substance(S),
    cas_number(S, "7723-14-0").  % white phosphorus

% ============================================================================
% Category V(e) — Military pyrotechnics and smoke agents
% 22 CFR 121.1 Category V(e)
% ============================================================================

category_v_e_item("military_flare").
category_v_e_item("illumination_flare").
category_v_e_item("infrared_flare").
category_v_e_item("tracer_element").
category_v_e_item("smoke_grenade_military").
category_v_e_item("smoke_signal_military").
category_v_e_item("colored_smoke_munition").
category_v_e_item("star_cluster_military").
category_v_e_item("trip_flare_military").
category_v_e_item("aircraft_decoy_flare").
category_v_e_item("chaff_military").
category_v_e_item("countermeasure_flare").

classified(C, "USML_V_e", "22 CFR 121.1 Category V(e)") :-
    component(C),
    component_category(C, Cat),
    category_v_e_item(Cat).

% ============================================================================
% Category V(f) — Propellant charges for Cat II weapons
% (propellants for rockets/missiles are in Cat IV; this covers artillery propellants)
% 22 CFR 121.1 Category V(f)
% ============================================================================

artillery_propellant_substance("single_base_powder").
artillery_propellant_substance("double_base_powder").
artillery_propellant_substance("triple_base_powder").
artillery_propellant_substance("artillery_propellant_charge").
artillery_propellant_substance("gun_propellant_military").

classified(S, "USML_V_f", "22 CFR 121.1 Category V(f)") :-
    substance(S),
    artillery_propellant_substance(S).

classified(C, "USML_V_f", "22 CFR 121.1 Category V(f)") :-
    component(C),
    component_category(C, "propellant_charge_artillery").

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
