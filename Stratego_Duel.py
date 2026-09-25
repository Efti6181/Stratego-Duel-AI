import pygame, sys, random
import heapq
pygame.init()

W,H=1100,680; CS=58; OX,OY=8,55; NR,NC=10,10
BG=(25,25,45); GR=(50,50,80)
HC=(195,55,55); AC=(50,110,200); SL=(255,210,0)
MV=(50,190,50); AK=(210,70,25); TX=(210,220,250)
DM=(100,125,165); GD=(255,190,40); PN=(15,20,40)
PB=(50,70,130); WN=(20,150,70); LS=(150,20,20)
BRIDGE=(60,90,60)
BRIDGE_SET={(3,3),(3,4),(4,3),(4,4),(6,3),(6,4),(7,3),(7,4)}
LAKE_SET=set()
HR=[6,7,8,9]; AR=[0,1,2,3]
PD={"F":("Flag","F",1,False,1000),"B":("Bomb","B",6,False,30),
    10:("Marshal","10",1,True,100),9:("General","9",1,True,90),
    8:("Colonel","8",2,True,70),7:("Major","7",3,True,55),
    6:("Captain","6",4,True,45),5:("Lieut","5",4,True,35),
    4:("Sgt","4",4,True,25),3:("Miner","3",5,True,35),
    2:("Scout","2",8,True,20),1:("Spy","1",1,True,40)}
ORD=["F","B",10,9,8,7,6,5,4,3,2,1]
RPX=OX+NC*CS+30

screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("Stratego Duel")
clock=pygame.time.Clock()
fT=pygame.font.SysFont("consolas",20,bold=True)
fL=pygame.font.SysFont("consolas",16,bold=True)
fM=pygame.font.SysFont("consolas",14,bold=True)
fS=pygame.font.SysFont("consolas",12)
fXS=pygame.font.SysFont("consolas",11)
fB=pygame.font.SysFont("consolas",30,bold=True)
TICK=0

def tx(s,f,c,x,y,cx=False):
    su=f.render(str(s),True,c); r=su.get_rect()
    if cx: r.center=(x,y)
    else: r.topleft=(x,y)
    screen.blit(su,r)
def cpx(r,c): return OX+c*CS,OY+r*CS
def pxc(px,py):
    c=(px-OX)//CS; r=(py-OY)//CS
    if 0<=r<NR and 0<=c<NC: return int(r),int(c)
    return None,None
def mdist(r1,c1,r2,c2): return abs(r1-r2)+abs(c1-c2)

class Piece:
    def __init__(self,rank,owner):
        self.rank=rank; self.owner=owner
        self.revealed=False; self.moved=False
        self.name=PD[rank][0]; self.sym=PD[rank][1]
        self.can_move=PD[rank][3]
    def fight(self,d):
        a,dv=self.rank,d.rank
        if dv=="F": return "a"
        if dv=="B": return "a" if a==3 else "d"
        if a==1 and dv==10: return "a"
        if not(isinstance(a,int) and isinstance(dv,int)): return "d"
        return "a" if a>dv else "d" if a<dv else "b"
    def copy(self):
        q=Piece(self.rank,self.owner)
        q.revealed=self.revealed; q.moved=self.moved; return q

class Board:
    def __init__(self): self.g=[[None]*NC for _ in range(NR)]
    def ok(self,r,c): return 0<=r<NR and 0<=c<NC
    def get(self,r,c): return self.g[r][c] if self.ok(r,c) else None
    def put(self,r,c,p): self.g[r][c]=p
    def rem(self,r,c):
        p=self.g[r][c]; self.g[r][c]=None; return p
    def moves(self,r,c):
        p=self.get(r,c)
        if not p or not p.can_move: return[]
        res=[]
        for dr,dc in[(-1,0),(1,0),(0,-1),(0,1)]:
            if p.rank==2:
                nr,nc=r+dr,c+dc
                while self.ok(nr,nc) and (nr,nc) not in LAKE_SET:
                    q=self.get(nr,nc)
                    if q is None: res.append((nr,nc))
                    else:
                        if q.owner!=p.owner: res.append((nr,nc))
                        break
                    nr+=dr; nc+=dc
            else:
                nr,nc=r+dr,c+dc
                if self.ok(nr,nc) and (nr,nc) not in LAKE_SET:
                    q=self.get(nr,nc)
                    if q is None or q.owner!=p.owner:
                        res.append((nr,nc))
        return res
    def all_moves(self,owner):
        res=[]
        for r in range(NR):
            for c in range(NC):
                p=self.get(r,c)
                if p and p.owner==owner and p.can_move:
                    for tr,tc in self.moves(r,c):
                        res.append((r,c,tr,tc))
        return res
    def do(self,fr,fc,tr,tc):
        a=self.get(fr,fc); d=self.get(tr,tc)
        info={"type":"move","a":a,"d":d,"aw":False,"dw":False,"bt":False,"flag":False}
        if d is None:
            self.g[fr][fc]=None; self.g[tr][tc]=a; a.moved=True
        else:
            a.revealed=True; d.revealed=True; info["type"]="combat"
            if d.rank=="F":
                info["flag"]=True; info["aw"]=True
                self.g[fr][fc]=None; self.g[tr][tc]=None
            else:
                rv=a.fight(d)
                if rv=="a":
                    info["aw"]=True; self.g[fr][fc]=None; self.g[tr][tc]=a; a.moved=True
                elif rv=="d":
                    info["dw"]=True; self.g[fr][fc]=None
                else:
                    info["bt"]=True; self.g[fr][fc]=None; self.g[tr][tc]=None
        return info
    def flag(self,owner):
        for r in range(NR):
            for c in range(NC):
                p=self.get(r,c)
                if p and p.owner==owner and p.rank=="F": return(r,c)
        return None
    def copy(self):
        b=Board()
        for r in range(NR):
            for c in range(NC):
                p=self.g[r][c]; b.g[r][c]=p.copy() if p else None
        return b
    def pieces(self,owner):
        res=[]
        for r in range(NR):
            for c in range(NC):
                p=self.g[r][c]
                if p and p.owner==owner: res.append((r,c,p))
        return res
    def count(self,owner):
        return sum(1 for r in range(NR) for c in range(NC) if self.g[r][c] and self.g[r][c].owner==owner)

class AI:
    def __init__(self):
        self.known={}
        self.turn_count=0
        self.last_moves=[]
        self.scout_visited={}

    def remember(self,r,c,rank):
        self.known[(r,c)]=rank

    def moved_piece(self,fr,fc,tr,tc):
        if (fr,fc) in self.known:
            rank=self.known.pop((fr,fc))
            self.known[(tr,tc)]=rank

    def find_flag(self,board):
        return board.flag("human")

    def threats_to(self,board,r,c,piece):
        threats=[]
        if not isinstance(piece.rank,int): return threats
        for hr,hc,hp in board.pieces("human"):
            if hp.revealed and isinstance(hp.rank,int) and hp.rank>piece.rank:
                d=mdist(r,c,hr,hc)
                if d<=3: threats.append((hr,hc,hp,d))
        return threats

    def flag_threats(self,board):
        af=board.flag("ai")
        if not af: return[]
        threats=[]
        for hr,hc,hp in board.pieces("human"):
            if hp.can_move:
                d=mdist(hr,hc,af[0],af[1])
                if d<=5: threats.append((hr,hc,hp,d))
        threats.sort(key=lambda x:x[3])
        return threats

    def best_escape(self,board,r,c,piece,thr,thc):
        mvs=board.moves(r,c)
        best=None; best_d=-1
        for mr,mc in mvs:
            target=board.get(mr,mc)
            if target: continue
            nd=mdist(mr,mc,thr,thc)
            if nd>best_d: best_d=nd; best=(r,c,mr,mc)
        return best

    def eval_board(self,board):
        vm={"F":1000,"B":30,10:100,9:90,8:70,7:55,6:45,5:35,4:25,3:35,2:20,1:40}
        score=0
        hf=board.flag("human"); af=board.flag("ai")
        min_hf=99; min_af=99
        for r in range(NR):
            for c in range(NC):
                p=board.get(r,c)
                if not p: continue
                v=vm.get(p.rank,10)
                if p.owner=="ai":
                    score+=v*2
                    if p.can_move:
                        score+=r*3
                        if hf:
                            d=mdist(r,c,hf[0],hf[1])
                            if d<min_hf: min_hf=d
                            if isinstance(p.rank,int) and p.rank>=7 and d<=4:
                                score+=(5-d)*25
                else:
                    score-=v*2
                    if p.can_move:
                        score-=(NR-1-r)*3
                        if af:
                            d=mdist(r,c,af[0],af[1])
                            if d<min_af: min_af=d
        if hf and min_hf<99: score+=max(0,(12-min_hf))*10
        if af and min_af<99:
            if min_af<=2: score-=250
            elif min_af<=4: score-=100
        for hr,hc,hp in board.pieces("human"):
            if hp.revealed and isinstance(hp.rank,int):
                for ar,ac,ap in board.pieces("ai"):
                    if ap.can_move and isinstance(ap.rank,int) and ap.rank>hp.rank:
                        d=mdist(ar,ac,hr,hc)
                        if d<=3: score+=(4-d)*12
        return score
    
    def score_move(self,board,m):
        fr,fc,tr,tc=m
        p=board.get(fr,fc); q=board.get(tr,tc)
        v=0
        hf=board.flag("human"); af=board.flag("ai")
        if isinstance(p.rank,int):
            threats=self.threats_to(board,fr,fc,p)
            if threats:
                closest=min(threats,key=lambda x:x[3])
                thr,thc=closest[0],closest[1]
                old_d=mdist(fr,fc,thr,thc); new_d=mdist(tr,tc,thr,thc)
                if new_d>old_d:
                    v+=250
                    if old_d==1: v+=300
                    if p.rank>=7: v+=150
                elif new_d<old_d:
                    v-=400
        if q and q.owner=="human":
            if q.rank=="F":
                v+=90000
            elif q.revealed:
                if isinstance(p.rank,int) and isinstance(q.rank,int):
                    if p.rank>q.rank: v+=500+(p.rank-q.rank)*30
                    elif p.rank==q.rank: v+=20
                    else: v-=700
                elif q.rank=="B":
                    if p.rank==3: v+=350
                    else: v-=900
            else:
                if not q.moved:
                    if p.rank==3: v+=120
                    elif p.rank==2: v+=15
                    else: v-=300
                else:
                    if isinstance(p.rank,int):
                        if p.rank>=8: v+=60
                        elif p.rank>=6: v+=30
                        elif p.rank<=4: v-=120
        if p.rank==2 and not q:
            adj_enemies=0
            for dr,dc in[(-1,0),(1,0),(0,-1),(0,1)]:
                nr,nc=tr+dr,tc+dc
                ep=board.get(nr,nc)
                if ep and ep.owner=="human": adj_enemies+=1
            if adj_enemies>=2: v-=200
            if adj_enemies==1: v-=50
            key=id(p)
            if key in self.scout_visited:
                if (tr,tc) in self.scout_visited[key]: v-=120
        if hf and isinstance(p.rank,int) and p.rank>=6:
            od=mdist(fr,fc,hf[0],hf[1]); nd=mdist(tr,tc,hf[0],hf[1])
            if nd<od:
                bonus=30
                if p.rank>=8: bonus=60
                if p.rank>=9: bonus=80
                v+=bonus*(od-nd)
                if nd<=2: v+=150
                if nd<=1: v+=300
        if af:
            ft=self.flag_threats(board)
            if ft:
                ct=ft[0]; ct_r,ct_c,ct_d=ct[0],ct[1],ct[3]
                if ct_d<=3 and isinstance(p.rank,int) and p.rank>=5:
                    od2=mdist(fr,fc,ct_r,ct_c); nd2=mdist(tr,tc,ct_r,ct_c)
                    if nd2<od2: v+=200
                if ct_d<=2:
                    od3=mdist(fr,fc,af[0],af[1]); nd3=mdist(tr,tc,af[0],af[1])
                    if nd3<=2 and od3>2 and isinstance(p.rank,int) and p.rank>=6:
                        v+=250
        v+=(tr-fr)*6
        if len(self.last_moves)>=1:
            lm=self.last_moves[-1]
            if (tr,tc)==(lm[0],lm[1]) and (fr,fc)==(lm[2],lm[3]): v-=400
        if (fr,fc,tr,tc) in self.last_moves: v-=100
        return v

    def minimax(self,board,d,al,be,mx):
        if board.flag("human") is None: return 99999
        if board.flag("ai") is None: return -99999
        if d==0: return self.eval_board(board)
        owner="ai" if mx else "human"
        mvs=board.all_moves(owner)
        if not mvs: return -80000 if mx else 80000
        mvs.sort(key=lambda m:self.score_move(board,m),reverse=mx)
        val=-99999 if mx else 99999
        for m in mvs[:8]:
            b=board.copy(); info=b.do(*m)
            if info["flag"]: return 99999 if mx else -99999
            nv=self.minimax(b,d-1,al,be,not mx)
            if mx:
                if nv>val: val=nv
                al=max(al,nv)
            else:
                if nv<val: val=nv
                be=min(be,nv)
            if be<=al: break
        return val

    def astar_path(self, board, start, goal, danger=None):
        """A* on a static board: (path, cost), or ([], infinity).

        Other pieces stay fixed during route planning. Enemy squares are
        terminal targets, never corridors. Minimax handles actual combat and
        opponent replies. Scouts use their existing multi-square movement.
        """
        piece = board.get(*start)
        if not piece or not piece.can_move or not board.ok(*goal):
            return [], float("inf")
        if goal in LAKE_SET:
            return [], float("inf")
        danger = danger or {}

        def heuristic(pos):
            if piece.rank == 2:
                # A scout can cover an entire clear row/column in one turn.
                return int(pos[0] != goal[0]) + int(pos[1] != goal[1])
            return mdist(pos[0], pos[1], goal[0], goal[1])

        frontier = [(heuristic(start), 0, start)]
        costs = {start: 0}
        parent = {}
        while frontier:
            _, cost, current = heapq.heappop(frontier)
            if cost != costs.get(current):
                continue
            if current == goal:
                path = [current]
                while current in parent:
                    current = parent[current]
                    path.append(current)
                return path[::-1], cost
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = current[0] + dr, current[1] + dc
                while board.ok(nr, nc) and (nr, nc) not in LAKE_SET:
                    nxt = (nr, nc)
                    # The moving piece has vacated its original square.
                    occupant = None if nxt == start else board.get(nr, nc)
                    if occupant and occupant.owner == piece.owner:
                        break
                    if occupant and nxt != goal:
                        break
                    if occupant and occupant.revealed:
                        # Do not plan a route ending in certain destruction.
                        if piece.fight(occupant) != "a":
                            break
                    new_cost = cost + 1 + danger.get(nxt, 0)
                    if new_cost < costs.get(nxt, float("inf")):
                        costs[nxt] = new_cost
                        parent[nxt] = current
                        heapq.heappush(frontier,
                                       (new_cost + heuristic(nxt), new_cost, nxt))
                    if occupant or piece.rank != 2:
                        break
                    nr += dr
                    nc += dc
        return [], float("inf")

    def astar_move_bonuses(self, board):
        """Plan once per real turn; give Minimax a modest positional signal.

        Keeps the existing AI's flag knowledge and all game rules unchanged.
        Paths are recalculated every turn, not followed blindly.
        """
        bonuses = {}
        enemies = board.pieces("human")
        flag = self.find_flag(board)
        own_flag = board.flag("ai")
        # Only revealed attackers contribute to route risk estimates.
        attacks = []
        for er, ec, enemy in enemies:
            if enemy.revealed and enemy.can_move:
                attacks.append((enemy, board.moves(er, ec)))
        for r, c, piece in board.pieces("ai"):
            if not piece.can_move:
                continue
            danger = {}
            for enemy, squares in attacks:
                if enemy.fight(piece) in ("a", "b"):
                    for square in squares:
                        danger[square] = danger.get(square, 0) + 3
            targets = {}
            if flag:
                targets[flag] = 70
            nearby = sorted(enemies, key=lambda e: mdist(r, c, e[0], e[1]))
            # Nearby engagements also provide goals when the flag is blocked.
            for er, ec, enemy in nearby[:4]:
                if enemy.revealed and piece.fight(enemy) != "a":
                    continue
                value = 22 if not enemy.revealed else 35
                if enemy.revealed and enemy.rank == "B" and piece.rank == 3:
                    value = 55
                if own_flag and enemy.can_move:
                    if mdist(er, ec, *own_flag) <= 3:
                        value += 20
                targets[(er, ec)] = max(targets.get((er, ec), 0), value)
            legal = set(board.moves(r, c))
            for goal, value in targets.items():
                path, cost = self.astar_path(board, (r, c), goal, danger)
                if len(path) < 2 or path[1] not in legal:
                    continue
                move = (r, c, path[1][0], path[1][1])
                # Bounded bonus: tactics and flag captures retain priority.
                bonus = min(35.0, value / (1 + cost / 4))
                bonuses[move] = max(bonuses.get(move, 0), bonus)
        return bonuses

    def best_move(self,board):
        self.turn_count+=1
        mvs=board.all_moves("ai")
        if not mvs: return None
        hf=self.find_flag(board)
        for m in mvs:
            tgt=board.get(m[2],m[3])
            if tgt and tgt.owner=="human" and tgt.rank=="F": return m
        escape_moves=[]
        for r,c,p in board.pieces("ai"):
            if not p.can_move or not isinstance(p.rank,int): continue
            threats=self.threats_to(board,r,c,p)
            if threats:
                closest=min(threats,key=lambda x:x[3])
                if closest[3]<=2 and (p.rank>=5 or closest[3]==1):
                    esc=self.best_escape(board,r,c,p,closest[0],closest[1])
                    if esc:
                        es=self.score_move(board,esc)
                        escape_moves.append((es+300,esc))
        defense_moves=[]
        af=board.flag("ai")
        if af:
            ft=self.flag_threats(board)
            if ft and ft[0][3]<=2:
                for m in mvs:
                    fr2,fc2,tr2,tc2=m
                    p2=board.get(fr2,fc2)
                    if not isinstance(p2.rank,int): continue
                    ct=ft[0]
                    if mdist(tr2,tc2,ct[0],ct[1])<=1 and p2.rank>=5:
                        ds=self.score_move(board,m)
                        defense_moves.append((ds+400,m))
        specials=escape_moves+defense_moves
        if specials:
            specials.sort(reverse=True,key=lambda x:x[0])
            if specials[0][0]>400: return specials[0][1]
        route_bonuses=self.astar_move_bonuses(board)
        scored=[]
        for m in mvs:
            s=self.score_move(board,m)+route_bonuses.get(m,0)
            scored.append((s,m))
        scored.sort(reverse=True,key=lambda x:x[0])
        candidates=[m for s,m in scored[:10]]
        best=candidates[0]; bv=-99999
        al=-99999; be=99999
        total=board.count("ai")+board.count("human")
        depth=2
        if total<=14: depth=3
        for m in candidates:
            b=board.copy(); info=b.do(*m)
            if info.get("flag"): return m
            route_bonus=route_bonuses.get(m,0)
            # Shift the search window because the route bonus is root-only.
            nv=self.minimax(b,depth,al-route_bonus,be-route_bonus,False)
            nv+=route_bonus
            if nv>bv: bv=nv; best=m
            al=max(al,nv)
        fr3,fc3,tr3,tc3=best
        p3=board.get(fr3,fc3)
        if p3 and p3.rank==2:
            key=id(p3)
            if key not in self.scout_visited: self.scout_visited[key]=set()
            self.scout_visited[key].add((tr3,tc3))
        self.last_moves.append(best)
        if len(self.last_moves)>8: self.last_moves.pop(0)
        return best

    def setup(self):
        g=[[None]*NC for _ in range(4)]
        cnt={"F":1,"B":6,10:1,9:1,8:2,7:3,6:4,5:4,4:4,3:5,2:8,1:1}
        strat=random.randint(0,5)
        if strat==0: fc=random.choice([0,1]); fr=0
        elif strat==1: fc=random.choice([8,9]); fr=0
        elif strat==2: fc=random.randint(3,6); fr=0
        elif strat==3: fc=random.choice([0,9]); fr=1
        elif strat==4: fc=random.randint(2,7); fr=1
        else: fc=random.randint(1,8); fr=0
        g[fr][fc]=("F","ai")
        bomb_near=random.randint(2,4)
        bsp=[]
        for dr in range(-1,2):
            for dc in range(-1,2):
                if dr==0 and dc==0: continue
                nr,nc=fr+dr,fc+dc
                if 0<=nr<4 and 0<=nc<NC: bsp.append((nr,nc))
        random.shuffle(bsp); bn=0
        for pos in bsp:
            if g[pos[0]][pos[1]] is None and bn<bomb_near:
                g[pos[0]][pos[1]]=("B","ai"); bn+=1
        ae=[(r,c) for r in range(4) for c in range(NC) if g[r][c] is None]
        random.shuffle(ae)
        for pos in ae:
            if bn>=6: break
            if g[pos[0]][pos[1]] is None:
                g[pos[0]][pos[1]]=("B","ai"); bn+=1
        strong=[10,9,8,8,7,7,7,1]
        random.shuffle(strong)
        rows_w=[3,2,3,2,3,2,1,3]
        random.shuffle(rows_w)
        for i,rank in enumerate(strong):
            prow=rows_w[i] if i<len(rows_w) else random.choice([2,3])
            spots=[(prow,c) for c in range(NC)]+[(prow-1,c) for c in range(NC)]
            random.shuffle(spots)
            placed=False
            for pos in spots:
                if 0<=pos[0]<4 and 0<=pos[1]<NC and g[pos[0]][pos[1]] is None:
                    g[pos[0]][pos[1]]=(rank,"ai"); placed=True; break
            if not placed:
                for r2 in range(3,-1,-1):
                    for c2 in range(NC):
                        if g[r2][c2] is None:
                            g[r2][c2]=(rank,"ai"); placed=True; break
                    if placed: break
        pl={k:sum(1 for r in range(4) for c in range(NC)
            if g[r][c] and g[r][c][0]==k) for k in cnt}
        rm=[k for k in ORD for _ in range(cnt[k]-pl.get(k,0))]
        em=[(r,c) for r in range(4) for c in range(NC) if g[r][c] is None]
        random.shuffle(em); random.shuffle(rm)
        for i,pos in enumerate(em):
            if i<len(rm): g[pos[0]][pos[1]]=(rm[i],"ai")
        return {(r,c):Piece(g[r][c][0],"ai")
                for r in range(4) for c in range(NC) if g[r][c]}

class Game:
    def __init__(self):
        self.board=Board(); self.ai=AI()
        self.phase="setup"; self.turn="human"
        self.winner=None; self.reason=""
        self.sel_rank=None; self.placed={}
        self.sel=None; self.vm=[]; self.log=[]
        self.ai_on=False; self.ai_t=0
        self.hcap=0; self.acap=0; self.moves=0
        self.ai_flag_revealed=False  # flag hidden during setup
        self.ai_flag_pos=None
        for (r,c),p in self.ai.setup().items():
            self.board.put(r,c,p)
    def start_battle(self):
        """Called when player presses ENTER after setup"""
        self.phase="battle"; self.turn="human"
        af=self.board.flag("ai")
        if af:
            self.ai_flag_revealed=True
            self.ai_flag_pos=af
            self.log.append(("🚩 AI Flag revealed! Plan your attack!",(255,215,0)))
        self.log.append(("⚔  Battle Start! Your move.",(200,220,255)))

    def rem(self):
        pl={}
        for p in self.placed.values(): pl[p.rank]=pl.get(p.rank,0)+1
        return {rk:PD[rk][2]-pl.get(rk,0) for rk in ORD if PD[rk][2]-pl.get(rk,0)>0}

    def click(self,r,c,btn):
        if self.phase=="setup":
            if btn==3:
                p=self.board.get(r,c)
                if p and p.owner=="human":
                    self.board.rem(r,c); self.placed.pop((r,c),None)
                return
            if self.sel_rank and r in HR and (r,c) not in LAKE_SET:
                ex=self.board.get(r,c)
                if ex and ex.owner=="human":
                    self.board.rem(r,c); self.placed.pop((r,c),None)
                p=Piece(self.sel_rank,"human")
                self.board.put(r,c,p); self.placed[(r,c)]=p
                if self.sel_rank not in self.rem(): self.sel_rank=None
        elif self.phase=="battle" and self.turn=="human":
            p=self.board.get(r,c)
            if self.sel:
                if (r,c) in self.vm:
                    self._hmove(*self.sel,r,c); return
                if p and p.owner=="human" and p.can_move and self.board.moves(r,c):
                    self.sel=(r,c); self.vm=self.board.moves(r,c); return
                self.sel=None; self.vm=[]
            elif p and p.owner=="human" and p.can_move:
                mv=self.board.moves(r,c)
                if mv: self.sel=(r,c); self.vm=mv

    def _hmove(self,fr,fc,tr,tc):
        self.ai.moved_piece(fr,fc,tr,tc)
        info=self.board.do(fr,fc,tr,tc)
        self.moves+=1; self.sel=None; self.vm=[]
        self._proc(info,"human")
        if self.phase!="gameover":
            self.turn="ai"; self.ai_on=True; self.ai_t=350

    def update(self,dt):
        if self.phase!="battle" or not self.ai_on: return
        self.ai_t-=dt
        if self.ai_t<=0:
            self.ai_on=False
            mv=self.ai.best_move(self.board)
            if mv is None: self._end("human","AI has no moves!"); return
            info=self.board.do(*mv); self.moves+=1
            d=info.get("d")
            if d and d.owner=="human" and d.revealed:
                self.ai.remember(mv[2],mv[3],d.rank)
            self._proc(info,"ai")
            af=self.board.flag("ai")
            if af: self.ai_flag_pos=af
            else: self.ai_flag_pos=None
            if self.phase!="gameover": self.turn="human"

    def _proc(self,info,who):
        a=info["a"]; d=info["d"]
        an=a.name if a else "?"; dn=d.name if d else "?"
        asym=a.sym if a else "?"; dsym=d.sym if d else "?"
        w="You" if who=="human" else "AI"
        if info["type"]=="combat":
            if info["aw"]:
                self.log.append((f"⚔ {w}: {an}[{asym}] beat {dn}[{dsym}]",
                    (250,155,65) if who=="human" else (100,180,255)))
                if who=="human": self.hcap+=1
                else: self.acap+=1
            elif info["dw"]:
                self.log.append((f"🛡 {w}: {an}[{asym}] lost to {dn}[{dsym}]",
                    (100,180,255) if who=="human" else (250,155,65)))
                if who=="human": self.acap+=1
                else: self.hcap+=1
            elif info["bt"]:
                self.log.append((f"💥 {an}[{asym}] vs {dn}[{dsym}]: Both gone!",(250,95,95)))
            if info["flag"]:
                self._end(who,f"{'You' if who=='human' else 'AI'} captured the Flag! 🚩")
                return
        else:
            col=(160,200,255) if who=="human" else (160,160,255)
            self.log.append((f"{'You' if who=='human' else 'AI'} moved",col))
        self._chk()

    def _chk(self):
        if self.board.flag("human") is None:
            self._end("ai","Your flag was captured!"); return
        if self.board.flag("ai") is None:
            self._end("human","AI flag captured!"); return
        if not self.board.all_moves("human"):
            self._end("ai","No moves left!"); return
        if not self.board.all_moves("ai"):
            self._end("human","AI is stuck!"); return

    def _end(self,w,r):
        self.phase="gameover"; self.winner=w; self.reason=r
        col=(70,255,130) if w=="human" else (255,80,80)
        self.log.append((("🏆 YOU WIN! " if w=="human" else "💀 AI WINS! ")+r,col))

    def auto_fill(self):
        rm=self.rem()
        pool=[rk for rk,n in rm.items() for _ in range(n)]
        empty=[(r,c) for r in HR for c in range(NC)
               if (r,c) not in LAKE_SET and self.board.get(r,c) is None]
        random.shuffle(empty); random.shuffle(pool)
        for i,rk in enumerate(pool):
            if i<len(empty):
                r,c=empty[i]; p=Piece(rk,"human")
                self.board.put(r,c,p); self.placed[(r,c)]=p

def draw(game):
    global TICK; TICK+=1
    screen.fill(BG)
    pygame.draw.rect(screen,PN,(0,0,W,48))
    pygame.draw.line(screen,PB,(0,48),(W,48),2)
    if game.phase=="setup":
        ttl="⚔  STRATEGO  —  SETUP: Place your army"; tc=GD
    elif game.phase=="battle":
        if game.turn=="human":
            ttl="⚔  STRATEGO  —  ✅ YOUR TURN"; tc=(100,220,100)
        else:
            ttl="⚔  STRATEGO  —  🤖 AI"+"."*((TICK//12)%4); tc=(100,160,255)
    else:
        ttl="⚔  STRATEGO  —  GAME OVER"; tc=GD
    tx(ttl,fT,tc,W//2,24,cx=True)
    for r in range(NR):
        for c in range(NC):
            x,y=cpx(r,c); rect=pygame.Rect(x,y,CS,CS)
            col2=(32,35,58) if (r+c)%2==0 else (38,42,65)
            if (r,c) in BRIDGE_SET:
                col2=(40,55,45) if (r+c)%2==0 else (45,62,50)
            pygame.draw.rect(screen,col2,rect)
            if (r,c) in BRIDGE_SET:
                pygame.draw.rect(screen,BRIDGE,rect,2)
            if game.phase=="setup" and r in HR:
                s=pygame.Surface((CS,CS),pygame.SRCALPHA)
                s.fill((195,55,55,25)); screen.blit(s,(x,y))
            if game.ai_flag_revealed and game.ai_flag_pos==(r,c):
                pulse=abs((TICK%60)-30)/30.0
                alpha=int(40+pulse*40)
                s2=pygame.Surface((CS,CS),pygame.SRCALPHA)
                s2.fill((255,215,0,alpha)); screen.blit(s2,(x,y))

            if game.sel==(r,c):
                pygame.draw.rect(screen,SL,rect,3)
            elif (r,c) in game.vm:
                q=game.board.get(r,c)
                hl=AK if (q and q.owner=="ai") else MV
                s=pygame.Surface((CS,CS),pygame.SRCALPHA)
                s.fill((*hl,55)); screen.blit(s,(x,y))
                pygame.draw.rect(screen,hl,rect,2)
            pygame.draw.rect(screen,GR,rect,1)
    for r in range(NR):
        for c in range(NC):
            p=game.board.get(r,c)
            if not p: continue
            x,y=cpx(r,c); pad=5
            cx2,cy2=x+CS//2,y+CS//2
            if p.owner=="human":
                show=True
            elif p.owner=="ai":
                if game.phase=="gameover":
                    show=True
                elif game.phase=="setup":
                    show=False 
                elif p.rank=="F" and game.ai_flag_revealed:
                    show=True  
                elif p.revealed:
                    show=True
                else:
                    show=False
            else:
                show=False
            pc=HC if p.owner=="human" else AC
            pr2=pygame.Rect(x+pad,y+pad,CS-pad*2,CS-pad*2)
            pygame.draw.rect(screen,pc,pr2,border_radius=7)
            if show and p.rank=="F":
                pulse=abs((TICK%40)-20)/20.0
                gc=int(180+pulse*75)
                pygame.draw.rect(screen,(255,gc,0),pr2,3,border_radius=7)
            elif game.sel==(r,c):
                pygame.draw.rect(screen,SL,pr2,2,border_radius=7)
            else:
                pygame.draw.rect(screen,(0,0,0),pr2,2,border_radius=7)

            if show:
                sc=(255,215,45) if p.rank in (10,"F") else (255,255,255)
                tx(p.sym,fM,sc,cx2,cy2-4,cx=True)
                tx(p.name[:5],fXS,(185,195,215),cx2,cy2+9,cx=True)
            else:
                tx("?",fM,DM,cx2,cy2,cx=True)
                if p.moved:
                    pygame.draw.circle(screen,(190,190,70),(x+pad+7,y+pad+7),3)
    for i in range(NR): tx(str(i),fXS,DM,OX+NC*CS+4,OY+i*CS+CS//2-6)
    for j in range(NC): tx(chr(65+j),fXS,DM,OX+j*CS+CS//2-4,OY-16)
    rw=W-RPX-5
    pygame.draw.rect(screen,PN,(RPX,48,rw,H-48))
    pygame.draw.line(screen,PB,(RPX,48),(RPX,H),2)
    ry=55

    if game.phase=="setup":
        tx("SELECT PIECE",fL,GD,RPX+rw//2,ry,cx=True); ry+=26
        pygame.draw.line(screen,PB,(RPX+8,ry),(W-8,ry),1); ry+=8
        rm=game.rem()
        col1=RPX+10; col2x=RPX+rw//2+5; col_y=ry; left=True
        for rk in ORD:
            r2=rm.get(rk,0); issel=(game.sel_rank==rk)
            cx3=col1 if left else col2x
            card=pygame.Rect(cx3,col_y,rw//2-14,28)
            cc=(65,105,195) if issel else (30,38,65) if r2>0 else (15,18,35)
            pygame.draw.rect(screen,cc,card,border_radius=5)
            if issel: pygame.draw.rect(screen,SL,card,2,border_radius=5)
            tc2=TX if r2>0 else DM
            tx(f"{PD[rk][1]} {PD[rk][0][:6]}",fS,tc2,cx3+5,col_y+7)
            tx(f"x{r2}",fS,tc2,cx3+rw//2-20,col_y+7)
            if not left: col_y+=30
            left=not left
        if not left: col_y+=30
        col_y+=8
        pygame.draw.line(screen,PB,(RPX+8,col_y),(W-8,col_y),1); col_y+=10
        ab=pygame.Rect(RPX+10,col_y,rw-20,32)
        gb=pygame.Rect(RPX+10,col_y+40,rw-20,32)
        pygame.draw.rect(screen,(35,60,115),ab,border_radius=7)
        pygame.draw.rect(screen,PB,ab,1,border_radius=7)
        gc=WN if not game.rem() else (22,44,25)
        pygame.draw.rect(screen,gc,gb,border_radius=7)
        pygame.draw.rect(screen,PB,gb,1,border_radius=7)
        tx("⚡ F1: Auto Fill",fM,TX,ab.centerx,ab.centery,cx=True)
        gl="⚔  ENTER: Start!" if not game.rem() else "⏳ Place all first"
        tx(gl,fM,GD if not game.rem() else DM,gb.centerx,gb.centery,cx=True)
        col_y+=82
        pygame.draw.line(screen,PB,(RPX+8,col_y),(W-8,col_y),1); col_y+=8
        tx("TIPS",fM,GD,RPX+rw//2,col_y,cx=True); col_y+=20
        tips=["Left-click: select & place","Right-click: remove",
              "Red zone = setup area","AI flag hidden until battle!",
              "≡ = Open bridge path","SPACE/R: deselect/reset"]
        for tip in tips:
            tx(tip,fXS,DM,RPX+10,col_y); col_y+=16
    else:
        bw3=(rw-20)//3; by3=ry
        stats=[("MOVES",str(game.moves),TX),
               ("YOU ⚔",str(game.hcap),(70,215,110)),
               ("AI ⚔",str(game.acap),(215,70,70))]
        for i,(lbl,val,vc) in enumerate(stats):
            bx3=RPX+10+i*(bw3+5)
            pygame.draw.rect(screen,(25,30,60),(bx3,by3,bw3,48),border_radius=8)
            pygame.draw.rect(screen,PB,(bx3,by3,bw3,48),1,border_radius=8)
            tx(lbl,fXS,DM,bx3+bw3//2,by3+12,cx=True)
            tx(val,fL,vc,bx3+bw3//2,by3+31,cx=True)
        ry+=56
        pygame.draw.line(screen,PB,(RPX+8,ry),(W-8,ry),1); ry+=8
        if game.phase=="gameover":
            tc3=GD; tl="— GAME OVER —"
        elif game.turn=="human":
            tc3=(100,220,100); tl="▶  YOUR TURN"
        else:
            tc3=(100,160,255); tl="🤖 AI..."+"."*((TICK//12)%4)
        tx(tl,fL,tc3,RPX+rw//2,ry+10,cx=True); ry+=28
        pygame.draw.line(screen,PB,(RPX+8,ry),(W-8,ry),1); ry+=8
        hf=game.board.flag("human"); af=game.board.flag("ai")
        tx("🚩 FLAGS",fXS,GD,RPX+rw//2,ry+2,cx=True); ry+=18
        if hf: tx(f"Your flag: row {hf[0]} col {chr(65+hf[1])}",fXS,(100,200,100),RPX+10,ry)
        else: tx("Your flag: CAPTURED!",fXS,(255,80,80),RPX+10,ry)
        ry+=14
        if af: tx(f"AI flag: row {af[0]} col {chr(65+af[1])}  🎯",fXS,(255,200,60),RPX+10,ry)
        else: tx("AI flag: CAPTURED!",fXS,(100,255,100),RPX+10,ry)
        ry+=14
        ac=game.board.count("ai"); hc=game.board.count("human")
        tx(f"Pieces — You: {hc}  AI: {ac}",fXS,(180,190,210),RPX+rw//2,ry+2,cx=True)
        ry+=18
        pygame.draw.line(screen,PB,(RPX+8,ry),(W-8,ry),1); ry+=6
        tx("BATTLE LOG",fL,GD,RPX+rw//2,ry,cx=True); ry+=22
        pygame.draw.line(screen,PB,(RPX+8,ry),(W-8,ry),1); ry+=4
        log_h=H-ry-65
        max_m=log_h//18
        msgs=list(reversed(game.log[-max_m:]))
        for i,(msg,col) in enumerate(msgs):
            rr=pygame.Rect(RPX+6,ry+i*18,rw-12,17)
            if i%2==0: pygame.draw.rect(screen,(20,24,48),rr,border_radius=3)
            f2=fM if i==0 else fXS
            c2=col if i==0 else tuple(max(80,v-40) for v in col)
            short=msg[:36]+"..." if len(msg)>36 else msg
            tx(short,f2,c2,RPX+10,ry+i*18+1)
            if ry+i*18>H-70: break
        ly=H-58
        pygame.draw.line(screen,PB,(RPX+8,ly),(W-8,ly),1); ly+=6
        legs=[((190,190,70),"Moved"),((255,215,0),"Flag"),(MV,"Move"),(AK,"Attack")]
        for i,(lc,lt) in enumerate(legs):
            cx4=RPX+8+(rw//4)*i
            pygame.draw.rect(screen,lc,(cx4,ly,8,8),border_radius=2)
            tx(lt,fXS,DM,cx4+11,ly-1)
        tx("SPACE:desel  R:new  ESC:quit",fXS,DM,RPX+rw//2,H-18,cx=True)
    if game.phase=="gameover":
        ov=pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,145)); screen.blit(ov,(0,0))
        bw2,bh2=460,215; bx2=W//2-bw2//2; by2=H//2-bh2//2
        bc=WN if game.winner=="human" else LS
        pygame.draw.rect(screen,bc,(bx2,by2,bw2,bh2),border_radius=16)
        pygame.draw.rect(screen,GD,(bx2,by2,bw2,bh2),2,border_radius=16)
        hl="🏆  YOU WIN!" if game.winner=="human" else "💀  AI WINS!"
        hc=(70,255,130) if game.winner=="human" else (255,90,90)
        tx(hl,fB,hc,W//2,by2+50,cx=True)
        tx(game.reason,fM,TX,W//2,by2+98,cx=True)
        tx(f"Moves: {game.moves}  You: {game.hcap}  AI: {game.acap}",
           fS,DM,W//2,by2+130,cx=True)
        tx("R = Again     ESC = Quit",fM,(175,195,250),W//2,by2+170,cx=True)
    pygame.display.flip()

def main():
    game=Game()
    while True:
        dt=clock.tick(60)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if e.key==pygame.K_r: game=Game()
                if e.key==pygame.K_F1 and game.phase=="setup": game.auto_fill()
                if e.key==pygame.K_RETURN and game.phase=="setup":
                    if not game.rem():
                        game.start_battle()  # reveals AI flag
                if e.key==pygame.K_SPACE: game.sel=None; game.vm=[]
            if e.type==pygame.MOUSEBUTTONDOWN:
                mx,my=e.pos; r,c=pxc(mx,my)
                if game.phase=="setup" and mx>=RPX:
                    rm=game.rem()
                    rw2=W-RPX-5; col1=RPX+10; col2x=RPX+rw2//2+5
                    row=89; left=True
                    for rk in ORD:
                        cx3=col1 if left else col2x
                        card=pygame.Rect(cx3,row,rw2//2-14,28)
                        if card.collidepoint(mx,my) and rm.get(rk,0)>0:
                            game.sel_rank=rk; break
                        if not left: row+=30
                        left=not left
                if r is not None: game.click(r,c,e.button)
        game.update(dt); draw(game)
main()