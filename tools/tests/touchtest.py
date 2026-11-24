"""Synthetic pointer events: finger draw, two-finger pinch, pen + finger pan, eraser, undo/redo."""
import glob
from playwright.sync_api import sync_playwright
exe = glob.glob('/home/longge/.cache/ms-playwright/chromium-1234/*/chrome')[0]
JS = r'''
() => {
  const cv = document.querySelector("#cv"), r = cv.getBoundingClientRect(), out = [];
  const ev = (type, id, ptype, x, y) => cv.dispatchEvent(new PointerEvent(type, {pointerId:id, pointerType:ptype, clientX:r.left+x, clientY:r.top+y, bubbles:true, button:0, isPrimary:true}));
  const stroke = (id, ptype, pts) => { ev("pointerdown", id, ptype, ...pts[0]); pts.slice(1).forEach(p => ev("pointermove", id, ptype, ...p)); ev("pointerup", id, ptype, ...pts[pts.length-1]); };
  const st = () => JSON.stringify(Board.debug());
  stroke(11, "touch", [[100,100],[150,130],[200,100]]); out.push("finger draw -> " + st());
  ev("pointerdown", 21, "touch", 200, 200); ev("pointerdown", 22, "touch", 300, 200);
  ev("pointermove", 22, "touch", 400, 200); ev("pointermove", 21, "touch", 100, 200);
  ev("pointerup", 21, "touch", 100, 200); ev("pointerup", 22, "touch", 400, 200); out.push("pinch out -> " + st());
  stroke(31, "pen", [[120,220],[160,260],[220,240]]); out.push("pen draw -> " + st());
  stroke(41, "touch", [[100,100],[160,160]]); out.push("finger after pen (should pan, not draw) -> " + st());
  document.querySelector("#btnUndo").click(); out.push("undo -> " + st());
  document.querySelector("#btnRedo").click(); out.push("redo -> " + st());
  document.querySelector('[data-tool="eraser"]').click();
  const d = Board.debug(); // erase where the pen stroke is: world->screen
  stroke(51, "pen", [[120,220],[160,260],[220,240]]); out.push("erase pen stroke -> " + st());
  document.querySelector("#btnUndo").click(); out.push("undo erase -> " + st());
  document.querySelector("#btnClear").click(); out.push("clear -> " + st());
  document.querySelector("#btnUndo").click(); out.push("undo clear -> " + st());
  document.querySelector("#zFit").click(); out.push("reset view -> " + st());
  return out;
}'''
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page(viewport={'width':1024,'height':768})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/longge/code/edutech/index.html'); pg.click('[data-subject="maths"]'); pg.click('#btnRandom'); pg.wait_for_timeout(600)
    for line in pg.evaluate(JS): print(line)
    pg.wait_for_timeout(200); print('page errors:', errs); b.close()
