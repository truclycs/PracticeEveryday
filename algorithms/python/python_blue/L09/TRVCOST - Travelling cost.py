import queue
MAX = 501
INF = int(1e9)

class Node:
    def __init__(self, id = 0, dist = 0):
        self.id = id
        self.dist = dist
    def __lt__(self, other):
        return self.dist <= other.dist

def Dijkstra(s):
    pq = queue.PriorityQueue()
    pq.put(Node(s, 0))
    dist[s] = 0
    while not pq.empty():
        top = pq.get()
        u = top.id 
        w = top.dist 
        for v in graph[u]:
            if w + v.dist < dist[v.id]:
                dist[v.id] = w + v.dist 
                pq.put(Node(v.id, dist[v.id]))

n = int(input())
graph = [[] for i in range(MAX + 1)]
dist = [INF for i in range(MAX + 1)]
for i in range(n):
    u, v, w = map(int, input().split())
    graph[u].append(Node(v, w))
    graph[v].append(Node(u, w))

s = int(input())
Dijkstra(s)
q = int(input())
for i in range(q):
    e = int(input())
    if dist[e] == INF:
        print("NO PATH")
    else:
        print(dist[e])
