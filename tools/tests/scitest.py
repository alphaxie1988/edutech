import sys, glob
from playwright.sync_api import sync_playwright
out = sys.argv[1]
exe = glob.glob('/home/longge/.cache/ms-playwright/chromium-1234/*/chrome')[0]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page(viewport={'width':1180,'height':820})
    logs = []; pg.on('pageerror', lambda e: logs.append('PAGEERROR: ' + str(e))); pg.on('console', lambda m: logs.append(m.text) if m.type == 'error' else None)
    pg.goto('file:///home/longge/code/edutech/index.html'); pg.wait_for_timeout(500)
    pg.click('[data-subject="science"]'); pg.wait_for_timeout(300); pg.screenshot(path=out + '/s1-menu.png')
    # force a structured question and an option-table mcq
    pg.evaluate('''() => { const L = PSLE.subjects.science; const q = L.questions.find(q => q.format !== "mcq" && q.parts.length >= 3 && q.images);
        startSession({mode:"topic", label:"Test", pool:[q.id]}); }''')
    pg.wait_for_timeout(900); pg.screenshot(path=out + '/s2-structured.png')
    pg.click('#btnCheck'); pg.wait_for_timeout(400); pg.screenshot(path=out + '/s3-selfmark.png')
    n = pg.locator('[data-self][data-val="right"]').count()
    for i in range(n): pg.locator('[data-self][data-val="right"]').first.click()
    pg.wait_for_timeout(400); pg.screenshot(path=out + '/s4-done.png')
    pg.evaluate('''() => { const L = PSLE.subjects.science; const q = L.questions.find(q => q.format === "mcq" && q.images && q.options[0].length > 30);
        startSession({mode:"topic", label:"Test", pool:[q.id]}); }''')
    pg.wait_for_timeout(900); pg.screenshot(path=out + '/s5-mcq.png')
    print('\n'.join(logs) or 'no errors'); b.close()
