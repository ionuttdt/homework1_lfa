from regex import *

alfabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
op = "*?+"


def get_number(str):
    """
    Functie folosita pentru parsarea numerelor pentru RANGE.
    """
    for i, s in enumerate(str):
        if s == ",":
            if i == 0:
                return -1
            else:
                return int(str[:i])
        elif s == "}":
            if i == 0:
                return -1
            else:
                return int(str[:i])


def symbol_set(str):
    """
    Parsarea stringului pentru cazul SYMBOL_SET.
    Stabilesc daca sunt simple simboluri sau tupluri si le adaug in set.

    Cand simbolul este "-", trebuie sters ultimul element adaugat in set si adaugat noul tuplu.
    """
    my_set = None
    aux = None
    cont = False
    for x in str:
        if cont:
            cont = False
            my_set.add((aux, x))
            continue
        if x in alfabet:
            if my_set is None:
                my_set = {x}
            else:
                my_set.add(x)
        elif x == "-":
            my_set.remove(aux)
            cont = True
            continue
        elif x == "]":
            return RegEx(SYMBOL_SET, my_set)
        aux = x


def str_to_regex(str):
    """
    Rezultatul este stocat in ans la care se adauga prin concatenare noul regex parsat.
    In variabila aux1 este stocat ultimul simbol din alfabet parsat.
    Functia are multe variabile pentru ca sunt zece cazuri posibile.
    :return: (regex, numarul de paranteze deschise: "(")
    """
    ans = None
    aux1 = None
    aux2 = None
    aux3 = None
    f1 = False
    f2 = False
    f3 = False
    f4 = False
    no1, no2 = None, None
    p = 0
    aux_p = 0

    if len(str) == 0:
        return RegEx(EMPTY_STRING), 0

    if len(str) == 1:
        if str == ".":
            return RegEx(SYMBOL_ANY), 0
        else:
            return RegEx(SYMBOL_SIMPLE, str), 0

    for i, x in enumerate(str):

        if f4 and x != ")":
            continue
        elif f4:
            aux_p -= 1
            f4 = False
            if ans is None:
                ans = aux3
                aux1 = None
                aux3 = None
            else:
                ans = RegEx(CONCATENATION, ans, aux3)
                aux3 = None
            continue

        if f2 and x != "]":
            continue
        elif f2:
            f2 = False

        if f3:
            if no1 is None:
                no1 = get_number(str[i::])
            if x == "}":
                if no2 is None:
                    ans = RegEx(RANGE, ans, (no1, no1))
                f3 = False
            elif no1 is not None:
                if x == ",":
                    no2 = get_number(str[i+1::])
                    ans = RegEx(RANGE, ans, (no1, no2))

            continue

        if ans is None and x in alfabet:
            ans = RegEx(SYMBOL_SIMPLE, x)
        elif x in alfabet:
            ans = RegEx(CONCATENATION, ans, RegEx(SYMBOL_SIMPLE, x))
            aux1 = RegEx(SYMBOL_SIMPLE, x)
        elif x == ".":
            ans = RegEx(CONCATENATION, ans, RegEx(SYMBOL_ANY))
        elif x == "*":
            if aux1 is not None:
                ans = RegEx(CONCATENATION, ans.lhs, RegEx(STAR, aux1))
            else:
                ans = RegEx(STAR, ans)
        elif x == "+":
            if aux1 is not None:
                ans = RegEx(CONCATENATION, ans.lhs, RegEx(PLUS, aux1))
            else:
                ans = RegEx(PLUS, ans)
        elif x == "?":
            if aux1 is not None:
                ans = RegEx(CONCATENATION, ans.lhs, RegEx(MAYBE, aux1))
            else:
                ans = RegEx(MAYBE, ans)
        elif x == "|":
            if not f1:
                aux2 = ans
                f1 = True
            else:
                aux2 = RegEx(ALTERNATION, aux2, ans)
            ans = None
        elif x == "[":
            f2 = True
            aux3 = symbol_set(str[i+1::])
            if ans is None:
                ans = aux3
        elif x == "{":
            f3 = True
        elif x == "(":
            p += 1
            f4 = True
            aux3, aux_p = str_to_regex(str[i + 1::])
            aux1 = aux3
            aux_p += 1
        elif x == ")":
            if not f4 and aux_p == 0:
                break
            aux_p -= 1

    if f1:
        ans = RegEx(ALTERNATION, aux2, ans)

    return ans, p
