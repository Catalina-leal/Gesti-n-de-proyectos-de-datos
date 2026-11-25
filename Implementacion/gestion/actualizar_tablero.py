"""Regenera el tablero HTML desde el registro de seguimiento versionado."""
from pathlib import Path
from html import escape
import json

tracking = Path(__file__).resolve().parent
source = tracking / "seguimiento.json"
board = json.loads(source.read_text(encoding="utf-8"))

def table(heads, rows, *, tasks=False):
    header = "".join(f"<th scope='col'>{escape(h)}</th>" for h in heads)
    body = []
    for row in rows:
        cells = []
        for idx, v in enumerate(row):
            value = escape(v)
            if tasks and idx == 7 and v.startswith(("../", "tablero")):
                value = f'<a href="{value}">Abrir evidencia</a>'
            cells.append(f"<td>{value}</td>")
        status = f' data-status="{escape(row[5])}"' if tasks else ""
        body.append(f"<tr{status}>{''.join(cells)}</tr>")
    return "<div class='scroll'><table><thead><tr>"+header+"</tr></thead><tbody>"+"".join(body)+"</tbody></table></div>"

task_table = table(["ID","EDT / hito","Plan","Responsable","Tarea","Estado","Ejecución documentada","Evidencia","Próximo paso"], board["tareas"], tasks=True)
report_table = table(["Corte","Etapa","Resultado / decisión"], board["reportes"])
change_table = table(["ID","Desviación o riesgo","Impacto en línea base","Acción aplicada","Responsable","Control de cierre"], board["desviaciones"])
statuses = sorted({row[5] for row in board["tareas"]})
controls = "".join(f"<option>{escape(status)}</option>" for status in statuses)
page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Seguimiento de la segmentación mayorista</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f7fa;color:#182c43;font:16px system-ui,sans-serif}}header{{background:#153553;color:#fff;padding:2.4rem max(5vw,1rem)}}header p{{max-width:52rem;color:#d9e6ed}}h1{{font-size:clamp(1.65rem,4vw,2.8rem);margin:.25rem 0}}h2{{font-size:1.35rem}}main{{margin:auto;max-width:1600px;padding:1rem max(3vw,1rem) 3rem}}section{{margin:1.4rem 0}}.scroll{{overflow:auto;border:1px solid #dce5ed;border-radius:.6rem;background:white}}table{{border-collapse:collapse;width:100%;min-width:52rem;font-size:.89rem}}th,td{{text-align:left;padding:.65rem;vertical-align:top;border-bottom:1px solid #e0e8ef}}th{{background:#eaf1f6}}td:nth-child(1){{font-weight:700;white-space:nowrap}}tbody tr:nth-child(even){{background:#f8fbfd}}a{{color:#00665c}}nav a{{margin-right:1.25rem}}label{{font-weight:650}}select,input{{font:inherit;padding:.35rem .55rem;border:1px solid #90a5b5;border-radius:.3rem;color:#182c43;background:white;margin:.25rem .65rem .5rem .2rem}}.count{{font-weight:700;color:#00665c}}[hidden]{{display:none}}.note{{max-width:72rem}}
</style></head><body><header><p>Gestión de Proyectos de Datos · Grupo 9</p><h1>Seguimiento de la segmentación mayorista</h1><p>Corte del {board['corte']} · 12 semanas de línea base · presupuesto adicional previsto de $0</p></header><main>
<nav aria-label="Secciones"><a href="#tareas">Plan y ejecución</a><a href="#reportes">Cortes de avance</a><a href="#control">Desviaciones y control</a><a href="seguimiento.json">Registro versionado</a></nav>
<p class="note">{escape(board['base'])}</p>
<section id="tareas"><h2>Plan y ejecución</h2><label for="state">Estado</label><select id="state"><option value="">Todos</option>{controls}</select><label for="query">Buscar</label><input id="query" type="search" placeholder="Hito, responsable o tarea"><span id="count" class="count" aria-live="polite"></span>{task_table}</section>
<section id="reportes"><h2>Cortes de avance</h2><p>Registros de hitos de trabajo documentados hasta el {board['corte']}. Las revisiones semanales y quincenales con la empresa se mantienen como cadencia del plan.</p>{report_table}</section>
<section id="control"><h2>Desviaciones y control</h2>{change_table}<p class="note">Para el siguiente corte, el líder revisa el estado, agrega evidencia y fecha al registro, y versiona el JSON junto con la vista HTML. H5 y la aceptación de H6 se cierran con actas.</p></section>
</main><script>
const state=document.querySelector('#state');
const query=document.querySelector('#query');
const rows=[...document.querySelectorAll('#tareas tbody tr')];
const count=document.querySelector('#count');
function filter(){{
  const search=query.value.trim().toLocaleLowerCase('es');
  let shown=0;
  for(const row of rows){{
    row.hidden=Boolean((state.value && row.dataset.status !== state.value) ||
        (search && !row.textContent.toLocaleLowerCase('es').includes(search)));
    if(!row.hidden) shown++;
  }}
  count.textContent=shown+' de '+rows.length+' tareas';
}}
state.addEventListener('change',filter);
query.addEventListener('input',filter);
filter();
</script></body></html>"""
(tracking / "tablero.html").write_text(page, encoding="utf-8")

