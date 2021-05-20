import re
import sys

def main(path):
    p = re.compile(r'^-{60}\n$')

    # 0 -> goal lines, 1 -> result lines
    int_lines = [[], []]

    mp = {
        'post-condition': 'postcond',
        'pre-condition': 'precond',
        'lemma': 'lemma',
        'assertion': 'assert',
        'property': 'prop',
        'variant': 'var'
    }

    res_mp = {
        'unknown': 'unch',
        'valid': 'prov',
        'failed': 'counter',
        'false': 'counter',
        'invalid': 'inv'
    }

    with open(path, 'r') as f:
        lines = f.readlines()
        for i, pair in enumerate(zip(lines, lines[1:])):
            for _ in range(2):
                if p.match(pair[_]) and pair[1 - _] == '\n':
                    int_lines[_].append(i + 2 - 3 * _)

        if len(int_lines[0]) is not len(int_lines[1]):
            sys.exit('Could not parse frama-c output.')

        goals = {}
        for gl, res in zip(int_lines[0], int_lines[1]):
            # Assign (line number, goal name, result) for each goal line number in goal lines.
            # Goal name relates to the section name.
            line = lines[gl].strip()
            words = line.split()
            res_words = lines[res].strip().split()
            result = res_words[res_words.index('returns') + 1].lower()
            # len('Goal ') == 5
            goal_str = line[5:line.find('(') - 1].lower()
            if 'invariant' in goal_str:
                goal_str = 'inv'
            else:
                for key in mp:
                    if key in goal_str:
                        goal_str = mp[key]
                        break
            goals[gl] = (int(re.search(r'\d+', words[words.index('line') + 1]).group()), goal_str, res_mp.get(result, result))

        print(goals)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        sys.exit("Usage: python3 parse.py file.txt")
    sys.exit(main(args[0]))
