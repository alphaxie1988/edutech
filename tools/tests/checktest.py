import glob, json
from playwright.sync_api import sync_playwright
exe = glob.glob('/home/longge/.cache/ms-playwright/chromium-1234/*/chrome')[0]
cases = [
 # (answer, input, expected)
 ({"type":"number","value":"48","unit":"cm"}, "48", "right"), ({"type":"number","value":"48","unit":"cm"}, "48 cm", "right"),
 ({"type":"number","value":"48","unit":"cm"}, "48cm", "right"), ({"type":"number","value":"48"}, "84", "wrong"),
 ({"type":"number","value":"1.50","unit":"$","unitPos":"before"}, "$1.5", "right"), ({"type":"number","value":"1.50"}, "1.50", "right"),
 ({"type":"number","value":"2160"}, "2,160", "right"), ({"type":"number","value":"2160"}, "2 160", "right"),
 ({"type":"number","value":"73","unit":"°"}, "73°", "right"), ({"type":"number","value":"154","unit":"cm²"}, "154 cm2", "right"),
 ({"type":"number","value":"0.5"}, "1/2", "right"), ({"type":"number","value":"25","unit":"%"}, "25%", "right"),
 ({"type":"number","value":"112.56","unit":"m"}, "112.56 m", "right"), ({"type":"number","value":"112.56"}, "112.6", "wrong"),
 ({"type":"number","value":"7"}, "y = 7", "right"), ({"type":"number","value":"7"}, "abc", "wrong"),
 ({"type":"fraction","value":"11/20"}, "11/20", "right"), ({"type":"fraction","value":"11/20"}, "22/40", "right"),
 ({"type":"fraction","value":"11/20"}, "0.55", "nudge"), ({"type":"fraction","value":"5/12","simplest":True}, "10/24", "nudge"),
 ({"type":"fraction","value":"5/12","simplest":True}, "5/12", "right"), ({"type":"fraction","value":"2 3/10","simplest":True}, "2 3/10", "right"),
 ({"type":"fraction","value":"2 3/10","simplest":True}, "23/10", "nudge"), ({"type":"fraction","value":"2 3/10","simplest":True}, "2.3", "nudge"),
 ({"type":"fraction","value":"2 3/10","simplest":True}, "2 6/20", "nudge"), ({"type":"fraction","value":"2 3/10"}, "3 2/10", "wrong"),
 ({"type":"ratio","value":"7:12"}, "7 : 12", "right"), ({"type":"ratio","value":"7:12"}, "14:24", "nudge"), ({"type":"ratio","value":"7:12"}, "12:7", "wrong"),
 ({"type":"ratio","value":"2:3:5"}, "2:3:5", "right"),
 ({"type":"expression","value":"12n + 18","accept":["12n+18","18+12n"]}, "18 + 12n", "right"), ({"type":"expression","value":"12n + 18"}, "12n+18", "right"),
 ({"type":"expression","value":"12n + 18"}, "6(2n+3)", "right"), ({"type":"expression","value":"12n + 18"}, "16n+7-4n+11", "nudge"),
 ({"type":"expression","value":"12n + 18"}, "12n+8", "wrong"), ({"type":"expression","value":"3y/4"}, "3/4y", "right?"),
 ({"type":"text","value":"August to September","accept":["aug to sep"]}, "Aug to Sep", "right"), ({"type":"text","value":"August to September","accept":[]}, "august to september.", "right"),
 ({"type":"text","value":"August to September","accept":[]}, "july to august", "wrong"),
 ({"type":"sum","count":2,"sum":"336","value":"x"}, "$167, $169", "right"), ({"type":"sum","count":2,"sum":"336","value":"x"}, "160 and 176", "right"),
 ({"type":"sum","count":2,"sum":"336","value":"x"}, "336", "wrong"), ({"type":"sum","count":2,"sum":"336","value":"x"}, "100, 200", "wrong"),
 ({"type":"mcq","value":2}, 2, "right"), ({"type":"mcq","value":2}, 3, "wrong"),
]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page()
    pg.goto('file:///home/longge/code/edutech/index.html')
    bad = 0
    for a, inp, exp in cases:
        r = pg.evaluate('([a,i]) => { const r = checkPart({answer:a}, i); return typeof r === "object" ? "nudge" : r; }', [a, inp])
        flag = '' if exp.rstrip('?') == r else ('  <-- note' if exp.endswith('?') else '  <-- FAIL')
        if 'FAIL' in flag: bad += 1
        if flag: print(f"{a['type']:10} want={a['value']!s:22} input={inp!s:16} -> {r} (expected {exp}){flag}")
    print(len(cases), 'cases,', bad, 'failures')
    b.close()
