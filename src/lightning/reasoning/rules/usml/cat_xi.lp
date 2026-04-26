% ============================================================================
% USML Category XI — Military Electronics
% Source: 22 CFR 121.1, Category XI
% ============================================================================

% ============================================================================
% Category XI(a)(1) — Electronic warfare systems
% Jamming, SIGINT, ELINT, direction finding
% 22 CFR 121.1 Category XI(a)(1)
% ============================================================================

category_xi_a1_system("electronic_warfare_system").
category_xi_a1_system("electronic_attack_system").
category_xi_a1_system("radar_jammer").
category_xi_a1_system("communications_jammer").
category_xi_a1_system("gps_jammer").
category_xi_a1_system("infrared_jammer").
category_xi_a1_system("laser_jammer").
category_xi_a1_system("deception_jammer").
category_xi_a1_system("noise_jammer").
category_xi_a1_system("active_cancellation_ew").
category_xi_a1_system("sigint_system").
category_xi_a1_system("elint_system").
category_xi_a1_system("comint_system").
category_xi_a1_system("direction_finding_military").
category_xi_a1_system("emitter_locating_system").
category_xi_a1_system("electronic_support_measures").
category_xi_a1_system("electronic_intelligence_receiver").

classified(C, "USML_XI_a_1", "22 CFR 121.1 Category XI(a)(1)") :-
    component(C),
    component_category(C, Cat),
    category_xi_a1_system(Cat).

% ============================================================================
% Category XI(a)(2) — Military communications: SATCOM, crypto, COMSEC
% 22 CFR 121.1 Category XI(a)(2)
% ============================================================================

category_xi_a2_system("military_satcom_terminal").
category_xi_a2_system("milsatcom_terminal").
category_xi_a2_system("crypto_equipment").
category_xi_a2_system("comsec_equipment").
category_xi_a2_system("type1_encryption_device").
category_xi_a2_system("nsa_approved_crypto").
category_xi_a2_system("secure_voice_terminal").
category_xi_a2_system("key_fill_device").
category_xi_a2_system("communications_security_module").
category_xi_a2_system("frequency_hopping_radio").
category_xi_a2_system("spread_spectrum_military_radio").
category_xi_a2_system("anti_jam_satcom").
category_xi_a2_system("have_quick_radio").
category_xi_a2_system("sincgars_radio").
category_xi_a2_system("jtids_terminal").
category_xi_a2_system("link16_terminal").
category_xi_a2_system("iff_interrogator").
category_xi_a2_system("iff_transponder").
category_xi_a2_system("identification_friend_or_foe").
category_xi_a2_system("military_data_link").

classified(C, "USML_XI_a_2", "22 CFR 121.1 Category XI(a)(2)") :-
    component(C),
    component_category(C, Cat),
    category_xi_a2_system(Cat).

% ============================================================================
% Category XI(a)(3) — Radar systems: fire control, SAR, ISAR, FMCW
% 22 CFR 121.1 Category XI(a)(3)
% ============================================================================

category_xi_a3_system("fire_control_radar").
category_xi_a3_system("fire_control_system").
category_xi_a3_system("weapon_guidance_radar").
category_xi_a3_system("synthetic_aperture_radar").
category_xi_a3_system("sar_military").
category_xi_a3_system("isar").
category_xi_a3_system("inverse_synthetic_aperture_radar").
category_xi_a3_system("fmcw_radar").
category_xi_a3_system("ground_penetrating_radar_military").
category_xi_a3_system("foliage_penetrating_radar").
category_xi_a3_system("moving_target_indicator_radar").
category_xi_a3_system("airborne_intercept_radar").
category_xi_a3_system("air_intercept_radar").
category_xi_a3_system("ballistic_missile_defense_radar").
category_xi_a3_system("phased_array_radar_military").
category_xi_a3_system("aesa_radar").
category_xi_a3_system("terrain_following_radar").
category_xi_a3_system("anti_radiation_missile_seeker").

classified(C, "USML_XI_a_3", "22 CFR 121.1 Category XI(a)(3)") :-
    component(C),
    component_category(C, Cat),
    category_xi_a3_system(Cat).

% ============================================================================
% Category XI(a)(4) — Military sonar
% 22 CFR 121.1 Category XI(a)(4)
% ============================================================================

category_xi_a4_system("hull_mounted_sonar").
category_xi_a4_system("towed_array_sonar").
category_xi_a4_system("dipping_sonar").
category_xi_a4_system("active_sonar_military").
category_xi_a4_system("passive_sonar_military").
category_xi_a4_system("sonobuoy_military").
category_xi_a4_system("submarine_detection_system").

classified(C, "USML_XI_a_4", "22 CFR 121.1 Category XI(a)(4)") :-
    component(C),
    component_category(C, Cat),
    category_xi_a4_system(Cat).

% ============================================================================
% Category XI(a)(5) — Directed energy weapons
% 22 CFR 121.1 Category XI(a)(5)
% ============================================================================

% High-power laser systems: power > 1W at military-relevant wavelengths
classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "high_energy_laser"),
    performance(C, "power_w", P),
    P >= 1.

classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "directed_energy_weapon").

classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "high_power_microwave_weapon").

classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "particle_beam_weapon").

classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "active_denial_system").

classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "laser_dazzler_military").

% Laser rangefinders used in weapon systems (military spec)
classified(C, "USML_XI_a_5", "22 CFR 121.1 Category XI(a)(5)") :-
    component(C),
    component_category(C, "laser_rangefinder"),
    attribute(C, "weapon_system_integrated").

% ============================================================================
% Category XI(b) — Night vision and thermal imaging
% 22 CFR 121.1 Category XI(b)
% ============================================================================

category_xi_b_item("image_intensifier_tube").
category_xi_b_item("night_vision_goggle_military").
category_xi_b_item("night_vision_device_military").
category_xi_b_item("thermal_imaging_weapon_sight").
category_xi_b_item("forward_looking_infrared_military").
category_xi_b_item("flir_military").
category_xi_b_item("infrared_detector_focal_plane_array_military").
category_xi_b_item("infrared_search_track").

classified(C, "USML_XI_b", "22 CFR 121.1 Category XI(b)") :-
    component(C),
    component_category(C, Cat),
    category_xi_b_item(Cat).

% ============================================================================
% Category XI(c) — Intelligence collection and processing
% 22 CFR 121.1 Category XI(c)
% ============================================================================

category_xi_c_item("signals_intelligence_processor").
category_xi_c_item("cryptanalysis_equipment").
category_xi_c_item("traffic_analysis_system").
category_xi_c_item("fusion_center_military").
category_xi_c_item("intelligence_processing_system").

classified(C, "USML_XI_c", "22 CFR 121.1 Category XI(c)") :-
    component(C),
    component_category(C, Cat),
    category_xi_c_item(Cat).

% ============================================================================
% Category XI(d) — Parts and components for Cat XI systems
% 22 CFR 121.1 Category XI(d)
% ============================================================================

category_xi_d_part("traveling_wave_tube_ew").
category_xi_d_part("gallium_nitride_power_amplifier_military").
category_xi_d_part("radar_transmitter_module").
category_xi_d_part("active_electronically_scanned_array_module").
category_xi_d_part("aesa_module").
category_xi_d_part("electronic_countermeasure_pod").
category_xi_d_part("chaff_dispenser").
category_xi_d_part("flare_dispenser_military").

classified(C, "USML_XI_d", "22 CFR 121.1 Category XI(d)") :-
    component(C),
    component_category(C, Cat),
    category_xi_d_part(Cat).

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
