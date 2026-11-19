import json,re,sys,urllib.parse,urllib.request
CFG="/root/.config/gdocs-writer"
cid=re.search(r"GOOGLE_CLIENT_ID=(.+)",open(f"{CFG}/config.env").read()).group(1).strip()
sec=open(f"{CFG}/client-secret").read().strip();ref=open(f"{CFG}/oauth-token").read().strip()
tok=json.load(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token",data=urllib.parse.urlencode({"client_id":cid,"client_secret":sec,"refresh_token":ref,"grant_type":"refresh_token"}).encode())))["access_token"]
H={"Authorization":"Bearer "+tok}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H)))
