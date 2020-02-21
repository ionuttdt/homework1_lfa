from dfa import *
import sys


def get_states(nfa):
    """
    :param nfa: automat finit nedeterminist
    :return: starile reale in care se poate afla automatul nedeterminist
    """
    e = {}
    for s in nfa.states:
        e[s] = {s}
        if (s, '') in nfa.delta != 0:
            e[s].update(nfa.delta[(s, '')])
        aux_e = None
        while aux_e != e[s]:
            aux_e = e[s].copy()
            for new_s in aux_e:
                if new_s != s:
                    if (new_s, '') in nfa.delta != 0:
                        e[s].update(nfa.delta[(new_s, '')])
    return e


def nfa_to_dfa(nfa):
    """
    st = starile in care se poate afla automatul determinist
    aux_st, dfa_st = toate starile automatului determinist
    l_visited = starile ce urmeaza sa fie vizitate
    new = flag pentru adaugarea unei stari
    f_fs = flag pentru adaugarea starilor finale
    :param nfa: automatul finit nedeterminist
    :return: automatul finit determinist
    """
    dfa = DFA("", {0}, 0, {0}, {})
    dfa.alphabet = nfa.alphabet

    st = get_states(nfa)
    aux_st = {}
    dfa_st = []
    no_st = 0
    new = False
    f_fs = False

    aux_st.update({no_st: st[nfa.start_state]})
    dfa_st.append(st[nfa.start_state])
    l_visited = []
    l_visited.append(st[nfa.start_state])

    g_st = sys.maxsize
    dfa.states.update({g_st})
    for a in nfa.alphabet:
        dfa.delta.update({(g_st, a): {g_st}})

    while len(l_visited) > 0:
        st_cur = dfa_st.index(l_visited.pop())

        for alp in nfa.alphabet:
            next_st = set()
            for s in aux_st[st_cur]:

                if (s, alp) in nfa.delta:
                    new = True
                    for e_s in nfa.delta[(s, alp)]:
                        next_st.update(st[e_s])

            if next_st not in dfa_st and len(next_st) > 0:
                no_st += 1
                aux_st.update({no_st: next_st})
                dfa_st.append(next_st)
                l_visited.append(next_st)
                dfa.states.update({no_st})

            if not (st_cur, alp) in dfa.delta and new:
                new = False
                dfa.delta.update({(st_cur, alp): {dfa_st.index(next_st)}})
            elif new:
                new = False
                dfa.delta[(st_cur, alp)].add({dfa_st.index(next_st)})
            else:
                dfa.delta.update({(st_cur, alp): {g_st}})

    for fs_nfa in nfa.final_states:
        for fs_dfa in dfa_st:
            if fs_nfa in fs_dfa:
                if not f_fs:
                    f_fs = True
                    dfa.final_states = {dfa_st.index(fs_dfa)}
                else:
                    dfa.final_states.add(dfa_st.index(fs_dfa))
    return dfa


def run_dfa(dfa, word):
    """
    Este parcurs cuvantul de la stanga la dreapta.
    Daca simbolul curent nu este in alfabet este intors false.
    Este intors True doar daca cuvantul se termina intr-o stare finala.
    """
    ans = False
    st_cur = dfa.start_state
    last_st_cur = st_cur
    for c in word:
        if c not in dfa.alphabet:
            if c == "\n":
                break
            return False
        st_cur = dfa.delta[(st_cur, c)].pop()
        dfa.delta[(last_st_cur, c)].add(st_cur)
        last_st_cur = st_cur
    if st_cur in dfa.final_states:
        ans = True
    return ans
