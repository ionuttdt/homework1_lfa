from parse import alfabet
from regular_expression import *
from regex import *
from nfa import *


def symbol_any(alf):
    """
    Intoarce a|b|...|8|9 pentru cazul symbol_any.
    """
    if len(alf) == 1:
        return RegularExpression(2, alf)
    else:
        aux = symbol_any(alf[1::])
        return RegularExpression(5, RegularExpression(2, alf[0]), aux)


def symbol_set_tup(tup):
    """
    Trateaza cazul tuplurilor din set
    ex: ("a", "d") = a|b|c|d
    """
    s = tup[0]
    e = tup[1]
    ans = None
    while s != e:
        if ans is None:
            ans = RegularExpression(2, s)
        else:
            ans = RegularExpression(5, ans, RegularExpression(2, s))
        s = chr(ord(s) + 1)
    ans = RegularExpression(5, ans, RegularExpression(2, e))
    return ans


def symbol_set_re(reg):
    """
    Calcularea expresiei regulate pentru cazul SYMBOL_SET prin parcurgerea fiecarui element din set.
    """
    my_set = reg.symbol_set
    ans = None
    while len(my_set) != 0:
        el = my_set.pop()
        if type(el) is tuple:
            if ans is None:
                ans = symbol_set_tup(el)
            else:
                ans = RegularExpression(5, ans, symbol_set_tup(el))
        else:
            if ans is None:
                ans = RegularExpression(2, el)
            else:
                ans = RegularExpression(5, ans, RegularExpression(2, el))
    return ans


def multiple_car(ex, n):
    """
    :param ex: expresia regulata care trebuie concatenata de n ori
    :param n: de cate ori trebuie concatenata expresia
    :return: noua expresie
    """
    ans = ex
    while n > 1:
        n -= 1
        ans = RegularExpression(4, ans, ex)
    return ans


def regex_to_re(reg):
    """
    Functia care face translatia din regex in expresie regulata.
    Calculex recursiv pentru membrul strang si drept cand este cazul, iar rezultatul este construit in
    functie de operatia curenta (EMPTY_STRING, SYMBOL_SIMPLE, ...)
    :param reg: regexul ce trebuie convertit in expresie regulata
    :return re: expresia regulata
    """
    re = None
    if reg.type == EMPTY_STRING:
        re = RegularExpression(1)
    elif reg.type == SYMBOL_SIMPLE:
        re = RegularExpression(2, reg.symbol)
    elif reg.type == SYMBOL_ANY:
        re = symbol_any(alfabet)
    elif reg.type == SYMBOL_SET:
        re = symbol_set_re(reg)
    elif reg.type == MAYBE:
        aux = regex_to_re(reg.lhs)
        re = RegularExpression(5, RegularExpression(1), aux)
    elif reg.type == STAR:
        aux = regex_to_re(reg.lhs)
        re = RegularExpression(3, aux)
    elif reg.type == PLUS:
        aux = regex_to_re(reg.lhs)
        re = RegularExpression(4, aux, RegularExpression(3, aux))
    elif reg.type == CONCATENATION:
        aux_l = regex_to_re(reg.lhs)
        aux_r = regex_to_re(reg.rhs)
        re = RegularExpression(4, aux_l, aux_r)
    elif reg.type == ALTERNATION:
        aux_l = regex_to_re(reg.lhs)
        aux_r = regex_to_re(reg.rhs)
        re = RegularExpression(5, aux_l, aux_r)
    elif reg.type == RANGE:
        re = None
        aux = regex_to_re(reg.lhs)
        if reg.range[0] == reg.range[1]:
            re = multiple_car(aux, reg.range[0])
        elif reg.range[0] == -1:
            re = RegularExpression(5, RegularExpression(1), aux)
            no0 = 1
            while no0 < reg.range[1]:
                no0 += 1
                aux1 = multiple_car(aux, no0)
                re = RegularExpression(5, re, aux1)
        elif reg.range[1] == -1:
            if reg.range[0] == 0:
                re = RegularExpression(3, aux)
            else:
                re = multiple_car(aux, reg.range[0])
                re = RegularExpression(4, re, RegularExpression(3, aux))
        else:
            re = multiple_car(aux, reg.range[0])
            no0 = reg.range[0]
            while no0 < reg.range[1]:
                no0 += 1
                aux1 = multiple_car(aux, no0)
                re = RegularExpression(5, re, aux1)
    return re


# Functii din laboratorul
def rename_states(target, reference):
    off = max(reference.states) + 1
    target.start_state += off
    target.states = set(map(lambda s: s + off, target.states))
    target.final_states = set(map(lambda s: s + off, target.final_states))
    new_delta = {}
    for (state, symbol), next_states in target.delta.items():
        new_next_states = set(map(lambda s: s + off, next_states))
        new_delta[(state + off, symbol)] = new_next_states

    target.delta = new_delta


def new_states(*nfas):
    state = 0
    for nfa in nfas:
        m = max(nfa.states)
        if m >= state:
            state = m + 1

    return state, state + 1


# Tema de laborator:
def re_to_nfa(re):
    ans = NFA("", {0, 1}, 0, {1}, {})

    if re.type == 0:    #EMPTY_SET:
        s_s, f_s = new_states()
        ans = NFA("", {s_s, f_s}, s_s, {f_s}, {})

    if re.type == 1:    #EMPTY_STRING:
        s_s, f_s = new_states()
        ans = NFA("", {s_s, f_s}, s_s, {f_s}, {(s_s, ""): {f_s}})

    if re.type == 2:    #SYMBOL:
        s_s, f_s = new_states()
        ans = NFA(re.symbol, {s_s, f_s}, s_s, {f_s}, {(s_s, re.symbol): {f_s}})

    if re.type == 3:    #STAR
        nfa = re_to_nfa(re.lhs)
        start_state, final_states = new_states(nfa)
        nfa.states.update({start_state, final_states})

        d = nfa.delta
        d.update({(start_state, ""): {nfa.start_state, final_states}})
        d.update({(nfa.final_states.pop(), ""): {final_states, nfa.start_state}})

        ans = NFA(nfa.alphabet, nfa.states, start_state, {final_states}, d)

    if re.type == 4:    #CONCATENATION
        a = re_to_nfa(re.lhs)
        b = re_to_nfa(re.rhs)
        rename_states(a, b)

        s_s, f_s = new_states(a, b)

        a.states.update(b.states)
        a.states.update({s_s, f_s})

        alf = a.alphabet
        for s in b.alphabet:
            if s not in alf:
                alf += s

        d = a.delta
        d.update(b.delta)
        d.update({(a.final_states.pop(), ""): {b.start_state}})
        d.update({(s_s, ""): {a.start_state}})
        d.update({(b.final_states.pop(), ""): {f_s}})
        ans = NFA(alf, a.states, s_s, {f_s}, d)

    if re.type == 5: #ALTERNATION:
        a = re_to_nfa(re.lhs)
        b = re_to_nfa(re.rhs)
        rename_states(a, b)

        alf = a.alphabet
        for s in b.alphabet:
            if s not in alf:
                alf += s

        s_s, f_s = new_states(a, b)

        a.states.update(b.states)
        a.states.update({s_s, f_s})

        d = a.delta
        d.update(b.delta)

        d.update({(s_s, ""): {a.start_state, b.start_state}})
        d.update({(a.final_states.pop(), ""): {f_s}})
        d.update({(b.final_states.pop(), ""): {f_s}})
        ans = NFA(alf, a.states, s_s, {f_s}, d)
    return ans
