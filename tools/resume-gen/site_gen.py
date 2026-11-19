# Build nasyrov.pro resume/portfolio fragments from the «Портфолио 2026г» doc dump (C5.txt).
import re,html,sys
SITE="/root/sergeynasyrow-site"
lines=open("C5.txt").read().split("\n")
def tab(name):
    out=[];on=False
    for l in lines:
        if l.startswith("=== TAB "): on=l.startswith("=== TAB "+name); continue
        if on: out.append(l)
    return out
def parse(l):
    st,_,t=l.partition(" "); b=t.startswith("• ")
    return st,(t[2:] if b else t),b
GLUE=r"(?<![\wА-Яа-яЁё])(а|и|в|к|с|о|у|я|от|до|на|по|за|из|не|но|ни|для|без|при|под|над|об|со|ко|во|что|как|же|или|их|его|её|раз|все|это)\s"
def esc(t):
    t=html.escape(t.replace("\x0b"," ").replace("  "," "),quote=False)
    return re.sub(GLUE,lambda m:m.group(1)+"&nbsp;",t)
# ---- portfolio from «Кейсы»
SKIP_CASES=("Организовал продвижение компании в Яндекс Картах",)
projs=[];cur=None;case=None;mode=None
for l in tab("Кейсы"):
    st,t,b=parse(l)
    if st=="HEADING_2": cur={"name":t,"cases":[]};projs.append(cur);case=None;continue
    if st=="HEADING_3":
        case={"h":t,"sit":[],"did":[],"res":[]};mode=None
        if not t.startswith(SKIP_CASES): cur["cases"].append(case)
        continue
    if case is None or not t.strip(): continue
    if t in("Ситуация","Что сделал","Результат"): mode={"Ситуация":"sit","Что сделал":"did","Результат":"res"}[t];continue
    if mode: case[mode].append(t)
def ul(items): return "<ul>\n"+"".join(f"                  <li>{esc(i)}</li>\n" for i in items)+"                </ul>"
P=[]
for p in projs:
    P.append(f'        <div class="proj">\n          <div class="proj__name">{esc(p["name"])}</div>\n')
    for c in p["cases"]:
        sit="<br><br>".join(esc(s) for s in c["sit"])
        P.append(f'''
          <details class="case-item">
            <summary>{esc(c["h"])}</summary>
            <div class="case-item__body">
              <div class="case-item__block">
                <div class="case-item__block-label">Ситуация</div>
                {sit}
              </div>
              <div class="case-item__block">
                <div class="case-item__block-label">Что&nbsp;сделал</div>
                {ul(c["did"])}
              </div>
              <div class="case-item__result">
                <strong>Результат:</strong>
                {ul(c["res"]).replace("<ul>",'<ul style="margin:6px 0 0;padding-left:20px;">',1)}
              </div>
            </div>
          </details>
''')
    P.append("        </div>\n\n")
portfolio_block="".join(P)
# ---- human tab from «Сайт — на согласование», section «Для человеков»
hum=[];job=None;sec=None;on=False
for l in tab("Сайт — на согласование"):
    st,t,b=parse(l)
    if st=="HEADING_2": on= t.startswith("Вкладка «Для человеков»"); continue
    if not on or not t.strip(): continue
    if st=="HEADING_3": job={"co":t,"meta":None,"pre":[],"res":[]};hum.append(job);sec=None;continue
    if job["meta"] is None: job["meta"]=t;continue
    if t in("Задача","Что сделал"): sec="pre";continue
    if t=="Результат": sec="res";continue
    job[sec].append(t)
import json
LEADS=json.load(open("leads.json"))
def para(x):
    ld=LEADS.get(x)
    if ld and x.startswith(ld): return f"<strong>{esc(ld.rstrip())}</strong> {esc(x[len(ld):].lstrip())}"
    return esc(x)
H=[]
for j in hum:
    period,_,title=j["meta"].partition(". ")
    pre="\n".join(f"          <p>{para(x)}</p>" for x in j["pre"])
    res="\n".join(f"            <p>{para(x)}</p>" for x in j["res"])
    H.append(f'''        <div class="job">
          <div class="job__top">
            <span class="job__company">{esc(j["co"])}</span>
            <span class="job__period">{esc(period)}</span>
          </div>
          <div class="job__title">{esc(title)}</div>
{pre}
          <div class="job__results">
            <div class="job__results-title">Результат</div>
{res}
          </div>
        </div>

''')
human_block="".join(H)
# ---- robots tab from «Резюме рук»: role header + KOBLiK and Croopa bullets
rob=tab("Резюме рук");i=next(k for k,l in enumerate(rob) if "Ведущий digital-маркетолог" in l)
role=parse(rob[i])[1];period=parse(rob[i+1])[1];intro=parse(rob[i+2])[1]
groups=[];k=i+3
while not rob[k].startswith("HEADING_2"):
    st,t,b=parse(rob[k])
    if st=="HEADING_3": groups.append((t,[]))
    elif b: groups[-1][1].append(t)
    k+=1
title,_,kind=role.partition(" · ")
R=[f'''      <div class="job">
        <div class="job__top">
          <span class="job__company">{esc(kind.capitalize())}: два параллельных проекта</span>
          <span class="job__period">Июль 2026 — настоящее время · 5&nbsp;месяцев</span>
        </div>
        <div class="job__title">{esc(title)}</div>
        <p style="font-size:13.5px;color:#666;margin-bottom:10px;">{esc(intro)}</p>
''']
for g,items in groups:
    R.append(f'''        <div class="job__results">
          <div class="job__results-title">{esc(g)}</div>
          <ul>
{"".join(f"            <li>{esc(x)}</li>{chr(10)}" for x in items)}          </ul>
        </div>
''')
R.append("      </div>\n\n")
robots_block="".join(R)
assert period=="07.2026 — настоящее время",period
# ---- splice
r=open("base/resume.html").read()
a=r.index('<div id="expHuman" class="exp-version">')+len('<div id="expHuman" class="exp-version">\n')
z=r.index('        <div class="job">\n          <div class="job__top">\n            <span class="job__company">Частная консалтинговая практика (ИП)</span>')
r=r[:a]+human_block+r[z:]
a=r.index('<div id="expRobots" class="exp-version" style="display:none;">')+len('<div id="expRobots" class="exp-version" style="display:none;">\n')
assert r[a:].startswith('      <div class="job">\n        <div class="job__top">\n          <span class="job__company">Частная консалтинговая практика</span>')
r=r[:a]+robots_block+r[a:]
p=open("base/portfolio.html").read()
a=p.index('<div class="proj">\n          <div class="proj__name">Physical Training</div>')-8
p=p[:a]+portfolio_block+p[a:]
if "--write" in sys.argv:
    open("preview/resume.html","w").write(r); open("preview/portfolio.html","w").write(p)
print("human jobs",len(hum),"robots groups",[g for g,_ in groups],"projects",[(x["name"],len(x["cases"])) for x in projs])
