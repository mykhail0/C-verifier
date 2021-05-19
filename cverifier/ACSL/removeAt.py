import sys
import os

def removeAt(s):
    if any(x in s for x in ['/*', '//']):
        # do not remove the first '@'
        return s[:s.find('@') + 1] + s[s.find('@') + 1:].replace('@', ' ')
    else:
        return s.replace('@', ' ')

# Removes additional '@' characters from ACSL.
def main(Cfile):
    try:
        os.mkdir('noAt')
    except:
        pass
    with open(Cfile, 'r') as f:
        with open('noAt/@' + Cfile, 'w') as r:
            s = f.readline()
            while s:
                r.write(removeAt(s))
                s = f.readline()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        exit("Usage: python3 removeAt.py path/to/file.c")
    sys.exit(main(args[0]))
