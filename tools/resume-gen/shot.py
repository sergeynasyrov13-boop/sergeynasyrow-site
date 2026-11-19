import http.server,threading,functools,sys
from playwright.sync_api import sync_playwright
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory="preview")
s=http.server.ThreadingHTTPServer(("127.0.0.1",8765),H); threading.Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,tag in((1280,"d"),(390,"m")):
        pg=b.new_page(viewport={"width":w,"height":900})
        pg.add_init_script("localStorage.setItem('cookie_consent','declined')")
        pg.goto("http://127.0.0.1:8765/resume.html"); pg.wait_for_timeout(500); pg.add_style_tag(content="#cookieBanner,header,nav,.rnav,.pnav{display:none!important}")
        pg.evaluate("document.querySelector('#expHuman').scrollIntoView()"); 
        pg.locator("#expHuman").screenshot(path=f"res-human-{tag}.png")
        pg.click("button[data-mode=robots]"); pg.wait_for_timeout(300)
        pg.locator("#expRobots .job").first.screenshot(path=f"res-robots-{tag}.png")
        pg.goto("http://127.0.0.1:8765/portfolio.html"); pg.wait_for_timeout(500); pg.add_style_tag(content="#cookieBanner,header,nav,.rnav,.pnav{display:none!important}")
        pg.evaluate("document.querySelectorAll('#experience .proj')[0].querySelector('details').open=true; document.querySelectorAll('#experience .proj')[1].querySelector('details').open=true")
        pg.locator("#experience .proj").nth(0).screenshot(path=f"port-koblik-{tag}.png")
        pg.locator("#experience .proj").nth(1).screenshot(path=f"port-croopa-{tag}.png")
    b.close()
s.shutdown()
