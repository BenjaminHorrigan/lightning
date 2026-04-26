% ============================================================================
% OFAC Sanctions — Patterns and Embargoed Destinations
% Source: 31 CFR Parts 500–599 (OFAC sanctions programs)
%         50 USC 1701 et seq. (IEEPA authority)
% ============================================================================
%
% A full SDN list is impractical in static ASP; this file encodes:
%   (1) Comprehensive embargoed country destination patterns
%   (2) WMD-nexus transfer patterns
%   (3) Terrorist organization nexus flags
%
% These rules fire on `attribute/2` facts that the extraction layer populates
% when a stated destination, end-user, or end-use context is detected.
% ============================================================================

% ============================================================================
% Comprehensive sanctions programs — embargoed countries
% 31 CFR Parts 515, 535, 560, 582, 585, 589, 594
% ============================================================================

embargoed_country("iran").
embargoed_country("north_korea").
embargoed_country("dprk").
embargoed_country("cuba").
embargoed_country("syria").
embargoed_country("russia").          % post-2022 comprehensive sanctions
embargoed_country("belarus").         % post-2021
embargoed_country("crimea").          % occupied territory, EO 13685
embargoed_country("donbas").          % occupied regions, EO 14024
embargoed_country("luhansk").
embargoed_country("donetsk").
embargoed_country("sudan").           % SDN / non-SDN
embargoed_country("zimbabwe").
embargoed_country("myanmar").
embargoed_country("burma").
embargoed_country("venezuela").       % OFAC designated sectors
embargoed_country("nicaragua").
embargoed_country("mali").
embargoed_country("haiti").
embargoed_country("afghanistan").     % Taliban-controlled

% Destination-based classification: any transfer to embargoed country
classified(C, "OFAC_embargo_destination", "31 CFR Parts 515-589; 50 USC 1701 et seq.") :-
    component(C),
    attribute(C, Dest),
    embargoed_country(Dest).

classified(S, "OFAC_embargo_destination", "31 CFR Parts 515-589; 50 USC 1701 et seq.") :-
    substance(S),
    attribute(S, Dest),
    embargoed_country(Dest).

% System-level destination flag
classified(Sys, "OFAC_embargo_destination", "31 CFR Parts 515-589; 50 USC 1701 et seq.") :-
    system(Sys),
    attribute(Sys, Dest),
    embargoed_country(Dest).

% ============================================================================
% WMD proliferation nexus patterns — EO 13382 (WMD Proliferators)
% ============================================================================

% Any transfer of WMD-usable technology to designated entities
wmd_nexus_attribute("wmd_end_use").
wmd_nexus_attribute("wmd_proliferator").
wmd_nexus_attribute("wmd_program_support").
wmd_nexus_attribute("nuclear_weapons_program").
wmd_nexus_attribute("chemical_weapons_program").
wmd_nexus_attribute("biological_weapons_program").
wmd_nexus_attribute("missile_wmd_delivery").

classified(C, "OFAC_WMD_nexus", "EO 13382; 31 CFR Part 544") :-
    component(C),
    attribute(C, Attr),
    wmd_nexus_attribute(Attr).

classified(S, "OFAC_WMD_nexus", "EO 13382; 31 CFR Part 544") :-
    substance(S),
    attribute(S, Attr),
    wmd_nexus_attribute(Attr).

% ============================================================================
% Terrorist organization nexus — EO 13224, 31 CFR Part 594
% ============================================================================

terrorist_nexus_attribute("sdgt_entity").
terrorist_nexus_attribute("terrorist_organization").
terrorist_nexus_attribute("terrorist_end_use").
terrorist_nexus_attribute("foreign_terrorist_organization").
terrorist_nexus_attribute("isis_affiliated").
terrorist_nexus_attribute("al_qaeda_affiliated").
terrorist_nexus_attribute("hamas_affiliated").
terrorist_nexus_attribute("hezbollah_affiliated").
terrorist_nexus_attribute("irgc_affiliated").
terrorist_nexus_attribute("irgc_qf_affiliated").

classified(C, "OFAC_terrorist_nexus", "EO 13224; 31 CFR Part 594") :-
    component(C),
    attribute(C, Attr),
    terrorist_nexus_attribute(Attr).

classified(S, "OFAC_terrorist_nexus", "EO 13224; 31 CFR Part 594") :-
    substance(S),
    attribute(S, Attr),
    terrorist_nexus_attribute(Attr).

% ============================================================================
% Sectoral sanctions — 31 CFR Part 589 (Russia)
% Specific sectors: defense/intelligence, energy, financial
% ============================================================================

russia_sanctioned_sector("russian_defense_sector").
russia_sanctioned_sector("russian_intelligence_sector").
russia_sanctioned_sector("russian_military_sector").
russia_sanctioned_sector("russian_defense_ministry").
russia_sanctioned_sector("russian_fsvb").
russia_sanctioned_sector("russian_svr").

classified(C, "OFAC_Russia_sectoral", "31 CFR Part 589; EO 14024") :-
    component(C),
    attribute(C, Attr),
    russia_sanctioned_sector(Attr).

classified(S, "OFAC_Russia_sectoral", "31 CFR Part 589; EO 14024") :-
    substance(S),
    attribute(S, Attr),
    russia_sanctioned_sector(Attr).

% ============================================================================
% Iran nuclear sanctions — 31 CFR Part 560 (ITSR)
% Additional specificity for nuclear/missile nexus
% ============================================================================

classified(C, "OFAC_Iran_nuclear", "31 CFR Part 560 (ITSR); 31 CFR Part 544") :-
    component(C),
    attribute(C, "iran_destination"),
    attribute(C, Attr),
    wmd_nexus_attribute(Attr).

classified(C, "OFAC_Iran_nuclear", "31 CFR Part 560 (ITSR); 31 CFR Part 544") :-
    component(C),
    attribute(C, "iran_nuclear_program").

% ============================================================================
% North Korea comprehensive sanctions — 31 CFR Part 510
% ============================================================================

classified(C, "OFAC_DPRK", "31 CFR Part 510; EO 13722") :-
    component(C),
    attribute(C, "north_korea_destination").

classified(C, "OFAC_DPRK", "31 CFR Part 510; EO 13722") :-
    component(C),
    attribute(C, "dprk_destination").

classified(S, "OFAC_DPRK", "31 CFR Part 510; EO 13722") :-
    substance(S),
    attribute(S, "north_korea_destination").

classified(S, "OFAC_DPRK", "31 CFR Part 510; EO 13722") :-
    substance(S),
    attribute(S, "dprk_destination").

% ============================================================================
% Output
% ============================================================================

controlled_element(X) :- classified(X, _, _).

#show classified/3.
#show controlled_element/1.
