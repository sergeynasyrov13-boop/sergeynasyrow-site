import sys; sys.path.insert(0,'.')
from g import *
i,out=sys.argv[1],sys.argv[2]
m=get(f"https://www.googleapis.com/drive/v3/files/{i}?fields=modifiedTime,name")
d=get(f"https://docs.googleapis.com/v1/documents/{i}?includeTabsContent=true")
o=[f"{m}"]
def walk(tabs):
    for tab in tabs:
        o.append("=== TAB "+tab["tabProperties"]["title"]+" "+tab["tabProperties"]["tabId"])
        for el in tab["documentTab"]["body"]["content"]:
            if "table" in el:
                for row in el["table"]["tableRows"]:
                    o.append(" | ".join("".join(r.get("textRun",{}).get("content","") for c in cell["content"] if "paragraph" in c for r in c["paragraph"]["elements"]).strip() for cell in row["tableCells"]))
            p=el.get("paragraph")
            if not p: continue
            t="".join(r.get("textRun",{}).get("content","") for r in p["elements"])
            o.append(f"{p.get('paragraphStyle',{}).get('namedStyleType','')[:9]} {'• ' if 'bullet' in p else ''}{t.rstrip()}")
        walk(tab.get("childTabs",[]))
walk(d["tabs"])
open(out,"w").write("\n".join(o)); print(o[0], len(o))
