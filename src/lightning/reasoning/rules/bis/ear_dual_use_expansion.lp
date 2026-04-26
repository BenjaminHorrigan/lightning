% ============================================================================
% BIS EAR Dual-Use Expansion — Additional ECCNs
% Source: 15 CFR Part 774 (CCL); EAR Supplement No. 1 to Part 774
% ============================================================================

% ============================================================================
% ECCN 1C350 — Chemical weapons precursors (CWC Schedule 2/3 overlap)
% 15 CFR Part 774, ECCN 1C350
% ============================================================================

% 1C350.a — Schedule 2A chemicals
eccn_1c350_a_substance("amiton").
eccn_1c350_a_substance("pfib").
eccn_1c350_a_substance("bz_3_quinuclidinyl_benzilate").
eccn_1c350_a_substance("3_quinuclidinyl_benzilate").

% 1C350.b — Schedule 2B chemicals (precursors)
eccn_1c350_b_substance("thiodiglycol").
eccn_1c350_b_substance("methyl_phosphonic_acid").
eccn_1c350_b_substance("dimethyl_methylphosphonate").
eccn_1c350_b_substance("dmmp").
eccn_1c350_b_substance("diethyl_methylphosphonate").
eccn_1c350_b_substance("dimethyl_phosphite").
eccn_1c350_b_substance("methyl_phosphonothioic_dichloride").
eccn_1c350_b_substance("methyl_phosphonic_difluoride").
eccn_1c350_b_substance("o_ethyl_o_2_diisopropylaminoethyl_methylphosphonite").
eccn_1c350_b_substance("cyclohexanol").
eccn_1c350_b_substance("phosphorus_trichloride").
eccn_1c350_b_substance("phosphorus_pentachloride").
eccn_1c350_b_substance("trimethyl_phosphite").
eccn_1c350_b_substance("triethyl_phosphite").
eccn_1c350_b_substance("thionyl_chloride").

% 1C350.c — Schedule 3 chemicals (large-volume industrial, export control relevance)
eccn_1c350_c_substance("phosgene").
eccn_1c350_c_substance("cyanogen_chloride").
eccn_1c350_c_substance("hydrogen_cyanide").
eccn_1c350_c_substance("chloropicrin").
eccn_1c350_c_substance("triethanolamine").

classified(S, "EAR_1C350_a", "15 CFR Part 774, ECCN 1C350.a") :-
    substance(S),
    eccn_1c350_a_substance(S).

classified(S, "EAR_1C350_b", "15 CFR Part 774, ECCN 1C350.b") :-
    substance(S),
    eccn_1c350_b_substance(S).

classified(S, "EAR_1C350_c", "15 CFR Part 774, ECCN 1C350.c") :-
    substance(S),
    eccn_1c350_c_substance(S).

% CAS-based matching for 1C350
eccn_1c350_cas("62-74-8").    % sodium fluoroacetate — pest control/dual-use
eccn_1c350_cas("596-09-8").   % dimethyl methylphosphonate (DMMP)
eccn_1c350_cas("507-55-1").   % chloropicrin
eccn_1c350_cas("75-44-5").    % phosgene
eccn_1c350_cas("74-90-8").    % hydrogen cyanide
eccn_1c350_cas("111-48-8").   % thiodiglycol
eccn_1c350_cas("10025-67-9"). % sulfur monochloride
eccn_1c350_cas("7719-09-7").  % thionyl chloride
eccn_1c350_cas("7647-19-0").  % phosphorus pentafluoride

classified(S, "EAR_1C350_CAS", "15 CFR Part 774, ECCN 1C350 [CAS match]") :-
    substance(S),
    cas_number(S, CAS),
    eccn_1c350_cas(CAS).

% ============================================================================
% ECCN 2B001 — Machine tools with precision tolerances
% Threshold: positional accuracy < 6 micron (6000 nm)
% Performance fact: positional_accuracy_nm as integer
% 15 CFR Part 774, ECCN 2B001
% ============================================================================

classified(C, "EAR_2B001", "15 CFR Part 774, ECCN 2B001") :-
    component(C),
    component_category(C, "machine_tool"),
    performance(C, "positional_accuracy_nm", Acc),
    Acc < 6000.

classified(C, "EAR_2B001", "15 CFR Part 774, ECCN 2B001") :-
    component(C),
    component_category(C, "cnc_machine_tool"),
    performance(C, "positional_accuracy_nm", Acc),
    Acc < 6000.

classified(C, "EAR_2B001", "15 CFR Part 774, ECCN 2B001") :-
    component(C),
    component_category(C, "lathe_precision"),
    performance(C, "positional_accuracy_nm", Acc),
    Acc < 6000.

classified(C, "EAR_2B001", "15 CFR Part 774, ECCN 2B001") :-
    component(C),
    component_category(C, "milling_machine_precision"),
    performance(C, "positional_accuracy_nm", Acc),
    Acc < 6000.

% ============================================================================
% ECCN 3A001 — Electronic components
% GaAs MMICs, high-speed ADCs (> 200 MSPS)
% 15 CFR Part 774, ECCN 3A001
% ============================================================================

classified(C, "EAR_3A001_a", "15 CFR Part 774, ECCN 3A001.a") :-
    component(C),
    component_category(C, "gaas_mmic").

classified(C, "EAR_3A001_a", "15 CFR Part 774, ECCN 3A001.a") :-
    component(C),
    component_category(C, "gan_mmic").

classified(C, "EAR_3A001_a", "15 CFR Part 774, ECCN 3A001.a") :-
    component(C),
    component_category(C, "inp_mmic").

% ADC > 200 MSPS (200_000_000 samples/sec, stored as MSPS integer)
classified(C, "EAR_3A001_a_5", "15 CFR Part 774, ECCN 3A001.a.5") :-
    component(C),
    component_category(C, "analog_to_digital_converter"),
    performance(C, "sample_rate_msps", SR),
    SR > 200.

% DAC > 3500 MSPS
classified(C, "EAR_3A001_a_6", "15 CFR Part 774, ECCN 3A001.a.6") :-
    component(C),
    component_category(C, "digital_to_analog_converter"),
    performance(C, "sample_rate_msps", SR),
    SR > 3500.

% High-speed electronics for radar/EW
classified(C, "EAR_3A001_b", "15 CFR Part 774, ECCN 3A001.b") :-
    component(C),
    component_category(C, "frequency_synthesizer_microwave").

% ============================================================================
% ECCN 5A001 — Telecommunications equipment
% Spread spectrum, frequency hopping, crypto
% 15 CFR Part 774, ECCN 5A001
% ============================================================================

classified(C, "EAR_5A001_b", "15 CFR Part 774, ECCN 5A001.b") :-
    component(C),
    component_category(C, "spread_spectrum_radio").

classified(C, "EAR_5A001_b", "15 CFR Part 774, ECCN 5A001.b") :-
    component(C),
    component_category(C, "frequency_hopping_radio_commercial").

classified(C, "EAR_5A001_b", "15 CFR Part 774, ECCN 5A001.b") :-
    component(C),
    component_category(C, "software_defined_radio").

% SATCOM terminals with anti-jam
classified(C, "EAR_5A001_f", "15 CFR Part 774, ECCN 5A001.f") :-
    component(C),
    component_category(C, "satcom_terminal"),
    attribute(C, "anti_jam_capability").

% ============================================================================
% ECCN 6A002 — Optical sensors and focal plane arrays
% Cooled FPAs controlled at all wavelengths
% 15 CFR Part 774, ECCN 6A002
% ============================================================================

classified(C, "EAR_6A002_a", "15 CFR Part 774, ECCN 6A002.a") :-
    component(C),
    component_category(C, "infrared_focal_plane_array"),
    attribute(C, "cooled").

classified(C, "EAR_6A002_a", "15 CFR Part 774, ECCN 6A002.a") :-
    component(C),
    component_category(C, "cryogenically_cooled_detector").

classified(C, "EAR_6A002_a", "15 CFR Part 774, ECCN 6A002.a") :-
    component(C),
    component_category(C, "hgcdte_detector").

classified(C, "EAR_6A002_a", "15 CFR Part 774, ECCN 6A002.a") :-
    component(C),
    component_category(C, "indium_antimonide_detector").

% ============================================================================
% ECCN 7A001 — Accelerometers (inertial navigation)
% Threshold: bias < 1 mg (1000 micro-g), over-range > 100g
% Performance: bias_ug (micro-g), over_range_g
% 15 CFR Part 774, ECCN 7A001
% ============================================================================

% High-precision accelerometer: bias < 1000 micro-g (1 mg)
classified(C, "EAR_7A001_a", "15 CFR Part 774, ECCN 7A001.a") :-
    component(C),
    component_category(C, "accelerometer"),
    performance(C, "bias_ug", Bias),
    Bias < 1000.

% ============================================================================
% ECCN 7A003 — Gyroscopes (inertial navigation)
% Threshold: drift rate < 0.5 deg/hr
% Performance: drift_rate_mdeg_hr (milli-deg/hr), < 500 = < 0.5 deg/hr
% 15 CFR Part 774, ECCN 7A003
% ============================================================================

classified(C, "EAR_7A003_a", "15 CFR Part 774, ECCN 7A003.a") :-
    component(C),
    component_category(C, "gyroscope"),
    performance(C, "drift_rate_mdeg_hr", DR),
    DR < 500.

classified(C, "EAR_7A003_a", "15 CFR Part 774, ECCN 7A003.a") :-
    component(C),
    component_category(C, "ring_laser_gyroscope"),
    performance(C, "drift_rate_mdeg_hr", DR),
    DR < 500.

classified(C, "EAR_7A003_a", "15 CFR Part 774, ECCN 7A003.a") :-
    component(C),
    component_category(C, "fiber_optic_gyroscope"),
    performance(C, "drift_rate_mdeg_hr", DR),
    DR < 500.

% ============================================================================
% ECCN 7E001 — Technology for inertial navigation systems
% 15 CFR Part 774, ECCN 7E001
% ============================================================================

classified(C, "EAR_7E001", "15 CFR Part 774, ECCN 7E001") :-
    component(C),
    component_category(C, "inertial_navigation_system"),
    attribute(C, "controlled_performance").

classified(C, "EAR_7E001", "15 CFR Part 774, ECCN 7E001") :-
    component(C),
    component_category(C, "inertial_measurement_unit_commercial"),
    performance(C, "drift_rate_mdeg_hr", DR),
    DR < 500.

% ============================================================================
% ECCN 9A004 — Space launch vehicles (EAR boundary; overlap with USML IV)
% Items NOT on USML (i.e., commercial SLVs that cleared CJ)
% 15 CFR Part 774, ECCN 9A004
% ============================================================================

classified(C, "EAR_9A004", "15 CFR Part 774, ECCN 9A004") :-
    component(C),
    component_category(C, "space_launch_vehicle_commercial"),
    not attribute(C, "usml_classified").

classified(C, "EAR_9A004", "15 CFR Part 774, ECCN 9A004") :-
    component(C),
    component_category(C, "commercial_satellite_launch_vehicle"),
    not attribute(C, "usml_classified").

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
