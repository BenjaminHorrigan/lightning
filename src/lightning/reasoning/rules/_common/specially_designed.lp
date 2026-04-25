% =============================================================================
% USML "Specially Designed" Doctrine — 22 CFR 120.41
% =============================================================================
% Implements the cross-cutting "specially designed" definition that applies
% across all 21 USML categories. This is the backbone of ITAR classification:
% parts, components, accessories, and attachments "specially designed" for
% USML-controlled articles are themselves USML-controlled, UNLESS a release
% paragraph applies.
%
% See 22 CFR 120.41 for the full definition and five release paragraphs.
% =============================================================================

#include "_common/atom_vocabulary.lp".

% -----------------------------------------------------------------------------
% § SPECIALLY DESIGNED DEFINITION (22 CFR 120.41)
% -----------------------------------------------------------------------------

% Core specially designed rule
% If a component has an USML-controlled article as its parent system,
% and no release paragraph applies, then the component is specially designed
specially_designed(Component) :-
    component(Component),
    parent_system(Component, System),
    classified(System, "usml", _, _),
    not release_paragraph_applies(Component, _).

% Alternative specially designed triggers
% Directly enumerated as specially designed in USML category
specially_designed(Component) :-
    component(Component),
    enumerated_as_specially_designed(Component, _).

% Has unique design features for controlled end item
specially_designed(Component) :-
    component(Component),
    unique_design_feature_for_controlled_item(Component, ControlledItem),
    classified(ControlledItem, "usml", _, _).

% Developed primarily for controlled application
specially_designed(Component) :-
    component(Component),
    developed_primarily_for(Component, Application),
    controlled_application(Application).

% -----------------------------------------------------------------------------
% § RELEASE PARAGRAPH (b)(1) — FORM, FIT, FUNCTION EQUIVALENT
% -----------------------------------------------------------------------------

% 22 CFR 120.41(b)(1): "The item has the same form, fit, and function as a
% commodity or software used in a civil application and is not produced or
% developed with knowledge that it would be used in a defense article."

% [DISABLED — needs ASP reformulation] release_paragraph_applies(Component, "b1_form_fit_function") :-
% [DISABLED — needs ASP reformulation]     component(Component),
% [DISABLED — needs ASP reformulation]     parent_system(Component, MilitarySystem),
% [DISABLED — needs ASP reformulation]     classified(MilitarySystem, "usml", _, _),
    
    % Has equivalent civilian component with same form/fit/function
% [DISABLED — needs ASP reformulation]     equivalent_civilian_component(Component, CivilianComponent),
% [DISABLED — needs ASP reformulation]     same_form_fit_function(Component, CivilianComponent),
    
    % Not produced with knowledge of defense use
% [DISABLED — needs ASP reformulation]     not produced_with_defense_knowledge(Component).

% Helper predicates for (b)(1) analysis
% [DISABLED — needs ASP reformulation] same_form_fit_function(Comp1, Comp2) :-
% [DISABLED — needs ASP reformulation]     component(Comp1), component(Comp2),
% [DISABLED — needs ASP reformulation]     same_form(Comp1, Comp2),
% [DISABLED — needs ASP reformulation]     same_fit(Comp1, Comp2),
% [DISABLED — needs ASP reformulation]     same_function(Comp1, Comp2).

% Form equivalence (physical characteristics)
% [DISABLED — needs ASP reformulation] same_form(Comp1, Comp2) :-
% [DISABLED — needs ASP reformulation]     specification(Comp1, "length_mm", L, "mm"),
% [DISABLED — needs ASP reformulation]     specification(Comp2, "length_mm", L2, "mm"),
% [DISABLED — needs ASP reformulation]     abs(L - L2) <= L * 0.05,  % within 5% tolerance
    
% [DISABLED — needs ASP reformulation]     specification(Comp1, "diameter_mm", D, "mm"),
% [DISABLED — needs ASP reformulation]     specification(Comp2, "diameter_mm", D2, "mm"),
% [DISABLED — needs ASP reformulation]     abs(D - D2) <= D * 0.05,
    
% [DISABLED — needs ASP reformulation]     material(Comp1, Material1),
% [DISABLED — needs ASP reformulation]     material(Comp2, Material2),
% [DISABLED — needs ASP reformulation]     equivalent_materials(Material1, Material2).

% Fit equivalence (interfaces and mounting)
% [DISABLED — needs ASP reformulation] same_fit(Comp1, Comp2) :-
% [DISABLED — needs ASP reformulation]     specification(Comp1, "interface_type", Interface, _),
% [DISABLED — needs ASP reformulation]     specification(Comp2, "interface_type", Interface, _),
    
% [DISABLED — needs ASP reformulation]     specification(Comp1, "mounting_pattern", Pattern, _),
% [DISABLED — needs ASP reformulation]     specification(Comp2, "mounting_pattern", Pattern, _).

% Function equivalence (performance characteristics)
% [DISABLED — needs ASP reformulation] same_function(Comp1, Comp2) :-
% [DISABLED — needs ASP reformulation]     specification(Comp1, "power_w", P1, "w"),
% [DISABLED — needs ASP reformulation]     specification(Comp2, "power_w", P2, "w"),
% [DISABLED — needs ASP reformulation]     abs(P1 - P2) <= P1 * 0.10,  % within 10% performance
    
% [DISABLED — needs ASP reformulation]     component_category(Comp1, Category),
% [DISABLED — needs ASP reformulation]     component_category(Comp2, Category).

% -----------------------------------------------------------------------------
% § RELEASE PARAGRAPH (b)(2) — SAFETY AND ENVIRONMENTAL PROTECTION
% -----------------------------------------------------------------------------

% 22 CFR 120.41(b)(2): Items whose control would not contribute to maintaining
% the quality of a U.S. defense article or furnish a military capability

_safety_or_env(Component) :- safety_critical_component(Component).
_safety_or_env(Component) :- environmental_protection_component(Component).

release_paragraph_applies(Component, "b2_safety_environmental") :-
    component(Component),
    parent_system(Component, _),
    _safety_or_env(Component),
    not affects_military_performance(Component).

% Safety components
safety_critical_component(Component) :-
    component_category(Component, Category),
    safety_category(Category).

safety_category("fire_suppression").
safety_category("emergency_shutdown").
safety_category("pressure_relief").
safety_category("safety_interlock").
safety_category("personnel_protection").

% Environmental protection components
environmental_protection_component(Component) :-
    component_category(Component, Category),
    environmental_category(Category).

environmental_category("emissions_control").
environmental_category("noise_suppression").
environmental_category("waste_treatment").
environmental_category("spill_containment").

% -----------------------------------------------------------------------------
% § RELEASE PARAGRAPH (b)(3) — FASTENERS
% -----------------------------------------------------------------------------

% 22 CFR 120.41(b)(3): Standard fasteners

release_paragraph_applies(Component, "b3_standard_fastener") :-
    component(Component),
    component_category(Component, "fastener"),
    standard_fastener(Component).

standard_fastener(Component) :-
    component_category(Component, "fastener"),
    specification(Component, "standard", Standard, _),
    commercial_fastener_standard(Standard).

% Commercial fastener standards
commercial_fastener_standard("iso_4762").    % Socket head cap screws
commercial_fastener_standard("iso_7380").    % Button head screws  
commercial_fastener_standard("din_912").     % Socket head cap screws
commercial_fastener_standard("asme_b18").    % ASME fastener standards
commercial_fastener_standard("astm_f835").   % Alloy steel socket screws

% -----------------------------------------------------------------------------
% § RELEASE PARAGRAPH (b)(4) — FORGINGS, CASTINGS, OTHER PRODUCTS
% -----------------------------------------------------------------------------

% 22 CFR 120.41(b)(4): Forgings, castings, and other unfinished products
% requiring extensive additional manufacturing

release_paragraph_applies(Component, "b4_unfinished_product") :-
    component(Component),
    unfinished_product(Component),
    requires_extensive_manufacturing(Component).

unfinished_product(Component) :-
    component_subcategory(Component, "forging").

unfinished_product(Component) :-
    component_subcategory(Component, "casting").

unfinished_product(Component) :-
    component_subcategory(Component, "billet").

unfinished_product(Component) :-
    component_subcategory(Component, "plate").

requires_extensive_manufacturing(Component) :-
    manufacturing_operations_required(Component, Operations),
    Operations >= 5.  % Arbitrary threshold - needs domain expertise

% -----------------------------------------------------------------------------
% § RELEASE PARAGRAPH (b)(5) — GENERAL PURPOSE ITEMS
% -----------------------------------------------------------------------------

% 22 CFR 120.41(b)(5): General purpose items, materials, or software

release_paragraph_applies(Component, "b5_general_purpose") :-
    component(Component),
    general_purpose_item(Component).

general_purpose_item(Component) :-
    component_category(Component, Category),
    general_purpose_category(Category).

% Categories considered general purpose
general_purpose_category("wire").
general_purpose_category("cable_standard").
general_purpose_category("connector_commercial").
general_purpose_category("resistor").
general_purpose_category("capacitor").
general_purpose_category("inductor").
general_purpose_category("bearing_commercial").
general_purpose_category("seal_standard").
general_purpose_category("gasket").
general_purpose_category("lubricant_commercial").
general_purpose_category("adhesive_commercial").

% Software categories
general_purpose_category("commercial_software").
general_purpose_category("open_source_software").
general_purpose_category("operating_system").

% Materials
general_purpose_category("aluminum_alloy_commercial").
general_purpose_category("steel_commercial").
general_purpose_category("plastic_commercial").

% Exclusions from general purpose - these remain specially designed
general_purpose_item(Component) :-
    component_category(Component, Category),
    general_purpose_category(Category),
    not general_purpose_exclusion(Component).

% Items that look general purpose but aren't
general_purpose_exclusion(Component) :-
    component_category(Component, "wire"),
    specification(Component, "temperature_rating", Temp, "celsius"),
    Temp > 200.  % High-temp wire for military applications

general_purpose_exclusion(Component) :-
    component_category(Component, Category),
    general_purpose_category(Category),
    hardened_for_military(Component).

% -----------------------------------------------------------------------------
% § SUPPORTING PREDICATES
% -----------------------------------------------------------------------------

% Define controlled applications that trigger specially designed classification
controlled_application("missile_guidance").
controlled_application("nuclear_weapons").
controlled_application("chemical_weapons").
controlled_application("military_communications").
controlled_application("electronic_warfare").
controlled_application("military_propulsion").
controlled_application("military_targeting").

% Military hardening characteristics
hardened_for_military(Component) :-
    specification(Component, "temperature_range", Range, "celsius"),
    military_temperature_range(Range).

hardened_for_military(Component) :-
    specification(Component, "shock_resistance", Shock, "g"),
    Shock > 50.

hardened_for_military(Component) :-
    specification(Component, "radiation_tolerance", Dose, "rad"),
    Dose > 1000.

military_temperature_range(Range) :-
    Range = "-55_to_125".  % MIL-STD-810 typical range

% Material equivalence for form/fit/function analysis
equivalent_materials("aluminum_6061", "aluminum_2024").
equivalent_materials("steel_4140", "steel_4340").
equivalent_materials("stainless_316", "stainless_304").
equivalent_materials("titanium_6al4v", "titanium_commercially_pure").

% Production knowledge indicators (negation of (b)(1) defense knowledge requirement)
produced_with_defense_knowledge(Component) :-
    manufacturer(Component, Company),
    defense_contractor(Company).

produced_with_defense_knowledge(Component) :-
    part_number(Component, PartNumber),
    military_part_number_pattern(PartNumber).

defense_contractor("lockheed_martin").
defense_contractor("boeing_defense").
defense_contractor("raytheon").
defense_contractor("general_dynamics").
defense_contractor("northrop_grumman").

% military_part_number_pattern(PartNumber) :- string_prefix(PartNumber, "mil-").

% military_part_number_pattern(PartNumber) :- string_prefix(PartNumber, "ms-").

% military_part_number_pattern(PartNumber) :- string_prefix(PartNumber, "nas-").

% -----------------------------------------------------------------------------
% § CLASSIFICATION INHERITANCE
% -----------------------------------------------------------------------------

% If a component is specially designed, it inherits the USML category
% of its parent system
classified(Component, "usml", Category, "Specially designed component") :-
    specially_designed(Component),
    parent_system(Component, System),
    classified(System, "usml", Category, _).

% If component is specially designed but parent category unknown,
% classify as general USML controlled
classified(Component, "usml", "specially_designed", "Specially designed for USML article") :-
    specially_designed(Component),
    parent_system(Component, System),
    classified(System, "usml", _, _),
    not classified(Component, "usml", _, "Specially designed component").

% =============================================================================
% USAGE NOTES
% =============================================================================
%
% 1. This file implements the framework for "specially designed" analysis.
%    Individual USML category files should define their controlled articles
%    using classified(Item, "usml", Category, Reasoning).
%
% 2. The release paragraph analysis requires domain-specific knowledge about
%    form/fit/function equivalence, manufacturing complexity, and general
%    purpose categories. The predicates here provide a starting framework.
%
% 3. For production use, the equivalent_civilian_component/2 predicate needs
%    a database of civilian equivalents, likely populated from industry
%    catalogs and technical specifications.
%
% 4. The defense contractor list should be populated from SAM.gov registrations
%    or similar authoritative sources.
%
% =============================================================================
