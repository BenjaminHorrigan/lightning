% ============================================================================
% Australia Group Nuclear Trigger List / NSG Part 1 (Trigger List)
% Source: Nuclear Suppliers Group (NSG) Guidelines, Part 1
%         Australia Group Guidelines (nuclear convergence items)
% ============================================================================
%
% The NSG Trigger List (INFCIRC/254/Part 1) identifies items requiring IAEA
% safeguards agreements as a condition of supply. The Australia Group aligns
% its nuclear export controls with NSG Part 1.
%
% Key reference: NSG Guidelines for Nuclear Transfers (INFCIRC/254/Rev.15/Part 1)
% ============================================================================

% ============================================================================
% NSG Part 1, Item 1 — Nuclear reactors and equipment
% ============================================================================

nsg_trigger_reactor("nuclear_reactor_complete").
nsg_trigger_reactor("reactor_pressure_vessel").
nsg_trigger_reactor("reactor_fuel_handling_machine").
nsg_trigger_reactor("reactor_control_rod_system").
nsg_trigger_reactor("reactor_coolant_pump_primary").
nsg_trigger_reactor("zircaloy_tube").
nsg_trigger_reactor("zirconium_alloy_tube").

classified(C, "NSG_Trigger_Item1", "NSG INFCIRC/254/Rev.15/Part 1, Item 1") :-
    component(C),
    component_category(C, Cat),
    nsg_trigger_reactor(Cat).

% Zirconium as structural material for fuel cladding
classified(S, "NSG_Trigger_Item1", "NSG INFCIRC/254/Rev.15/Part 1, Item 1") :-
    substance(S),
    attribute(S, "nuclear_grade_zirconium").

% ============================================================================
% NSG Part 1, Item 2 — Non-nuclear materials for reactors
% ============================================================================

nsg_nonnuclear_material("heavy_water_reactor_grade").
nsg_nonnuclear_material("deuterium_reactor_grade").
nsg_nonnuclear_material("nuclear_grade_graphite").
nsg_nonnuclear_material("reactor_grade_beryllium").

classified(S, "NSG_Trigger_Item2", "NSG INFCIRC/254/Rev.15/Part 1, Item 2") :-
    substance(S),
    nsg_nonnuclear_material(S).

classified(S, "NSG_Trigger_Item2", "NSG INFCIRC/254/Rev.15/Part 1, Item 2") :-
    substance(S),
    attribute(S, "reactor_moderator_material").

% ============================================================================
% NSG Part 1, Item 3 — Plants for reprocessing irradiated fuel elements
% ============================================================================

nsg_reprocessing_item("reprocessing_plant").
nsg_reprocessing_item("hot_cell_facility").
nsg_reprocessing_item("dissolution_vessel_nuclear").
nsg_reprocessing_item("solvent_extraction_system_nuclear").

classified(C, "NSG_Trigger_Item3", "NSG INFCIRC/254/Rev.15/Part 1, Item 3") :-
    component(C),
    component_category(C, Cat),
    nsg_reprocessing_item(Cat).

% ============================================================================
% NSG Part 1, Item 4 — Plants for fabricating nuclear fuel elements
% ============================================================================

nsg_fuel_fab_item("fuel_fabrication_plant").
nsg_fuel_fab_item("sintering_furnace_uo2").
nsg_fuel_fab_item("pellet_press_nuclear").
nsg_fuel_fab_item("fuel_rod_welding_equipment").

classified(C, "NSG_Trigger_Item4", "NSG INFCIRC/254/Rev.15/Part 1, Item 4") :-
    component(C),
    component_category(C, Cat),
    nsg_fuel_fab_item(Cat).

% ============================================================================
% NSG Part 1, Item 5 — Uranium enrichment plants and equipment
% ============================================================================

nsg_enrichment_item("enrichment_plant_complete").
nsg_enrichment_item("gas_centrifuge_enrichment").
nsg_enrichment_item("gaseous_diffusion_plant").
nsg_enrichment_item("laser_isotope_separation_plant").
nsg_enrichment_item("aerodynamic_enrichment_plant").

classified(C, "NSG_Trigger_Item5", "NSG INFCIRC/254/Rev.15/Part 1, Item 5") :-
    component(C),
    component_category(C, Cat),
    nsg_enrichment_item(Cat).

% ============================================================================
% NSG Part 1, Item 6 — Source material: uranium, thorium
% ============================================================================

classified(S, "NSG_Trigger_Item6", "NSG INFCIRC/254/Rev.15/Part 1, Item 6") :-
    substance(S),
    nsg_source_material(S).

nsg_source_material("uranium_ore").
nsg_source_material("uranium_ore_concentrate").
nsg_source_material("uo2").
nsg_source_material("uf4").
nsg_source_material("uf6").
nsg_source_material("natural_uranium_metal").
nsg_source_material("thorium_ore").
nsg_source_material("thorium_metal").
nsg_source_material("thorium_nitrate").

% UO2 CAS
classified(S, "NSG_Trigger_Item6", "NSG INFCIRC/254/Rev.15/Part 1, Item 6 [CAS match]") :-
    substance(S),
    cas_number(S, "1344-57-6").  % UO2 (uranium dioxide)

% ============================================================================
% NSG Part 1, Item 7 — Special fissionable material
% Enriched uranium, Pu-239, U-233
% ============================================================================

classified(S, "NSG_Trigger_Item7_HEU", "NSG INFCIRC/254/Rev.15/Part 1, Item 7") :-
    substance(S),
    attribute(S, "highly_enriched_uranium").

classified(S, "NSG_Trigger_Item7_HEU", "NSG INFCIRC/254/Rev.15/Part 1, Item 7") :-
    substance(S),
    attribute(S, "enriched_uranium"),
    performance(S, "enrichment_pct", Enr),
    Enr >= 20.

classified(S, "NSG_Trigger_Item7_Pu", "NSG INFCIRC/254/Rev.15/Part 1, Item 7") :-
    substance(S),
    substance_is_pu239_nsg(S).

substance_is_pu239_nsg("plutonium_239").
substance_is_pu239_nsg("reactor_grade_plutonium").
substance_is_pu239_nsg("weapons_grade_plutonium").

classified(S, "NSG_Trigger_Item7_U233", "NSG INFCIRC/254/Rev.15/Part 1, Item 7") :-
    substance(S),
    substance_is_u233_nsg(S).

substance_is_u233_nsg("uranium_233").
substance_is_u233_nsg("u_233").

% ============================================================================
% Australia Group — nuclear convergence: isotope separation equipment
% (items dual-listed with NSG Part 2 and AG guidelines)
% ============================================================================

ag_nuclear_dual_use("mass_spectrometer_pu_analysis").
ag_nuclear_dual_use("isotope_ratio_mass_spectrometer_nuclear").
ag_nuclear_dual_use("alpha_spectrometer_nuclear").

classified(C, "AG_Nuclear_Dual_Use", "AG Nuclear-related Dual-Use Equipment Guidelines") :-
    component(C),
    component_category(C, Cat),
    ag_nuclear_dual_use(Cat).

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
