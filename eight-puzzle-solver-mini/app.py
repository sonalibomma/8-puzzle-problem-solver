from flask import Flask, request, jsonify, render_template
import sqlite3, time, heapq

app = Flask(__name__)
DB = "puzzle.db"

GOAL = (1,2,3,4,5,6,7,8,0)

def connect():
    return sqlite3.connect(DB)

def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_state TEXT,
            moves INTEGER,
            nodes INTEGER,
            time_ms INTEGER
        )
    """)
    con.commit()
    con.close()

def manhattan(state):
    d = 0
    for i,v in enumerate(state):
        if v == 0: continue
        gi = GOAL.index(v)
        d += abs(i%3 - gi%3) + abs(i//3 - gi//3)
    return d

def neighbors(s):
    z = s.index(0)
    res = []
    for d in [-1,1,-3,3]:
        nz = z + d
        if 0 <= nz < 9 and abs(z%3 - nz%3) <= 1:
            l = list(s)
            l[z], l[nz] = l[nz], l[z]
            res.append(tuple(l))
    return res

def solvable(s):
    a = [x for x in s if x != 0]
    inv = sum(a[i] > a[j] for i in range(len(a)) for j in range(i+1,len(a)))
    return inv % 2 == 0

def astar(start):
    pq = [(manhattan(start),0,start)]
    seen = set()
    parent = {}
    nodes = 0

    while pq:
        f,g,s = heapq.heappop(pq)
        if s in seen: continue
        seen.add(s)
        nodes += 1

        if s == GOAL:
            path = [s]
            while s in parent:
                s = parent[s]
                path.append(s)
            return path[::-1], nodes

        for n in neighbors(s):
            if n not in seen:
                parent[n] = s
                heapq.heappush(pq,(g+1+manhattan(n),g+1,n))
    return None, nodes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    nums = list(map(int, data["state"].split()))
    start = tuple(nums)

    if len(nums) != 9 or sorted(nums) != list(range(9)):
        return jsonify({"error":"Invalid input"}),400
    if not solvable(start):
        return jsonify({"error":"Unsolvable puzzle"}),400

    t0 = time.time()
    path, nodes = astar(start)
    t_ms = int((time.time()-t0)*1000)
    moves = len(path)-1

    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO runs (input_state,moves,nodes,time_ms) VALUES (?,?,?,?)",
        (" ".join(map(str,start)),moves,nodes,t_ms)
    )
    con.commit()
    con.close()

    return jsonify({
        "moves":moves,
        "nodes":nodes,
        "time":t_ms,
        "path":[list(p) for p in path]
    })

@app.route("/history")
def history():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT input_state,moves,nodes,time_ms FROM runs ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    con.close()
    return jsonify(rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
