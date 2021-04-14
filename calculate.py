#!/usr/bin/env python

import multiprocessing
import pickle
import sys

import chess
import chess.engine

MATE_SCORE = 100000

engine = None
def init_engine():
    global engine
    engine = chess.engine.SimpleEngine.popen_uci("stockfish", debug=True)


def top_children(scored_board, tolerance=50):
    score, board = scored_board
    def score2num(score):
        return score.pov(board.turn).score(mate_score=MATE_SCORE)
    results = engine.analyse(board, limit=chess.engine.Limit(depth=20), multipv=5)
    top_score = score2num(results[0]['score'])
    result = []
    print(f"    FEN = {board.fen()}")
    for i, r in enumerate(results):
        move = r['pv'][0]
        score = score2num(r['score'])
        if score < top_score - tolerance: continue # This move is bad.
        new_board = board.copy()
        new_board.push(move)
        print(f"        score={score} new_board={new_board.fen()}")
        result.append((score, new_board))
    return result


def uniquify(scored_boards):
    results = {}
    for s, b in scored_boards:
        key = b.fen()
        if key not in results:
            results[key] = (s, b)
    return [results[k] for k in sorted(results.keys())]



if __name__ == '__main__':
    N = int(sys.argv[1])
    scored_boards = [(None, chess.Board())]
    with multiprocessing.Pool(None, init_engine) as pool:
        for k in range(N):
            scored_boards = [sb for sbs in pool.imap(top_children, scored_boards) for sb in sbs]
            print(f"ply={k+1} #scored_boards = {len(scored_boards)}")
            scored_boards = uniquify(scored_boards)
            print(f"ply={k+1} #scored_boards unique = {len(scored_boards)}")
    if N % 2 == 0: # Scores were for black.
        scored_boards = [(-s,b) for s,b in scored_boards]

    with open(f'ply{N}_scored_boards.pkl', 'wb') as f:
        pickle.dump(scored_boards, f)
