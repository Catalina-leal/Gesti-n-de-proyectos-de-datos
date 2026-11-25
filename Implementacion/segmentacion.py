"""Segmentación reproducible para el piloto académico."""
import argparse
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import time

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "datos" / "wholesale.csv"
FEATURES = ["Fresh", "Milk", "Grocery", "Frozen", "Detergents_Paper", "Delicassen"]
CHANNELS = {1: "Horeca", 2: "Retail"}
REGIONS = {1: "Lisboa", 2: "Oporto", 3: "Otra"}
SEED = 42
VERSION = "1.0"


def preparar(source):
    raw = pd.read_csv(source)
    if set(raw) != set(FEATURES + ["Channel", "Region"]):
        raise ValueError("El CSV no tiene las ocho columnas esperadas.")
    data = raw.apply(pd.to_numeric, errors="raise")
    spends = data[FEATURES]
    quality = {
        "filas": len(data), "columnas": len(data.columns),
        "nulos": int(data.isna().sum().sum()),
        "duplicados": int(data.duplicated().sum()),
        "negativos": int(spends.lt(0).sum().sum()),
        "no_finitos": int((~np.isfinite(spends)).sum().sum()),
        "codigos_invalidos": int((~data.Channel.isin(CHANNELS) | ~data.Region.isin(REGIONS)).sum()),
    }
    if any(quality[key] for key in ("nulos", "negativos", "no_finitos", "codigos_invalidos")):
        raise ValueError(f"Errores críticos de entrada: {quality}")
    if quality["duplicados"]:
        raise ValueError("Revisar filas idénticas con el dueño de los datos antes de consolidar.")
    if len(data) < 7:
        raise ValueError("Se requieren al menos siete registros para evaluar k hasta 6.")
    q1, q3 = spends.quantile(.25), spends.quantile(.75)
    iqr = q3 - q1
    flagged = (spends.lt(q1 - 1.5 * iqr) | spends.gt(q3 + 1.5 * iqr)).any(axis=1)
    quality.update(atipicos=int(flagged.sum()), sha256=sha256(source.read_bytes()).hexdigest(),
                   version=VERSION)
    data = data.assign(
        cliente_id=[f"CL-{idx:04d}" for idx in range(1, len(data)+1)],
        canal=data.Channel.map(CHANNELS), region=data.Region.map(REGIONS), atipico_iqr=flagged,
    ).drop(columns=["Channel", "Region"])
    return data[["cliente_id", "canal", "region"] + FEATURES + ["atipico_iqr"]], quality


def pipeline(k, seed):
    return make_pipeline(FunctionTransformer(np.log1p), StandardScaler(),
                         KMeans(n_clusters=k, random_state=seed, n_init=10))


def ejecutar(source=SOURCE, out=ROOT / "resultados"):
    start = time.perf_counter()
    data, quality = preparar(source)
    spends = data[FEATURES]
    candidates = []
    with threadpool_limits(limits=1):
        for k in range(2, 7):
            model = pipeline(k, SEED).fit(spends)
            transformed = model[:-1].transform(spends)
            score = silhouette_score(transformed, model[-1].labels_)
            candidates.append((k, score, model))
        k, score, model = max(candidates, key=lambda row: row[1])
        labels = model.predict(spends)
        stability = [
            (seed, adjusted_rand_score(labels, pipeline(k, seed).fit_predict(spends)))
            for seed in (0, 7, 24, 99)
        ]
    medians = spends.assign(raw_group=labels).groupby("raw_group").median()
    ordered = medians.sort_values("Grocery", kind="stable").index
    mapping = {int(group): i for i, group in enumerate(ordered, 1)}
    names = ({1: "Frescos y congelados", 2: "Lácteos, abarrotes e higiene"}
             if k == 2 else {i: f"Perfil {i}" for i in mapping.values()})
    assigned = data.assign(segmento=pd.Series(labels, index=data.index).map(mapping))
    assigned["perfil"] = assigned.segmento.map(names)
    grouped = assigned.groupby(["segmento", "perfil"])
    profiles = grouped[FEATURES].median().join(grouped.size().rename("clientes")).reset_index()
    quality.update(k=k, silhouette=score, asignados=len(assigned),
                   ari_min=min(value for _, value in stability),
                   python=__import__("platform").python_version(),
                   sklearn=sklearn.__version__, pandas=pd.__version__, numpy=np.__version__)
    out.mkdir(parents=True, exist_ok=True)
    data.to_csv(out / "base_limpia.csv", index=False, encoding="utf-8-sig")
    assigned.to_csv(out / "clientes_segmentados.csv", index=False, encoding="utf-8-sig")
    profiles.to_csv(out / "perfiles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([(k, score) for k, score, _ in candidates],
                 columns=["k", "silhouette"]).to_csv(out / "comparacion_k.csv", index=False)
    pd.DataFrame(stability, columns=["semilla", "ari"]).to_csv(out / "estabilidad.csv", index=False)
    for field in ("canal", "region"):
        audit = assigned.groupby([field, "segmento"]).size().unstack(fill_value=0)
        audit.to_csv(out / f"auditoria_{field}.csv", encoding="utf-8-sig")
    joblib.dump({"modelo": model, "mapa": mapping, "perfiles": names, "variables": FEATURES,
                 "version": VERSION}, out / "modelo.joblib")
    saved = joblib.load(out / "modelo.joblib")
    if not np.array_equal(saved["modelo"].predict(spends), labels):
        raise RuntimeError("El modelo guardado cambió las asignaciones.")
    quality.update(prediccion_verificada=True, segundos=round(time.perf_counter()-start, 3),
                   ejecucion=datetime.now().astimezone().isoformat(timespec="seconds"))
    (out / "calidad.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return quality


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=SOURCE)
    parser.add_argument("--salida", type=Path, default=ROOT / "resultados")
    args = parser.parse_args()
    print(json.dumps(ejecutar(args.entrada, args.salida), indent=2))