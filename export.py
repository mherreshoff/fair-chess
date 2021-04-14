#!/usr/bin/env python

import json
import pickle
import random
import sys

import chess

FAIRNESS_THRESHOLD = 10
N = int(sys.argv[1])
with open(f'ply{N}_scored_boards.pkl', 'rb') as f:
    scored_boards = pickle.load(f)

fair_boards = [(s, b) for s,b in scored_boards if abs(s) <= FAIRNESS_THRESHOLD]
fair_boards = sorted(fair_boards, key=lambda sb: sb[1].fen())

print(f"{len(scored_boards)} total boards, {len(fair_boards)} qualify as fair.")

start = chess.Board()
output = []
for s, b in fair_boards:
    output.append({
        'score': s,
        'fen': b.fen(),
        'moves': [m.uci() for m in b.move_stack],
        'san': start.variation_san(b.move_stack)})

with open(f'ply{N}_fairchess.json', 'w') as f:
    json.dump(output, f)
