% ============================================================================
% NRC 10 CFR 110 — Nuclear Export Controls
% Source: 10 CFR Part 110 (NRC import/export), 10 CFR Part 50 (reactor licensing)
% ============================================================================

% ============================================================================
% Special Nuclear Material (SNM) — 10 CFR 110.8, 10 CFR 110.10
% Enriched uranium, plutonium, uranium-233
% ============================================================================

% Highly enriched uranium (HEU): U-235 enrichment >= 20%
% Performance fact: enrichment_percent as integer
classified(S, "NRC_SNM_HEU", "10 CFR 110.8; 10 CFR 110.10(a)") :-
    substance(S),
    attribute(S, "enriched_uranium"),
    performance(S, "enrichment_pct", Enr),
    Enr >= 20.

classified(S, "NRC_SNM_HEU", "10 CFR 110.8; 10 CFR 110.10(a)") :-
    substance(S),
    attribute(S, "highly_enriched_uranium").

% Plutonium-239
classified(S, "NRC_SNM_Pu239", "10 CFR 110.8; 10 CFR 110.10(b)") :-
    substance(S),
    substance_is_pu239(S).

substance_is_pu239("plutonium_239").
substance_is_pu239("pu_239").
substance_is_pu239("weapons_grade_plutonium").

classified(S, "NRC_SNM_Pu239", "10 CFR 110.8; 10 CFR 110.10(b)") :-
    substance(S),
    cas_number(S, "15117-48-3").  % Pu-239

% Uranium-233
classified(S, "NRC_SNM_U233", "10 CFR 110.8; 10 CFR 110.10(c)") :-
    substance(S),
    substance_is_u233(S).

substance_is_u233("uranium_233").
substance_is_u233("u_233").

% Low enriched uranium (LEU) for reactors: 0.7–20% U-235
% Also controlled but under different license category (general license threshold)
classified(S, "NRC_SNM_LEU", "10 CFR 110.27") :-
    substance(S),
    attribute(S, "enriched_uranium"),
    performance(S, "enrichment_pct", Enr),
    Enr >= 1,
    Enr < 20.

% Source material: natural/depleted uranium, thorium
classified(S, "NRC_source_material", "10 CFR 110.8(z)") :-
    substance(S),
    source_material_substance(S).

source_material_substance("natural_uranium").
source_material_substance("depleted_uranium").
source_material_substance("thorium").
source_material_substance("uranium_ore_concentrate").
source_material_substance("yellowcake").

% ============================================================================
% Nuclear reactors and major components — 10 CFR 110.9
% ============================================================================

nuclear_reactor_component("nuclear_reactor").
nuclear_reactor_component("research_reactor").
nuclear_reactor_component("power_reactor").
nuclear_reactor_component("reactor_pressure_vessel").
nuclear_reactor_component("reactor_core").
nuclear_reactor_component("reactor_control_rod").
nuclear_reactor_component("control_rod_assembly").
nuclear_reactor_component("reactor_fuel_assembly").
nuclear_reactor_component("nuclear_fuel_element").
nuclear_reactor_component("reactor_coolant_pump").
nuclear_reactor_component("pressurizer").
nuclear_reactor_component("steam_generator_nuclear").
nuclear_reactor_component("reactor_containment_vessel").
nuclear_reactor_component("reactor_vessel_head").
nuclear_reactor_component("neutron_reflector").
nuclear_reactor_component("moderator_material").
nuclear_reactor_component("nuclear_instrumentation_system").

classified(C, "NRC_reactor_component", "10 CFR 110.9(a)") :-
    component(C),
    component_category(C, Cat),
    nuclear_reactor_component(Cat).

% ============================================================================
% Uranium enrichment equipment — 10 CFR 110, Appendix A
% ============================================================================

enrichment_equipment("gas_centrifuge").
enrichment_equipment("centrifuge_rotor").
enrichment_equipment("centrifuge_bearing").
enrichment_equipment("centrifuge_cascade").
enrichment_equipment("gaseous_diffusion_barrier").
enrichment_equipment("diffusion_barrier_membrane").
enrichment_equipment("laser_enrichment_equipment").
enrichment_equipment("atomic_vapor_laser_isotope_separation").
enrichment_equipment("avlis_equipment").
enrichment_equipment("molecular_laser_isotope_separation").
enrichment_equipment("mlis_equipment").
enrichment_equipment("electromagnetic_separation_calutron").
enrichment_equipment("calutron").
enrichment_equipment("aerodynamic_enrichment_nozzle").
enrichment_equipment("vortex_tube_enrichment").
enrichment_equipment("uf6_handling_equipment").
enrichment_equipment("uranium_hexafluoride_handling").

classified(C, "NRC_enrichment_equipment", "10 CFR 110, Appendix A Part 1") :-
    component(C),
    component_category(C, Cat),
    enrichment_equipment(Cat).

% UF6 as a substance
classified(S, "NRC_enrichment_material", "10 CFR 110, Appendix A Part 2") :-
    substance(S),
    enrichment_chemical_substance(S).

enrichment_chemical_substance("uranium_hexafluoride").
enrichment_chemical_substance("uf6").

classified(S, "NRC_enrichment_material", "10 CFR 110, Appendix A Part 2") :-
    substance(S),
    cas_number(S, "7783-81-5").  % UF6

% ============================================================================
% Plutonium reprocessing — PUREX process and related equipment
% 10 CFR 110.9(e)
% ============================================================================

reprocessing_equipment("purex_extraction_column").
reprocessing_equipment("mixer_settler_reprocessing").
reprocessing_equipment("pulsed_column_reprocessing").
reprocessing_equipment("hot_cell_reprocessing").
reprocessing_equipment("fuel_chopping_machine").
reprocessing_equipment("fuel_dissolution_vessel").
reprocessing_equipment("solvent_extraction_centrifuge").
reprocessing_equipment("plutonium_conversion_system").
reprocessing_equipment("high_level_waste_vitrification").
reprocessing_equipment("reprocessing_plant_system").

classified(C, "NRC_reprocessing_equipment", "10 CFR 110.9(e)") :-
    component(C),
    component_category(C, Cat),
    reprocessing_equipment(Cat).

% PUREX chemicals
reprocessing_chemical_substance("tributyl_phosphate").
reprocessing_chemical_substance("tbp").
reprocessing_chemical_substance("diluent_odorless_kerosene").
reprocessing_chemical_substance("hydroxylamine_nitrate").

classified(S, "NRC_reprocessing_chemical", "10 CFR 110.9(e)") :-
    substance(S),
    reprocessing_chemical_substance(S).

% TBP CAS
classified(S, "NRC_reprocessing_chemical", "10 CFR 110.9(e) [CAS match]") :-
    substance(S),
    cas_number(S, "126-73-8").  % tributyl phosphate (TBP)

% ============================================================================
% Heavy water and production equipment — 10 CFR 110.10(d)
% ============================================================================

classified(S, "NRC_heavy_water", "10 CFR 110.10(d)") :-
    substance(S),
    heavy_water_substance(S).

heavy_water_substance("heavy_water").
heavy_water_substance("deuterium_oxide").
heavy_water_substance("d2o").

classified(S, "NRC_heavy_water", "10 CFR 110.10(d) [CAS match]") :-
    substance(S),
    cas_number(S, "7789-20-0").  % D2O

heavy_water_production_equipment("girdler_sulfide_plant").
heavy_water_production_equipment("girdler_sulfide_tower").
heavy_water_production_equipment("h2s_deuterium_exchange").
heavy_water_production_equipment("bithermal_exchange_column").
heavy_water_production_equipment("heavy_water_distillation_column").

classified(C, "NRC_heavy_water_equipment", "10 CFR 110, Appendix A Part 3") :-
    component(C),
    component_category(C, Cat),
    heavy_water_production_equipment(Cat).

% ============================================================================
% Nuclear weapons-related components — 10 CFR 110.8
% These are items whose sole plausible use is weapons
% ============================================================================

nuclear_weapon_component("implosion_lens").
nuclear_weapon_component("explosive_lens_nuclear").
nuclear_weapon_component("nuclear_initiator").
nuclear_weapon_component("polonium_initiator").
nuclear_weapon_component("neutron_initiator").
nuclear_weapon_component("pit_nuclear").
nuclear_weapon_component("reentry_vehicle_nuclear").
nuclear_weapon_component("nuclear_reflector").
nuclear_weapon_component("beryllium_reflector").
nuclear_weapon_component("uranium_reflector").
nuclear_weapon_component("nuclear_weapon_case").
nuclear_weapon_component("bomb_assembly_nuclear").

classified(C, "NRC_weapons_component", "10 CFR 110.8; 10 CFR 110.9") :-
    component(C),
    component_category(C, Cat),
    nuclear_weapon_component(Cat).

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
