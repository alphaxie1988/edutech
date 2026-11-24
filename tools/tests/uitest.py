import sys, glob, json
from playwright.sync_api import sync_playwright
out = sys.argv[1]
exe = glob.glob('/home/longge/.cache/ms-playwright/chromium-1234/*/chrome')[0]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width':1180,'height':820})
    logs = []
    pg.on('console', lambda m: logs.append(m.type + ': ' + m.text))
    pg.on('pageerror', lambda e: logs.append('PAGEERROR: ' + str(e)))
    pg.goto('file:///home/longge/code/edutech/index.html')
    pg.wait_for_timeout(700); pg.screenshot(path=out + '/1-home.png')
    pg.click('[data-subject="maths"]'); pg.wait_for_timeout(300); pg.screenshot(path=out + '/2-menu.png')
    pg.click('[data-topic="data"]'); pg.wait_for_timeout(400); pg.screenshot(path=out + '/3-topic.png')
    pg.click('#topicStart'); pg.wait_for_timeout(900)
    # draw on canvas
    box = pg.locator('#cv').bounding_box()
    pg.mouse.move(box['x'] + 200, box['y'] + 60); pg.mouse.down()
    for i in range(30): pg.mouse.move(box['x'] + 200 + i*8, box['y'] + 60 + (i % 6) * 9)
    pg.mouse.up()
    pin = pg.locator('[data-pin]')
    if pin.count(): pin.first.click(); pg.wait_for_timeout(300)
    pg.screenshot(path=out + '/4-play.png')
    print('question:', pg.evaluate('cur.id'), pg.evaluate('JSON.stringify(cur.parts.map(p=>p.answer))'))
    pg.click('#btnGiveUp'); pg.wait_for_timeout(500); pg.screenshot(path=out + '/5-wrong.png')
    # answer several correctly through the real UI
    for n in range(6):
        pg.click('#btnNext'); pg.wait_for_timeout(400)
        q = pg.evaluate('({format:cur.format, parts:cur.parts.map(p=>p.answer)})')
        if q['format'] == 'mcq':
            pg.click(f'[data-opt="{q["parts"][0]["value"]}"]')
        else:
            for i, a in enumerate(q['parts']):
                if a['type'] == 'self': continue
                v = '167, 169' if a['type'] == 'sum' else str(a['value'])
                pg.fill(f'[data-part="{i}"]', v)
        pg.click('#btnCheck'); pg.wait_for_timeout(300)
        for s in pg.locator('[data-self][data-val="right"]').all(): pg.locator('[data-self][data-val="right"]').first.click()
        print(pg.evaluate('cur.id'), pg.evaluate('JSON.stringify(pending.results)'), 'xp', pg.evaluate('S.xp'))
    pg.wait_for_timeout(300); pg.screenshot(path=out + '/6-right.png')
    pg.click('#btnQuit'); pg.wait_for_timeout(200); pg.click('#menu [data-go="progress"]'); pg.wait_for_timeout(300); pg.screenshot(path=out + '/7-progress.png')
    # phone-size check
    pg.set_viewport_size({'width':390,'height':780}); pg.click('#btnProgBack'); pg.click('#btnRandom'); pg.wait_for_timeout(700); pg.screenshot(path=out + '/8-phone.png')
    print('\n'.join(logs) or 'no console output')
    b.close()
