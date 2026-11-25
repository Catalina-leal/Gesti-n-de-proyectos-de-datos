# Segmentación de clientes mayoristas

Grupo 9 · SCY1102 · Sección 002V · Evaluación 3

El repositorio local reproduce la segmentación de la Evaluación 1 y conserva la línea base de la Evaluación 2. Trabaja con la fuente anual pública. La validación con usuarios y la aceptación del sponsor siguen abiertas.

## Demostración

1. Abrir [el notebook con salidas ejecutadas](Segmentacion%20mayorista.ipynb). Revisar calidad, selección de k y asignaciones.
2. Abrir [el tablero de gestión](gestion/tablero.html) en un navegador. Filtrar por **Contingencia** y luego por **Pendiente**. Revisar los tres cortes y el registro de desviaciones.
3. Para mostrar las salidas sin abrir Jupyter, consultar [el reporte de ejecución](resultados/calidad.json), [los perfiles](resultados/perfiles.csv) y [las asignaciones](resultados/clientes_segmentados.csv).

## Reproducir

Con Python 3.12, abrir una terminal en esta carpeta.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe segmentacion.py --salida demo
.venv\Scripts\python.exe -m jupyterlab
```

La última instrucción es opcional y abre JupyterLab para ejecutar el notebook. El CSV público se incluye en el repositorio. El comando de consola genera las salidas en `demo` para conservar el corte original. El notebook usa una carpeta temporal. Para utilizar el modelo serializado, cargar únicamente el artefacto de este repositorio con las dependencias del entorno de reproducción. El modelo espera las seis columnas de gasto en el orden de `variables` y el diccionario `mapa` traduce las etiquetas internas a segmentos.

## Evidencias y seguimiento

- [Script Python](segmentacion.py) y [CSV UCI](datos/wholesale.csv).
- [Base limpia D2](resultados/base_limpia.csv), [comparación de k](resultados/comparacion_k.csv), [estabilidad por semilla](resultados/estabilidad.csv), [canal](resultados/auditoria_canal.csv) y [región](resultados/auditoria_region.csv).
- [Registro de control](gestion/seguimiento.json). Después de actualizarlo con el siguiente corte y sus evidencias, ejecutar `python gestion/actualizar_tablero.py` para regenerar el HTML y registrar el cambio en Git.
- `git log --oneline` muestra el historial del repositorio local. No se necesita un remoto para reproducir las evidencias.
- El informe y la presentación con notas se encuentran en el paquete académico de la Evaluación 3.

## Fuente

Cardoso, M. (2013). *Wholesale customers* [dataset]. UCI Machine Learning Repository. [DOI 10.24432/C5030X](https://doi.org/10.24432/C5030X). Licencia CC BY 4.0. El archivo proporcionado por el equipo, `Wholesale customers data (2).csv`, coincide byte por byte con el CSV de UCI incluido como `datos/wholesale.csv`. Se volvió a correr el pipeline usando el archivo proporcionado y se verificó que las siete salidas CSV coinciden con las de esta entrega. Las salidas incorporan etiquetas en español, identificadores técnicos, atípicos marcados y asignaciones cuando corresponde.