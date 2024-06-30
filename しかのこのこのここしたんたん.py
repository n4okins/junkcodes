import random
from collections import deque

"""
しかのこのこのここしたんたん*3が出るまでしかのこのこのここしたんたんする
"""

q = deque(maxlen=30)
src = ["しか", "の", "こ", "のこのこ", "こしたんたん"]
while True:
    q.append(random.choice(src))
    text = "".join(q)
    print(text, end="")
    if text.endswith("しかのこのこのここしたんたん" * 3):
        break
