"""Passage-group flow for a language subject.  usage: langtest.py <out-dir> [subject=chinese] [topic]"""
import sys, glob
from playwright.sync_api import sync_playwright
out = sys.argv[1]; subj = sys.argv[2] if len(sys.argv) > 2 else 'chinese'; topic = sys.argv[3] if len(sys.argv) > 3 else None
exe = glob.glob('/home/longge/.cache/ms-playwright/chromium-1234/*/chrome')[0]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page(viewport={'width':1180,'height':820})
    logs = []; pg.on('pageerror', lambda e: logs.append('PAGEERROR: ' + str(e))); pg.on('console', lambda m: logs.append(m.text) if m.type == 'error' else None)
    pg.goto('file:///home/longge/code/edutech/index.html'); pg.wait_for_timeout(500)
    pg.screenshot(path=f'{out}/{subj}-0-home.png')
    pg.click(f'[data-subject="{subj}"]'); pg.wait_for_timeout(300); pg.screenshot(path=f'{out}/{subj}-1-menu.png')
    pg.evaluate('''(topic) => { const L = PSLE.subjects[subjectId]; const g = L.questions.find(q => q.group && (!topic || q.topic === topic)).group;
        startSession({mode:"topic", label:"Test", pool:L.questions.filter(q => q.group === g).map(q => q.id)}); }''', topic)
    pg.wait_for_timeout(1200); pg.screenshot(path=f'{out}/{subj}-2-passage.png')
    n = pg.evaluate('session.gpos.n')
    for i in range(n):
        if pg.locator('#answer [data-opt]').count(): pg.locator('#answer [data-opt]').first.click()
        else:
            for k in range(pg.locator('#answer [data-part]').count()): pg.locator('#answer [data-part]').nth(k).fill('test')
        pg.click('#btnCheck'); pg.wait_for_timeout(300)
        while pg.locator('[data-self][data-val="right"]').count(): pg.locator('[data-self][data-val="right"]').first.click()
        if i in (0, n-1): pg.screenshot(path=f'{out}/{subj}-3-result{i}.png')
        if i < n-1: pg.click('#btnNext'); pg.wait_for_timeout(300)
    pg.click('[data-pt="pad"]'); pg.wait_for_timeout(300); pg.screenshot(path=f'{out}/{subj}-4-pad.png')
    print(subj, 'group of', n, '|', '\n'.join(logs) or 'no errors'); b.close()
