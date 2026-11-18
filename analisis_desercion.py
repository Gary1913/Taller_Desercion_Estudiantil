
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    asistencia_pct aparece como str y debería ser número.
    """
    print("=" * 60)
    print("PASO 1: PRIMERA MIRADA")
    print("=" * 60)

    print("\nTamaño del dataset:", df.shape)

    print("\nTipos y no nulos:")
    df.info()

    print("\nEstadísticas numéricas:")
    print(df.describe())

    for col in ["programa", "jornada", "genero", "ciudad_procedencia", "estado"]:
        print(f"\nValores de {col}:")
        print(df[col].value_counts(dropna=False))


def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
    print("\n" + "=" * 60)
    print("PASO 2: AUDITORÍA DE CALIDAD")
    print("=" * 60)

    # 6.1 Nulos reales
    print("\n[6.1] Nulos reales por columna:")
    print(df.isnull().sum())

    # 6.2 Faltantes disfrazados
    print("\n[6.2] Faltantes disfrazados:")
    print("Guiones en asistencia_pct:", (df["asistencia_pct"] == "-").sum())
    print("Guiones en horas_trabajo_semana:", (df["horas_trabajo_semana"] == "-").sum())
    print("Valores 999 en distancia_km:", (df["distancia_km"] == 999).sum())

    # 6.3 Símbolos dentro del texto
    print("\n[6.3] Celdas de asistencia_pct con '%':",
          df["asistencia_pct"].str.contains("%", regex=False).sum())

    # 6.4 Duplicados
    print("\n[6.4] Filas duplicadas (idénticas en todo):", df.duplicated().sum())
    print("id_estudiante repetidos:", df["id_estudiante"].duplicated().sum())

    # 6.5 Valores imposibles
    edad_imposible = (df["edad"] < 15) | (df["edad"] > 60)
    promedio_imposible = df["promedio_acumulado"] > 5
    print("\n[6.5] Valores imposibles:")
    print("Edades fuera de 15 a 60:", edad_imposible.sum())
    print("Promedios mayores a 5:", promedio_imposible.sum())

    # horas sigue siendo texto: la convertimos SOLO para contar, sin cambiar df
    horas_num = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")
    print("Horas de trabajo mayores a 100:", (horas_num > 100).sum())

    # Formato de fechas (paso 9 de la guía, pero se audita aquí)
    print("\nFechas en formato DD/MM/AAAA:",
          df["fecha_matricula"].str.contains("/", regex=False).sum())


def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    # TODO 3: convertir asistencia_pct, horas_trabajo_semana y distancia_km a número.
    
    print("\n" + "=" * 60)
    print("PASO 3: CONVERTIR TEXTO A NÚMEROS")
    print("=" * 60)

    # --- asistencia_pct ---
    # Contar ANTES de cambiar
    con_pct = df["asistencia_pct"].str.contains("%", regex=False).sum()
    guiones_asist = (df["asistencia_pct"] == "-").sum()

    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "", regex=False)
    registrar("paso 3", "asistencia_pct", "quitar símbolo %", con_pct,
              "El % impide que la columna sea numérica; el valor no cambia al quitarlo")

    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"].replace("-", np.nan), errors="coerce")
    registrar("paso 3", "asistencia_pct", "guion a nulo y convertir a número", guiones_asist,
              "El guion significa 'sin dato'; como nulo real se puede tratar en el paso 7")

    # --- horas_trabajo_semana ---
    guiones_horas = (df["horas_trabajo_semana"] == "-").sum()
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")
    registrar("paso 3", "horas_trabajo_semana", "guion a nulo y convertir a número", guiones_horas,
              "El guion significa 'sin dato'; se revisa en el paso 8 con la columna trabaja")

    # --- distancia_km ---
    n_999 = (df["distancia_km"] == 999).sum()
    df["distancia_km"] = df["distancia_km"].replace(999, np.nan)
    registrar("paso 3", "distancia_km", "999 a nulo", n_999,
              "999 es un código de 'sin dato', no una distancia real; deja la media inflada")

    # --- Verificar el resultado ---
    print("\nTipos después de convertir:")
    print(df[["asistencia_pct", "horas_trabajo_semana", "distancia_km"]].dtypes)
    print("\nNulos después de convertir:")
    print(df[["asistencia_pct", "horas_trabajo_semana", "distancia_km"]].isnull().sum())
    return df

def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    # TODO 4: unificar las escrituras de programa, jornada, genero y ciudad_procedencia.

    print("\n" + "=" * 60)
    print("PASO 4: UNIFICAR CATEGORÍAS")
    print("=" * 60)

    # Variantes que no se arreglan solo con minúsculas (tildes y abreviaturas)
    variantes_extra = {
        "programa": {"ingenieria de sistemas": "Ingeniería de Sistemas",
                     "psicologia": "Psicología"},
        "jornada": {},
        "genero": {"m": "Masculino", "f": "Femenino"},
        "ciudad_procedencia": {"bogota": "Bogotá", "medellin": "Medellín"},
    }

    for col in ["programa", "jornada", "genero", "ciudad_procedencia"]:
        antes = df[col].copy()

        # 1. Normalizar: quitar espacios y pasar a minúsculas
        df[col] = df[col].str.strip().str.lower()

        # 2. Diccionario: cada valor válido en minúscula -> su forma correcta
        diccionario = {valor.lower(): valor for valor in VALIDOS[col]}
        diccionario.update(variantes_extra[col])
        df[col] = df[col].replace(diccionario)

        # 3. Contar cuántas celdas cambiaron (sin contar los nulos)
        cambiadas = (antes.ne(df[col]) & antes.notna()).sum()
        registrar("paso 4", col, "unificar escrituras con strip, lower y diccionario", cambiadas,
                  "Eran el mismo valor escrito distinto; si no se unifican, un grupo se parte en varios")

        # 4. Verificar
        print(f"\nValores de {col} después de unificar:")
        print(df[col].value_counts(dropna=False))
    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    # TODO 5: convertir fecha_matricula a fecha con los dos formatos.
    print("\n" + "=" * 60)
    print("PASO 5: FECHAS EN DOS FORMATOS")
    print("=" * 60)

    # Contar ANTES de convertir: las DD/MM/AAAA tienen '/'
    formato_dmy = df["fecha_matricula"].str.contains("/", regex=False).sum()

    iso = pd.to_datetime(df["fecha_matricula"], format="%Y-%m-%d", errors="coerce")
    dmy = pd.to_datetime(df["fecha_matricula"], format="%d/%m/%Y", errors="coerce")
    df["fecha_matricula"] = iso.fillna(dmy)

    registrar("paso 5", "fecha_matricula", "convertir a fecha con dos formatos", formato_dmy,
              "Había fechas en AAAA-MM-DD y en DD/MM/AAAA; con un solo formato la mitad quedaría vacía")

    print("Tipo:", df["fecha_matricula"].dtype)
    print("Fechas que no se pudieron convertir:", df["fecha_matricula"].isnull().sum())
    print("Fecha más antigua:", df["fecha_matricula"].min())
    print("Fecha más reciente:", df["fecha_matricula"].max())
    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    # TODO 6: eliminar duplicados, registrar la decisión y devolver el dataframe.
    print("\n" + "=" * 60)
    print("PASO 6: DUPLICADOS")
    print("=" * 60)

    filas_antes = len(df)
    n_duplicados = df.duplicated().sum()

    df = df.drop_duplicates().reset_index(drop=True)

    registrar("paso 6", "todas", "eliminar filas duplicadas", n_duplicados,
              "Tienen el mismo id_estudiante y todos los datos iguales: es el mismo estudiante "
              "registrado dos veces y contaría doble en las tasas")

    print("Filas antes:", filas_antes)
    print("Duplicados eliminados:", n_duplicados)
    print("Filas después:", len(df))
    print("id_estudiante repetidos que quedan:", df["id_estudiante"].duplicated().sum())
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    # TODO 7: tratar los nulos de promedio_acumulado, ciudad_procedencia y tipo_colegio.

    print("\n" + "=" * 60)
    print("PASO 7: FALTANTES REALES")
    print("=" * 60)

    # --- promedio_acumulado: eliminar filas ---
    nulos_promedio = df["promedio_acumulado"].isnull().sum()
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("paso 7", "promedio_acumulado", "eliminar filas", nulos_promedio,
              "Una nota no se puede inventar: imputarla escondería la relación entre nota y deserción")

    # --- ciudad_procedencia y tipo_colegio: marcar 'Sin dato' ---
    for col in ["ciudad_procedencia", "tipo_colegio"]:
        nulos = df[col].isnull().sum()
        df[col] = df[col].fillna("Sin dato")
        registrar("paso 7", col, "reemplazar nulos por 'Sin dato'", nulos,
                  "Eliminar al estudiante haría perder su nota, asistencia y estado, que sí son útiles")

    # --- motivo_retiro: dejar como nulo, pero verificar ---
    desertores_sin_motivo = ((df["estado"] == "desertor") & df["motivo_retiro"].isnull()).sum()
    no_desertores_con_motivo = ((df["estado"] != "desertor") & df["motivo_retiro"].notna()).sum()
    print("Desertores sin motivo de retiro:", desertores_sin_motivo)
    print("No desertores con motivo de retiro:", no_desertores_con_motivo)
    registrar("paso 7", "motivo_retiro", "dejar como nulo", df["motivo_retiro"].isnull().sum(),
              "Nulo esperado: la pregunta solo aplica a desertores")

    # --- Verificar ---
    print("\nFilas después del paso 7:", len(df))
    print("\nNulos que quedan:")
    print(df.isnull().sum()[df.isnull().sum() > 0])

        # --- asistencia_pct y distancia_km: dejar como nulo ---
    registrar("paso 7", "asistencia_pct", "dejar como nulo", df["asistencia_pct"].isnull().sum(),
              "Inventar la asistencia distorsionaría la pregunta 5; quedan fuera de los cuartiles")
    registrar("paso 7", "distancia_km", "dejar como nulo", df["distancia_km"].isnull().sum(),
              "Ninguna de las cinco preguntas usa la distancia; imputarla no aporta")
    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # TODO 8: tratar edad, promedio_acumulado y horas_trabajo_semana, con sus justificaciones.

    print("\n" + "=" * 60)
    print("PASO 8: VALORES IMPOSIBLES")
    print("=" * 60)

    # --- promedio_acumulado: convertir escala 0-100 a 0-5 ---
    fuera_escala = df["promedio_acumulado"] > 5
    print("Promedios mayores a 5 (antes):", sorted(df.loc[fuera_escala, "promedio_acumulado"].tolist()))
    n_prom = fuera_escala.sum()
    df.loc[fuera_escala, "promedio_acumulado"] = df.loc[fuera_escala, "promedio_acumulado"] / 20
    print("Esos mismos promedios (después):", sorted(df.loc[fuera_escala, "promedio_acumulado"].tolist()))
    registrar("paso 8", "promedio_acumulado", "dividir entre 20 (escala 0-100 a 0-5)", n_prom,
              "Los valores estaban en escala 0-100; al convertirlos quedan dentro del rango normal de notas")

    # --- edad: imposibles a nulo y luego mediana ---
    edad_imposible = (df["edad"] < 15) | (df["edad"] > 60)
    print("\nEdades imposibles:", sorted(df.loc[edad_imposible, "edad"].tolist()))
    n_edad = edad_imposible.sum()
    df.loc[edad_imposible, "edad"] = np.nan
    mediana_edad = df["edad"].median()          # se calcula sin las edades imposibles
    df["edad"] = df["edad"].fillna(mediana_edad)
    print("Mediana usada:", mediana_edad)
    registrar("paso 8", "edad", f"edades fuera de 15-60 a nulo y luego mediana ({mediana_edad})", n_edad,
              "Son errores de registro; la mediana no se afecta por los extremos como el 150")

    # --- horas_trabajo_semana ---
    print("\nValores de trabaja:")
    print(df["trabaja"].value_counts())
    print("\nNulos de horas según trabaja:")
    print(df.loc[df["horas_trabajo_semana"].isnull(), "trabaja"].value_counts())

    # Regla 1: si no trabaja, 0 horas
    regla_cero = (df["trabaja"] == "no") & df["horas_trabajo_semana"].isnull()
    n_cero = regla_cero.sum()
    df.loc[regla_cero, "horas_trabajo_semana"] = 0
    registrar("paso 8", "horas_trabajo_semana", "nulo a 0 si trabaja es 'no'", n_cero,
              "Si el estudiante no trabaja, sus horas de trabajo son 0; el guion significaba 'no aplica'")

    # Regla 2: más de 100 horas es imposible -> nulo -> mediana de quienes trabajan
    horas_imposibles = df["horas_trabajo_semana"] > 100
    n_horas = horas_imposibles.sum()
    df.loc[horas_imposibles, "horas_trabajo_semana"] = np.nan
    mediana_trab = df.loc[df["trabaja"] != "no", "horas_trabajo_semana"].median()
    df.loc[horas_imposibles, "horas_trabajo_semana"] = mediana_trab
    print("\nMediana de horas de quienes trabajan:", mediana_trab)
    registrar("paso 8", "horas_trabajo_semana", f"más de 100 a mediana de quienes trabajan ({mediana_trab})", n_horas,
              "Nadie trabaja más de 100 horas y estudia; la mediana de quienes trabajan es un valor realista")

    # --- Verificar ---
    print("\nNulos que quedan en horas:", df["horas_trabajo_semana"].isnull().sum())
    print("\nResumen después del paso 8:")
    print(df[["promedio_acumulado", "edad", "horas_trabajo_semana"]].describe())
    print("No trabajan pero tienen horas > 0:",
          ((df["trabaja"] == "no") & (df["horas_trabajo_semana"] > 0)).sum())
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    # TODO 9: crear las columnas desertor y cuartil_asistencia.
    print("\n" + "=" * 60)
    print("PASO 9: VARIABLES NUEVAS")
    print("=" * 60)

    # --- desertor: True si estado es 'desertor' ---
    df["desertor"] = df["estado"].eq("desertor")
    print("Desertores (True):", df["desertor"].sum(), "de", len(df), "estudiantes")
    print("Tasa general de deserción:", round(df["desertor"].mean(), 3))

    # --- cuartil_asistencia: 4 grupos de igual tamaño ---
    df["cuartil_asistencia"] = pd.qcut(df["asistencia_pct"], 4, labels=["Q1", "Q2", "Q3", "Q4"])

    print("\nEstudiantes por cuartil:")
    print(df["cuartil_asistencia"].value_counts(dropna=False).sort_index())

    print("\nRango de asistencia de cada cuartil:")
    print(df.groupby("cuartil_asistencia", observed=True)["asistencia_pct"].agg(["min", "max", "count"]))

    registrar("paso 9", "desertor", "crear columna True/False desde estado", len(df),
              "Permite calcular la tasa de deserción como el promedio de True")
    registrar("paso 9", "cuartil_asistencia", "dividir asistencia_pct en 4 grupos con qcut",
              df["cuartil_asistencia"].notna().sum(),
              "Grupos de tamaño parecido dan tasas más confiables que los valores exactos")
    return df


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    # TODO 10: dibujar, guardar en GRAFICOS / "mapa_faltantes.png" y mostrar.
    
    GRAFICOS.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
    plt.title("Mapa de faltantes (dataset original)")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "mapa_faltantes.png", bbox_inches="tight")
    plt.show()


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    # TODO 11: dibujar los cuatro boxplots, guardar en GRAFICOS / "distribuciones_antes_despues.png" y mostrar.
    
    fig, ejes = plt.subplots(2, 2, figsize=(12, 8))

    sns.boxplot(x=antes["promedio_acumulado"], ax=ejes[0, 0])
    ejes[0, 0].set_title("promedio_acumulado (antes)")
    sns.boxplot(x=despues["promedio_acumulado"], ax=ejes[0, 1])
    ejes[0, 1].set_title("promedio_acumulado (después)")

    sns.boxplot(x=antes["edad"], ax=ejes[1, 0])
    ejes[1, 0].set_title("edad (antes)")
    sns.boxplot(x=despues["edad"], ax=ejes[1, 1])
    ejes[1, 1].set_title("edad (después)")

    plt.tight_layout()
    plt.savefig(GRAFICOS / "distribuciones_antes_despues.png", bbox_inches="tight")
    plt.show()


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    # TODO 12: dibujar la tasa por programa, guardar en GRAFICOS / "tasa_desercion_por_programa.png" y mostrar.
    
    tasa = df.groupby("programa")["desertor"].mean().sort_values(ascending=False)

    plt.figure(figsize=(10, 6))
    tasa.plot(kind="bar")
    plt.title("Tasa de deserción por programa")
    plt.ylabel("Tasa de deserción")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "tasa_desercion_por_programa.png", bbox_inches="tight")
    plt.show()


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    # TODO 13: dibujar la tasa por cuartil, guardar en GRAFICOS / "tasa_desercion_por_asistencia.png" y mostrar.
    
    tasa = df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()

    plt.figure(figsize=(8, 5))
    tasa.plot(kind="bar")
    plt.title("Tasa de deserción por cuartil de asistencia")
    plt.xlabel("Cuartil de asistencia (Q1 = más baja, Q4 = más alta)")
    plt.ylabel("Tasa de deserción")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(GRAFICOS / "tasa_desercion_por_asistencia.png", bbox_inches="tight")
    plt.show()


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    # TODO 14: responder las cinco preguntas con groupby() y agg().
    
    print("\n" + "=" * 60)
    print("PASO 10: LAS CINCO PREGUNTAS")
    print("=" * 60)

    # Pregunta 1: tasa de deserción por programa
    print("\nPregunta 1: tasa de deserción por programa")
    p1 = df.groupby("programa").agg(tasa=("desertor", "mean"),
                                    estudiantes=("desertor", "size"))
    print(p1.sort_values("tasa", ascending=False).round(3))

    # Pregunta 2: becados frente a no becados
    print("\nPregunta 2: tasa de deserción según beca")
    p2 = df.groupby("beca").agg(tasa=("desertor", "mean"),
                                estudiantes=("desertor", "size"))
    print(p2.round(3))

    # Pregunta 3: promedio acumulado por jornada
    print("\nPregunta 3: promedio acumulado por jornada")
    p3 = df.groupby("jornada").agg(promedio=("promedio_acumulado", "mean"),
                                   estudiantes=("promedio_acumulado", "size"))
    print(p3.sort_values("promedio").round(3))

    # Pregunta 4: materias reprobadas, desertores frente a activos (sin graduados)
    print("\nPregunta 4: materias reprobadas (sin graduados)")
    sin_graduados = df[df["estado"] != "graduado"]
    p4 = sin_graduados.groupby("estado").agg(materias_reprobadas=("materias_reprobadas", "mean"),
                                             estudiantes=("materias_reprobadas", "size"))
    print(p4.round(3))

    # Pregunta 5: deserción por cuartil de asistencia
    print("\nPregunta 5: tasa de deserción por cuartil de asistencia")
    p5 = df.groupby("cuartil_asistencia", observed=True).agg(
        tasa=("desertor", "mean"),
        asistencia_promedio=("asistencia_pct", "mean"),
        estudiantes=("desertor", "size"))
    print(p5.round(3))


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
