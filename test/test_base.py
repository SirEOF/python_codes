from collections import Counter

l = sum(([i] * i for i in range(100)), [])

lc = Counter(l)

