inp2_c = "500x1 + 300x2 - 30x3"
inp2="""200x1 + 100x2 <= 1200
x1 + x2 - x3 >= 7"""

inp1_c = "2x1+x2+x3"
inp1 = """x1+x2>=3
x1+x3<=3
x1,x2,x3>=0"""

#promjeni u 

inp3="""-x1-x2+x3 =-5
x1+x2+x4=8
x1+x5=6
x2+x6=6"""

inp4="""-2x1 -x1 -> min
x1 + x2 -x3 = 5
x1 + x2 + x4 = 8
x1 + x5 =6
x2 + x6 =6
x1,x2,x3,x4,x5,x6 >= 0"""

import re
import numpy as np

def get_pairs(string):
    pairs = re.findall(r"\-[0-9]*x[0-9]|\+[0-9]*x[0-9]|^[0-9]*x[0-9]",string)
    
    out = []
    for elem in pairs:
        val_str, idx = elem.split("x")
        if val_str == "+" or val_str == "-" or val_str == "":
            if val_str == "-":
                out.append((int(idx),-1))
            else:
                out.append((int(idx),1))
        else:
            out.append((int(idx),int(val_str)))
    
    return out

def find_max(arr):
    maxx = 0
    for elem in arr:
        if elem[0] > maxx:
            maxx = elem[0]
            
    return maxx
    


def parse_lin(fc_string, cond_string, min_max):
    cond_string = re.sub(" ", "", cond_string)
    fc_string = re.sub(" ", "", fc_string)
    lines = cond_string.split("\n")
    
    flag = False
    if re.search(",",lines[-1]) or re.match("x[0-9]>=0",lines[-1]):
        conditions = lines[0:-1]
    else:
        conditions = lines
        flag = True
    
    equations_pile = []
    equation_types = []
    maxx = 1
    colls_count = 0
    for condition in conditions:
        if re.search(r">=",condition):
            a, b = condition.split(">=")
            pairs = get_pairs(a)
            equations_pile += [(pairs,int(b))]
            equation_types.append(0)
            colls_count +=1
        elif re.search(r"<=",condition):
            a, b = condition.split("<=")
            pairs = get_pairs(a)
            equations_pile += [(pairs,int(b))]
            equation_types.append(1)
            colls_count +=1
        else:
            a, b = condition.split("=")
            pairs = get_pairs(a)
            equations_pile += [(pairs,int(b))]
            equation_types.append(2)
            
        if find_max(pairs) > maxx:
            maxx = find_max(pairs)

    
    collumns = maxx + colls_count
    
    A = []
    b = []
    counter = 0
    for elem, etype in zip(equations_pile, equation_types):
        row = [0]*collumns
        for e in elem[0]:
            row[e[0]-1] = e[1]
         
        if etype == 0:
            row[maxx+counter] = -1
            counter += 1
        elif etype == 1:
            row[maxx+counter] = 1
            counter += 1
        
        b.append(elem[1])
        A.append(row)
    
    jedn = fc_string
    pairs = get_pairs(jedn)
    c = [0]*collumns
    for e in pairs:
        c[e[0]-1] =  e[1]
        
    if min_max:
        c = [x*-1 for x in c]

    if not flag:
        gt_zeros = lines[-1]
        xs, _ = gt_zeros.split(">=")
        xs = xs.split(",")
    check_xs = [0]*maxx
    if not flag:
        for x in xs:
            _, num = x.split("x")
            check_xs[int(num)-1] = 1
    

    if sum(check_xs) < maxx:
        difference = maxx-sum(check_xs)
        c += [0]*difference
        for idx, x in enumerate(check_xs):
            new_A = []
            if x == 0:
                for elem in A:
                    new_elem = elem
                    new_elem.append(elem[idx]*-1)
                    new_A.append(new_elem)
                    
                A = new_A.copy()
            
    return np.array(A), np.array(b), np.array(c)
            
print(parse_lin(inp1_c, inp1, False))
            
    

