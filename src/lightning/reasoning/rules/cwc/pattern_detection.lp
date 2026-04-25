% =============================================================================
% CWC pattern-based detection (Article II.1.(a) general purpose criterion)
% =============================================================================
% Catches unlisted toxic chemicals via structural patterns. Pattern hits
% always require human review — they're suspicious, not definitive.

% --- Pattern 1: organophosphorus + fluorinated (classic nerve-agent pattern)
classified(S, "cwc", "pattern_op_fluorinated",
    "Organophosphorus + fluorination pattern (potential nerve agent precursor)") :-
    substance(S),
    contains_functional_group(S, "organophosphorus"),
    contains_functional_group(S, "fluorinated"),
    not schedule(S, "cwc", _).

% --- Pattern 2: organophosphorus + halogenated (broader precursor pattern)
% Body disjunction split into helper rule (clingo doesn't accept (A;B;C) in body).
_op_halogenated(S) :- contains_functional_group(S, "organophosphorus"), contains_functional_group(S, "chlorinated").
_op_halogenated(S) :- contains_functional_group(S, "organophosphorus"), contains_functional_group(S, "brominated").
_op_halogenated(S) :- contains_functional_group(S, "organophosphorus"), contains_functional_group(S, "fluorinated").

classified(S, "cwc", "pattern_op_halogenated",
    "Organophosphorus + halogen pattern (broad precursor signature)") :-
    substance(S),
    _op_halogenated(S),
    not schedule(S, "cwc", _).

% --- Pattern 3: cholinesterase inhibitor structural patterns
cholinesterase_inhibitor_structure(S) :-
    contains_functional_group(S, "organophosphorus"),
    contains_functional_group(S, "ester").
cholinesterase_inhibitor_structure(S) :-
    contains_functional_group(S, "carbamate"),
    contains_functional_group(S, "methyl").

classified(S, "cwc", "pattern_cholinesterase",
    "Cholinesterase inhibitor structural pattern") :-
    substance(S),
    cholinesterase_inhibitor_structure(S),
    not schedule(S, "cwc", _).

% --- Pattern 4: mustard-like alkylating agents
alkylating_agent_structure(S) :- contains_functional_group(S, "bis_chloroethyl").
alkylating_agent_structure(S) :- contains_functional_group(S, "nitrogen_mustard").

classified(S, "cwc", "pattern_alkylating",
    "Alkylating-agent structural pattern (mustard-like)") :-
    substance(S),
    alkylating_agent_structure(S),
    not schedule(S, "cwc", _).

% --- Any pattern hit ⇒ human review (intent verification)
% Enumerate the four pattern names directly; clingo can't do string_concat-prefix matching.
_cwc_pattern_hit(S) :- classified(S, "cwc", "pattern_op_fluorinated", _).
_cwc_pattern_hit(S) :- classified(S, "cwc", "pattern_op_halogenated", _).
_cwc_pattern_hit(S) :- classified(S, "cwc", "pattern_cholinesterase", _).
_cwc_pattern_hit(S) :- classified(S, "cwc", "pattern_alkylating", _).

requires_human_review(S, "Matches CWC toxic-chemical pattern; verify research intent") :-
    _cwc_pattern_hit(S).
