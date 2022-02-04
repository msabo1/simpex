import math
import parser
import random

import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__, static_url_path='', static_folder='dist/simplex')

# -1 -1 1 0 0 0
# 1 1 0 1 0 0
# 1 0 0 0 1 0
# 0 1 0 0 0 1

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/solve', methods=['POST'])
def solve():
    try:
        A, b, c = None, None, None
        if request.json['mode'] == 'text':
            A, b, c = parser.parse_lin(request.json['func'], request.json['conditions'], True if request.json['goal'] == 'max' else False)
        elif request.json['mode'] == 'matrix':
            A = np.array(np.mat(request.json['A'].replace('\n', ';')))
            b = np.fromstring(request.json['b'], sep=' ')
            c = np.fromstring(request.json['c'], sep=' ')
        strategy = request.json['strategy']

        table, base, tables, bases, pivots, A2, b2, c2, status = simplex(A, b, c, strategy)
        return jsonify({'status': status, 'table': table.tolist(), 'base': base, 'tables': tables, 'bases': bases, 'pivots': pivots, 'A': A.tolist(), 'b': b.tolist(), 'c': c.tolist(), 'A2': A2.tolist(), 'b2': b2.tolist(), 'c2': c2.tolist(), 'strategy': request.json['strategy'], 'mode': request.json['mode'], 'goal': request.json['goal']})
    except Exception as e:
        print(e)
        return jsonify({'status': 4})

def firstPhase(A, b, tables, bases, pivots, pivot_strategy):
    # print(A)
    shape = A.shape
    
    for i in range(shape[0]):
        if b[i] < 0:
            b[i] = -b[i]
            A[i] = -A[i]
    A = np.concatenate((A, np.eye(A.shape[0])), axis=1)
    c = np.array([[0 if i < shape[1] else 1 for i in range(A.shape[1])]])
    base = [*range(shape[1], shape[1] + shape[0])]

    table = np.empty((A.shape[0] + 1, A.shape[1] + 1))
    table[0, 0] = -b.sum()
    table[0, 1:] = c - c.T[base].T@A
    table[1:, 0] = b.T
    table[1:, 1:] = A[:, :]
    tables[0].append(table.tolist())
    bases[0].append(base[:])
    # print (table)
    for i in range(2000):
        table, base, pivot, pivotStatus = simplexStep(table, base, pivot_strategy)
        if pivotStatus == 0:
            if math.isclose(table[0, 0], 0, abs_tol=1e-9):
                return table, base, A, b, c, 0
            else:
                return table, base, A, b, c, 1
        if pivotStatus == 1:
            return table, base, A, b, c, 1
        tables[0].append(table.tolist())
        bases[0].append(base[:])
        pivots[0].append(pivot)
        # print(table)
    return None, None, None, None, None, 3
        

def secondPhase(A, b, c, table, base, tables, bases, pivots, pivot_strategy):
    table = table[0:, 0:A.shape[1] + 1]
    table[0, 0] = -c.T[base].T@table[1:, 0]
    table[0, 1:] = c - c.T[base].T@table[1:, 1:]
    tables[1].append(table.tolist())
    bases[1].append(base[:])
    for i in range(2000):
        table, base, pivot, pivotStatus = simplexStep(table, base, pivot_strategy)
        if pivotStatus == 0:
            return table, base, 0
        if pivotStatus == 1:
            return table, base, 2
        tables[1].append(table.tolist())
        bases[1].append(base[:])
        pivots[1].append(pivot)
        #print(table)
    return None, None, 3

def simplex(A, b, c, strategy):
    tables = [[], []]
    bases = [[], []]
    pivots = [[], []]
    pivot_strategy = None
    if strategy == 'bland':
        pivot_strategy = lambda table, base: bland(table, base)
    elif strategy == 'lex':
        pivot_strategy = lambda table, base: lex(table)
    elif strategy == 'rand':
        pivot_strategy = lambda table, base: rand(table)
    table, base, A2, b2, c2, status = firstPhase(A, b, tables, bases, pivots, pivot_strategy)
    print(table)
    if status == 1 or status == 3:
        return table, base, tables, bases, pivots, A2, b2, c2, status
    table, base, status = secondPhase(A, b, c, table, base, tables, bases, pivots, pivot_strategy)
    print(table)
    return table, base, tables, bases, pivots, A2, b2, c2, status

def bland(table, base):
    status = 0
    for j in range(1, table.shape[1]):
        if (not math.isclose(table[0, j], 0, abs_tol=1e-9)) and table[0, j] < 0:
            status = 1
            i = None
            for ii in range(1, table.shape[0]):
                if (not math.isclose(table[ii, j], 0, abs_tol=1e-9)) and table[ii, j] > 0 and (i == None or (table[ii, 0]/table[ii, j] < table[i, 0]/table[i, j] or (table[ii, 0]/table[ii, j] == table[i, 0]/table[i, j] and base[ii] < base[i]))):
                    i = ii
            if i != None:
                status = 2
                return (i, j), status
    return (None, None), status

def lex(table):
    status = 0
    for j in range(1, table.shape[1]):
        if (not math.isclose(table[0, j], 0, abs_tol=1e-9)) and table[0, j] < 0:
            status = 1
            i = None
            for ii in range(1, table.shape[0]):
                if (not math.isclose(table[ii, j], 0, abs_tol=1e-9)) and table[ii, j] > 0 and (i == None or (isLexSmaller(table[ii]/table[ii, j], table[i]/table[i, j]))):
                    i = ii
            if i != None:
                status = 2
                return (i, j), status
    return (None, None), status

def isLexSmaller(a, b):
    for i in range(len(a)):
        if a[i] != 0 or b[i] != 0:
            if a[i] < b[i]:
                return True
            elif a[i] > b[i]:
                return False
    return True

def rand(table):
    status = 0
    j_s = []
    ji_s = []
    for j in range(1, table.shape[1]):
        if (not math.isclose(table[0, j], 0, abs_tol=1e-9)) and table[0, j] < 0:
            status = 1
            i_s = []
            i = None
            for ii in range(1, table.shape[0]):
                if (not math.isclose(table[ii, j], 0, abs_tol=1e-9)) and table[ii, j] > 0 and (i == None or table[ii, 0]/table[ii, j] <= table[i, 0]/table[i, j]):
                    if ii != i:
                        i = ii
                        i_s = []
                    i_s.append(ii)
            ji_s.append(i_s)
            if len(i_s) > 0:
                j_s.append(j)
    if len(j_s) == 0:
        return (None, None), status
    j = random.randint(0, len(j_s) - 1)
    i = random.choice(ji_s[j])
    status = 2
    return (i, j_s[j]), status

def simplexStep(table, base, pivotStrategy):
    pivot, pivotStatus = pivotStrategy(table, base)
    if pivotStatus == 0 or pivotStatus == 1:
        return table, base, (None, None), pivotStatus
    print(pivot)
    table[pivot[0]] = table[pivot[0]]/table[pivot[0], pivot[1]]
    for i in range(table.shape[0]):
        if i != pivot[0]:
            #print(table[pivot[0]])
            table[i] = table[i] - table[i, pivot[1]]*table[pivot[0]]
    base[pivot[0] - 1] = pivot[1] - 1
    return table, base, pivot, pivotStatus

A = np.array([[-1, -1, 1, 0, 0, 0],
              [1, 1, 0, 1, 0, 0],
              [1, 0, 0, 0, 1, 0],
              [0, 1, 0, 0, 0, 1]], dtype=np.float64)
b = np.array([-5, 8, 6, 6], dtype=np.float64)
c = np.array([-1, -2, 0, 0, 0, 0], dtype=np.float64)
# table, base, tables, bases, pivots = simplex(A, b, c)
# print(base)


