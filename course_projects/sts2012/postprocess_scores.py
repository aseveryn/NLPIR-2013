import sys
if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s sentences.txt scores.txt" % sys.argv[0]
    exit(1)

orig = []
for l in open(sys.argv[1]):
    orig.append([x.strip() for x in l.lower().split("\t")])

scores = map(float, open(sys.argv[2]).readlines())

if len(orig) != len(scores):
    print >>sys.stderr, "Error: inputs should have the same number of lines"
    exit(1)

f = open(sys.argv[2], 'w')
for i, s in enumerate(scores):
    if orig[0] == orig[1]:
        s = 5.
    if s > 5:
        s = 5.
    if s < 0:
        s = 0.
    print >>f, s
f.close()
