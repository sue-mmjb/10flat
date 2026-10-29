import sys, re
from html.parser import HTMLParser
src = open(sys.argv[1], encoding="utf-8").read()
sel=sys.argv[2]; maxdepth=int(sys.argv[3]); minlen=int(sys.argv[4]) if len(sys.argv)>4 else 0
line_starts=[0]
for m in re.finditer("\n", src): line_starts.append(m.end())
def off(pos): return line_starts[pos[0]-1]+pos[1]
VOID={"img","br","meta","link","input","hr","source","wbr","area","base","col","embed","param","track"}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.nodes=[]
    def handle_starttag(s, tag, attrs):
        a=dict(attrs); n={"tag":tag,"attrs":a,"start":off(s.getpos()),"end":None,"children":[]}
        (s.stack[-1]["children"] if s.stack else s.nodes).append(n)
        if tag not in VOID: s.stack.append(n)
        else: n["end"]=src.find(">",n["start"])+1
    def handle_endtag(s, tag):
        for i in range(len(s.stack)-1,-1,-1):
            if s.stack[i]["tag"]==tag:
                e=off(s.getpos()); n=s.stack[i]; n["end"]=src.find(">",e)+1
                for k in s.stack[i+1:]: k["end"]=k["end"] or e
                del s.stack[i:]; break
p=P(); p.feed(src)
def find(nodes, pred):
    for n in nodes:
        if pred(n): return n
        r=find(n["children"],pred)
        if r: return r
def text(n): return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",src[n["start"]:n["end"]])).strip()
if sel.startswith("class="): node=find(p.nodes, lambda n: sel[6:] in (n["attrs"].get("class") or "").split())
elif sel.startswith("id="): node=find(p.nodes, lambda n: n["attrs"].get("id")==sel[3:])
else: node=find(p.nodes, lambda n:n["attrs"].get("data-framer-name")==sel)
def show(n, depth):
    a=n["attrs"]; sl=src[n["start"]:n["end"]]
    if n["end"]-n["start"]<minlen and depth>0: return
    st=(a.get("style") or "")
    print(f"{'  '*depth}<{n['tag']} name={a.get('data-framer-name','')!r} id={a.get('id','')!r} class={(a.get('class') or '')[:40]!r} [{n['start']}-{n['end']}] op0={sl.count('opacity:0;')+sl.count('opacity:0\"')} style={st[:70]!r}")
    t=text(n); print(f"{'  '*depth}   text: {t[:110]!r}")
    if depth<maxdepth:
        for c in n["children"]: show(c, depth+1)
show(node,0)
