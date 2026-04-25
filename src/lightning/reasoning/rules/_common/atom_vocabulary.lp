% =============================================================================
% LIGHTNING Standard Atom Vocabulary
% =============================================================================
% This file defines the canonical shapes of all atoms used across LIGHTNING rules.
% Every regime-specific .lp file should #include this file to ensure
% consistent atom signatures and enable cross-regime reasoning.
%
% Generated atoms (from extraction) use lowercase_underscore naming.
% Classification atoms (from reasoning) use the same convention.
% =============================================================================

% -----------------------------------------------------------------------------
% § SUBSTANCE FACTS (emitted by extraction)
% -----------------------------------------------------------------------------

% Basic substance identification
% substance(Name).                         % canonical name (lowercase_underscore)
% cas_number(Substance, CAS).              % CAS registry number as string
% inchi(Substance, InChIString).           % IUPAC International Chemical Identifier
% smiles(Substance, SMILES).               % Simplified molecular input line entry
% molecular_formula(Substance, Formula).   % e.g., "C8H9NO2" for acetaminophen
% iupac_name(Substance, Name).             % systematic IUPAC name

% Regulatory classification of substances
% schedule(Substance, Regime, Schedule).   % e.g., schedule("sarin", "cwc", 1)
%   Regimes: "cwc", "dea", "hhs_select", "usda_select", "australia_group"
%   Schedules: integers or strings depending on regime

% Physical properties and quantities
% quantity(Substance, Value, Unit).        % e.g., quantity("vx", 50, "mg")
% purity(Substance, Percent).              % percentage purity
% physical_state(Substance, State).        % "solid", "liquid", "gas"
% melting_point(Substance, Temp, Unit).    % e.g., melting_point("tnt", 80.1, "celsius")
% boiling_point(Substance, Temp, Unit).

% Chemical relationships
% precursor_of(PrecursorSubstance, ProductSubstance).
% reaction_product_of(Product, Reactant, ReactionType).
%   ReactionTypes: "hydrolysis", "fluorination", "methylation", "acetylation", etc.
% isomer_of(Substance1, Substance2).
% structural_analog_of(Substance1, Substance2).

% Functional group patterns (for pattern-based classification)
% contains_functional_group(Substance, Group).
%   Groups: "organophosphorus", "carbamate", "fluorinated", "nitro", "azide", etc.
% organophosphorus_precursor(Substance).   % shorthand for specific CWC pattern

% -----------------------------------------------------------------------------
% § COMPONENT FACTS (emitted by extraction)
% -----------------------------------------------------------------------------

% Basic component identification
% component(Name).                         % canonical name (lowercase_underscore)
% component_category(Component, Category). % "turbopump", "centrifuge", "laser", etc.
% component_subcategory(Component, Subcat).% more specific categorization
% part_number(Component, PartNumber).      % manufacturer part number
% manufacturer(Component, Company).

% Component relationships
% parent_system(Component, System).        % what system this component belongs to
% subcomponent_of(Component, ParentComponent).
% assembly_contains(Assembly, Component).

% Technical specifications
% specification(Component, Parameter, Value, Unit).
%   Common parameters: "power", "speed_rpm", "pressure_bar", "temperature_k",
%   "flow_rate", "voltage", "frequency", "diameter_mm", "length_mm", etc.
% material(Component, Material).           % construction material
% coating(Component, Coating).             % surface coating/treatment
% tolerance(Component, Parameter, PlusMinus, Unit).

% Performance characteristics
% operates_at(Component, Parameter, Min, Max, Unit).
% rated_for(Component, Condition, Value, Unit).
% maximum_operating(Component, Parameter, Value, Unit).

% -----------------------------------------------------------------------------
% § SYSTEM FACTS (emitted by extraction)
% -----------------------------------------------------------------------------

% System identification
% system(Name).                            % canonical system name
% system_type(System, Type).               % "rocket", "aircraft", "satellite", etc.
% system_designation(System, Designation). % official designation (e.g., "F-16C")
% system_variant(BaseSystem, Variant).

% System capabilities (critical for threshold-based rules)
% system_capability(System, Parameter, Value, Unit).
%   Key parameters: "payload_kg", "range_km", "speed_mach", "altitude_m",
%   "thrust_n", "power_w", etc.
% performance_envelope(System, Parameter, Min, Max, Unit).

% System purpose and classification
% intended_end_use(System, Use).           % "military", "civilian", "dual_use", "research"
% military_designation(System, Branch, Role). % e.g., ("f22_raptor", "usaf", "fighter")
% civilian_certification(System, Authority, CertNumber).

% System composition
% system_contains(System, Component).
% primary_propulsion(System, PropulsionType).
% guidance_system(System, GuidanceType).

% -----------------------------------------------------------------------------
% § CONTEXT FACTS (emitted by extraction or provided by user)
% -----------------------------------------------------------------------------

% Export/transfer context
% destination_country(Artifact, Country).  % destination for export analysis
% recipient_entity(Artifact, Entity).      % receiving organization
% end_user(Artifact, Entity).              % ultimate end user
% export_purpose(Artifact, Purpose).       % stated purpose of export/transfer

% Research context
% researcher_affiliation(Affiliation).     % institution conducting research
% research_purpose(Purpose).               % stated research purpose
% research_sponsor(Sponsor).               % funding organization
% clearance_level(Entity, Level).          % security clearance if applicable

% License and authorization context
% existing_license(Artifact, Authority, LicenseType, Status).
% license_exemption_claimed(Artifact, Authority, Exemption).
% export_administration(Artifact, Jurisdiction). % "itar", "ear", "ofac", etc.

% -----------------------------------------------------------------------------
% § CLASSIFICATION ATOMS (produced by reasoning rules)
% -----------------------------------------------------------------------------

% Primary classification results
% classified(Artifact, Regime, Category, Reasoning).
%   Regimes: "usml", "ear", "cwc", "bwc", "mtcr", "wassenaar", etc.
%   Categories: regime-specific (e.g., "iv_h", "schedule_1", "category_i")
%   Reasoning: human-readable explanation string

% USML-specific classification concepts
% specially_designed(Component).           % meets 22 CFR 120.41 definition
% release_paragraph_applies(Component, Paragraph). % (b)(1) through (b)(5) releases
% enumerated_article(Artifact, USMLCategory). % directly listed in USML
% parts_components_accessories(Component, ParentArticle).

% EAR/CCL-specific classification concepts
% eccn_classified(Artifact, ECCN).         % Export Control Classification Number
% ear_designation(Artifact, Designation).  % "EAR99", "Commerce Control List", etc.
% license_required(Artifact, Destination). % destination-dependent licensing
% license_exception_available(Artifact, Exception). % available exceptions

% Cross-cutting classification concepts
% controlled_under(Artifact, Regime).      % high-level "this regime applies"
% dual_use_item(Artifact).                 % has both civilian and military applications
% military_critical_technology(Artifact).  % technology critical to military capability

% WMD-related concepts
% weapons_related(Artifact, WeaponType).   % "chemical", "biological", "nuclear"
% proliferation_concern(Artifact, Concern). % specific proliferation risk
% precursor_material(Material, TargetWeapon).

% -----------------------------------------------------------------------------
% § CROSS-REGIME REASONING ATOMS
% -----------------------------------------------------------------------------

% Multiple regime violations
% cross_regime_violation(Artifact, RegimeList, Reason).
%   RegimeList: list of regime names that simultaneously apply
%   Reason: explanation of the cross-regime concern

% Regime-specific interaction patterns
% usml_mtcr_overlap(Artifact, USMLCategory, MTCRCategory).
% ear_wassenaar_overlap(Artifact, ECCN, WassenaarReference).
% cwc_usml_xiv_overlap(Substance, CWCSchedule, USMLSubcategory).

% Escalation triggers
% requires_human_review(Artifact, Reason).
% ambiguous_classification(Artifact, PossibleRegimes).
% insufficient_information(Artifact, MissingFacts).

% Gap analysis
% extraction_gap(Artifact, AtomType, Confidence).
% reasoning_gap(Artifact, RuleFile, MissingPremises).

% -----------------------------------------------------------------------------
% § CONFIDENCE AND METADATA ATOMS
% -----------------------------------------------------------------------------

% Rule application confidence
% rule_confidence(RuleName, Artifact, Confidence). % 0.0 to 1.0
% extraction_confidence(AtomType, Artifact, Confidence).
% classification_confidence(Regime, Artifact, Confidence).

% Provenance and audit trail
% fact_source(Atom, Source).               % where this fact came from
% extracted_at(Atom, Timestamp).           % when this fact was extracted
% rule_version(RuleFile, Version, Date).   % version of rules used
% regulation_version(Regime, Version, EffectiveDate). % regulatory version used

% Decision metadata
% decision_basis(Artifact, AtomList).       % which atoms drove the decision
% primary_citation(Classification, CFRReference, Text).
% supporting_citation(Classification, CFRReference, Text).
% consulted_authority(Classification, Authority, Document).

% =============================================================================
% USAGE NOTES
% =============================================================================
%
% 1. NAMING CONVENTION: All atom names use lowercase_underscore. Multi-word
%    substance/component names are normalized (e.g., "Diethyl phosphite" →
%    "diethyl_phosphite").
%
% 2. UNITS: Always specify units explicitly. Common units:
%    - Mass: "g", "kg", "lb", "ton"
%    - Length: "mm", "cm", "m", "in", "ft"
%    - Pressure: "bar", "psi", "pa", "atm"
%    - Temperature: "celsius", "kelvin", "fahrenheit"
%    - Speed: "mps" (meters/sec), "mph", "kmh", "mach"
%    - Power: "w", "kw", "hp"
%    - Force: "n" (newtons), "lbf"
%
% 3. COUNTRY CODES: Use ISO 3166-1 alpha-2 codes (e.g., "US", "CN", "RU").
%
% 4. CONFIDENCE VALUES: 0.0 to 1.0, where:
%    - 1.0 = certain (e.g., substance on published schedule)
%    - 0.8-0.9 = high confidence (clear pattern match)
%    - 0.6-0.7 = moderate confidence (probable but not certain)
%    - 0.3-0.5 = low confidence (weak pattern or ambiguous)
%    - 0.0-0.2 = very uncertain (extraction error likely)
%
% 5. INCLUDE DIRECTIVE: Every regime .lp file should start with:
%    #include "_common/atom_vocabulary.lp".
%
% =============================================================================
