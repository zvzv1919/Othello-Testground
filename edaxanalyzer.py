import timeit

import numpy as np
import re
import subprocess
import os
from utils import timer
from multiprocessing import Process, Queue

# globals
BOARD_SIZE = 64 # total number of squares in a board
RANDOM_OBF_BATCH_SIZE = 100000 # file I/O batch size for random_obf. Single process takes ~5s to process a batch of
# this size on intel i9
RANDOM_OBF_PROCESSES = 8 # number of worker procs random_obf utilize


def compute_one_verbose2_problem(lines):

    lines.reverse()
    for x in lines:
        print(x)
        m = re.search(
            r"([0-9]+)\s+([-+][0-9]{2})\s+([0-9.:]+)\s+([0-9]+)\s+([0-9]*)\s+(([a-hA-H][1-8]\s?)+)",
            x,
        )
        if m is not None:
            depth = int(m.group(1))
            score = m.group(2)
            nodes = int(m.group(4))
            principal_variation = m.group(6).lower().strip().split(" ")
            return {
                "perfect": True,
                "depth": depth,
                "accuracy": 100,
                "nodes": nodes,
                "score": score,
                "principal_variation": principal_variation,
            }

        m = re.search(
            r"([0-9]+)@([0-9]+)%\s+([-+][0-9]{2})\s+([0-9.:]+)\s+([0-9]+)\s+([0-9]*)\s+(([a-hA-H][1-8]\s?)+)",
            x,
        )
        if m is not None:
            depth = int(m.group(1))
            accuracy = int(m.group(2))
            score = int(m.group(3))
            nodes = int(m.group(5))
            principal_variation = m.group(7).lower().strip().split(" ")
            assert accuracy < 100
            return {
                "perfect": False,
                "depth": depth,
                "accuracy": accuracy,
                "nodes": nodes,
                "score_lowerbound": score,
                "score_upperbound": score,
                "principal_variation": principal_variation,
            }

    return None

def extract_scores(solution_file):
    scores = []
    with open(solution_file, 'r') as file:
        # Skip the header and the line below it
        next(file)
        next(file)

        for line in file:
            if not line.strip():
                continue  # Skip any empty lines

            parts = line.split('|')[1].split()
            depth = int(parts[0].strip())
            score = parts[1].strip()

            # Check if the depth is 16, then extract the score
            # assert(depth == 16)
            scores.append(int(score))

    return scores

def obf_generator(q, state_cnt, empties):
    """
        Generate obf states and batch write to a queue.
        :param empties: number of empties
        :param state_cnt: number of states to generate
        :param q: mp/mt queue
        :return:
    """
    result = []
    batch_cnt = 0
    # print(state_cnt)
    for _ in range(state_cnt):

        arr = np.array(['-'] * BOARD_SIZE)
        indices = np.random.choice(64, size=(BOARD_SIZE - empties), replace=False)
        replacements = np.random.choice(['X', 'O'], size=(BOARD_SIZE - empties))
        arr[indices] = replacements
        # always solve for black
        result.append(''.join(arr) + " X;")

        batch_cnt += 1
        if batch_cnt >= RANDOM_OBF_BATCH_SIZE:
            q.put('\n'.join(result) + '\n')
            result = []
            batch_cnt = 0

    if len(result) > 0:
        q.put('\n'.join(result) + '\n')

def file_writer(q, file_path):
    """
        consume from mp/mt queue and writes to a file
        :param file_path: file to write too
        :param q: mp/mt queue
        :return:
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        while True:
            data = q.get()
            if data == "STOP":
                break
                # Make sure \n is appended in {data}
            f.write(f'{data}')

@timer
def random_obf(empties, cnt, filename):
    """
        Generate obf file containing many game states all with the same number of empties. NOT guarenteed to be a state reachable from normal game play.
        :param empties: number of empties
        :param cnt: number of states to generate\
        :param filename: filename
        :return:
    """
    def data_producer(data, q):
        q.put(data)

    q = Queue()
    writer_process = Process(target=file_writer, args=(q, filename))
    writer_process.start()

    workers = []
    for i in range(RANDOM_OBF_PROCESSES - 1):
        p = Process(target=obf_generator, args=(q, cnt // RANDOM_OBF_PROCESSES, empties))
        workers.append(p)
        p.start()
    remaining_cnt = cnt - cnt // RANDOM_OBF_PROCESSES * (RANDOM_OBF_PROCESSES-1)
    last_worker = Process(target=obf_generator, args=(q, remaining_cnt, empties))
    workers.append(last_worker)
    last_worker.start()

    for p in workers:
        p.join()
    q.put("STOP")
    writer_process.join()

def analyze_obf_entry(obf_entry, lvl):
    """
        Aux function, takes in an obf entry (a game state), generates 2 edax search results, one at lvl1 (depth 0),
        one at @param lvl, ideally reaching endgame for accuracy. Used to enhance the eval function.
        :param obf_entry: game state to analyze
        :param lvl: high eval lvl
        :return: (lvl1_result, lvl{lvl}_result)
    """
    with open("resources/tmp_obf_file", "w") as f:
        f.write(obf_entry)
    proc = subprocess.Popen(
        ['./bin/mEdax', '-solve', "tmp_obf_file", '-l', str(lvl)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        )
    result_stdout = []
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            result_stdout.append(line.rstrip())

    analyze = compute_one_verbose2_problem(result_stdout)

    print(analyze["depth"])
    print(analyze["score"])

if __name__ == '__main__':
    random_obf(12, 100, "data/test/obf")

    # extract_scores("a.txt")
    # analyze_obf_entry("X-OOOOXOO--OO--OX-XOXXXXXO--XO-OOOX---OO--OO-OOOXXOOOOXXXOXXO-XX X;", 16)
