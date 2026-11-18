# Taller práctico proyecto integrador: calidad de datos para la retención estudiantil

Una institución de educación superior quiere entender qué factores están asociados a la deserción, para diseñar estrategias de retención tempranas. Antes de responder preguntas de análisis, el equipo de datos debe garantizar que la información sea confiable. Este taller trabaja justo ese paso: auditar, limpiar y documentar los datos, y después responder cinco preguntas con esos datos limpios.

Los datos son sintéticos. Fueron generados para el taller y no corresponden a estudiantes reales.

## Requisitos

- Python 3.10 o superior
- Git
- Lo visto en los talleres de Pandas y de limpieza de datos

## Cómo empezar

1. Clona el repositorio y entra a la carpeta del proyecto:

   ```
   git clone <URL-DEL-REPOSITORIO>
   cd <NOMBRE-DE-LA-CARPETA>
   ```

2. Crea y activa un ambiente virtual. Las instrucciones para Windows y Mac/Linux están en `LEEME_ambiente.txt`.

3. Instala las librerías:

   ```
   pip install -r requirements.txt
   ```

4. Ejecuta el script:

   ```
   python analisis_desercion.py
   ```

Ejecuta el comando desde la carpeta del proyecto.

## Estructura del proyecto

```
proyecto/
├── analisis_desercion.py   Script principal. Tiene un TODO por cada paso.
├── requirements.txt        Versiones de las librerías.
├── LEEME_ambiente.txt      Pasos para crear el ambiente virtual.
├── README.md               Este archivo.
├── .gitignore              Archivos que Git no debe subir.
└── Data/
    ├── raw/
    │   └── datos_estudiantes.csv   Dataset original. No lo modifiques.
    └── processed/
        ├── .gitkeep                Mantiene la carpeta en el repositorio.
        ├── dataset_limpio.csv      Lo genera el script. No se sube (está en .gitignore).
        ├── decisiones.csv          Lo genera el script. Sí se sube.
        └── graficos/               Lo genera el script. Sí se sube.
```

Lo que genera el script (`dataset_limpio.csv`, `decisiones.csv` y `graficos/`) aparece en `Data/processed/` al ejecutarlo. Los dos últimos se suben al repositorio, porque son parte de la entrega.

## Qué debes hacer

Completa los TODO de `analisis_desercion.py` en orden. Cada función tiene un docstring con preguntas: respóndelas antes de escribir el código. Cada decisión que tomes debe quedar registrada con `registrar()`.

Cuando termines, el script debe producir:

- `Data/processed/dataset_limpio.csv`: el dataset limpio.
- `Data/processed/decisiones.csv`: la tabla de decisiones.
- `Data/processed/graficos/`: los cuatro gráficos.

La guía del taller (`Taller_Retencion_Estudiantil.docx`) explica cada método antes de usarlo, con ejemplos y errores frecuentes.

## Entrega

Sube tu código completo al repositorio y envía el enlace por el formulario de entrega. La entrega es individual.

El repositorio debe incluir:

- `analisis_desercion.py` con todos los TODO completados.
- `Data/processed/decisiones.csv` y la carpeta `Data/processed/graficos/`.
- Un `README.md` al final de este archivo, con una sección titulada **Mis decisiones y respuestas**. Debe incluir:
  0. El diccionario de datos: la tabla de las 23 columnas con tipo, descripción y rol, completada según el paso 1 de la guía.
  1. Tu diagnóstico de calidad: qué problemas encontraste y en qué columnas.
  2. Tus decisiones de limpieza, con su justificación.
  3. Las respuestas a las cinco preguntas, cada una con el número de estudiantes por grupo.
  4. Tu respuesta a la reflexión sobre asociación y causalidad.
  5. Tu respuesta a la reflexión sobre `motivo_retiro` y la predicción.
  6. Tu respuesta a la reflexión sobre el uso de variables sensibles.

El script debe ejecutarse sin errores desde cero. Cada decisión necesita una justificación, y cada conclusión debe apoyarse en un número del análisis.



# Mis decisiones y respuestas

## 0. Diccionario de datos


| Columna | Tipo | Descripción | Rol |
|---|---|---|---|
| id_estudiante | texto | Código único que identifica a cada estudiante | identificación |
| programa | categórica | Carrera que cursa el estudiante | explicativa |
| facultad | categórica | Facultad a la que pertenece el programa | explicativa |
| jornada | categórica | Horario de estudio: diurna, nocturna o fin de semana | explicativa |
| semestre | numérica | Semestre que cursa actualmente (1 a 10) | explicativa |
| promedio_acumulado | numérica | Nota promedio de la carrera, en escala de 0 a 5 | explicativa |
| creditos_aprobados | numérica | Cuantos creditos a aprobado el estudiante | explicativa |
| materias_reprobadas | numérica | Cantidad de materias que ha perdido | explicativa |
| asistencia_pct | numérica (llega como texto) | Porcentaje de asistencia a clases | explicativa |
| sesiones_tutoria | numérica | Número de tutorías a las que asistió | explicativa |
| cambios_programa | numérica (0 o 1) | Indica si el estudiante ha cambiado de carrera | explicativa |
| estrato | categórica ordinal | Estrato socioeconómico de la vivienda (1 a 6) | explicativa |
| beca | categórica | Indica si el estudiante recibe una beca (sí o no) | explicativa |
| trabaja | categórica | Indica si el estudiante trabaja (sí o no) | explicativa |
| horas_trabajo_semana | numérica (llega como texto) | Horas que trabaja a la semana | explicativa |
| distancia_km | numérica | Distancia en kilómetros entre su vivienda y la sede | explicativa |
| edad | numérica | Edad del estudiante en años | explicativa |
| genero | categórica | Género del estudiante | explicativa |
| ciudad_procedencia | categórica | Ciudad de donde viene el estudiante | explicativa |
| tipo_colegio | categórica | Tipo de colegio donde terminó el bachillerato | explicativa |
| fecha_matricula | fecha (llega como texto) | Fecha en que se matriculó en la institución | explicativa |
| estado | categórica | Situación del estudiante: activo, graduado o desertor | resultado |
| motivo_retiro | categórica | Razón por la que el estudiante se retiró; solo existe para desertores | resultado |

## 1. Diagnóstico de calidad

### Primera mirada (Paso 1)
**¿Alguna columna numérica aparece como texto? ¿Por qué?**
Sí: asistencia_pct y horas_trabajo_semana aparecen como texto (str). Pasa porque
se puso algun dato diferente a un numero, y pandas la identifica la columna como tipo texto

**¿Coinciden filas y columnas con el enunciado?**
El dataset tiene 10150 filas y 23 columnas. Las 23 columnas coinciden con el
diccionario. Las filas incluían 150 duplicados; sin ellos quedan 10000.

**¿Qué mínimo o máximo no tiene sentido?**
- promedio_acumulado: máximo de 78, cuando la escala es de 0 a 5.
- edad: mínimo de 12 y máximo de 150.
- distancia_km: máximo de 999, un código de "sin dato".

**¿Qué valores parecen variantes de otros?**
- programa: "Ingenieria de Sistemas" (144) y "Psicologia" (116), sin tilde.
- jornada: "diurna" (318), "nocturna" (89) y "NOCTURNA" (78).
- genero: "M" (239), "F" (167) y "femenino" (153).
- ciudad_procedencia: "BOGOTÁ" (128), "Bogota" (120), "bogota" (118),
  "medellin" (90) y "Medellin" (86).

### Auditoría (Paso 2)

**Nulos reales**
- promedio_acumulado: 304, distancia_km: 199, ciudad_procedencia: 103,
  tipo_colegio: 152. Son errores, porque ese dato debería existir para todos.
- motivo_retiro: 6877. Es un nulo esperado: coincide con los activos (5977)
  más los graduados (900), y a ellos la pregunta no les aplica.

**Faltantes disfrazados**
- asistencia_pct: 202 guiones.
- horas_trabajo_semana: 2822 guiones. podrian  ser de estudiantes que no trabajan
- distancia_km: 152 valores 999. Sumados a los 199 nulos, faltan 351 distancias.

**Símbolos**
- asistencia_pct: 300 celdas tienen el signo %. Junto con los guiones, por eso
  la columna se lee como texto.

**Duplicados**
- Hay 150 filas idénticas, y también 150 id_estudiante repetidos. Dos
  estudiantes distintos podrían tener datos parecidos, pero no el mismo id.
  Como el id se repite, son el mismo estudiante registrado dos veces.
  Al quitarlos quedan 10000 estudiantes.

**Valores imposibles**
- edad fuera de 15 a 60: 12 filas.
- promedio_acumulado mayor a 5: 17 filas (parecen estar en escala de 0 a 100).
- horas_trabajo_semana mayor a 100: 30 filas.

**Fechas:** 3052 fechas están en formato DD/MM/AAAA (cerca del 30 %).

**¿Cuál problema afecta más el análisis?**
Los duplicados. Hay 150 filas repetidas, y si un desertor aparece dos veces,
cuenta doble en la tasa de deserción. Es un error que no se nota: el cálculo
funciona, pero da un resultado equivocado.

## 2. Decisiones de limpieza

### Paso 3: convertir texto a números
- asistencia_pct: quité el símbolo % en 300 celdas y convertí 202 guiones en
  nulos reales. Después la columna pasó a ser numérica.
- horas_trabajo_semana: convertí 2822 guiones en nulos y la columna a número.
  Los reviso en el paso 8 junto con la columna trabaja.
- distancia_km: convertí 152 valores 999 en nulos, porque 999 es un código de
  "sin dato" y no una distancia real. Ahora tiene 351 nulos (199 + 152).
- Verifiqué que los nulos después de convertir coinciden con los guiones y 999
  contados en la auditoría, así que no se perdió ningún dato válido.

### Paso 4: unificar categorías
**¿Qué variantes son el mismo valor?** Las diferencias de mayúsculas y tildes:
"Psicologia" y "Psicología", "NOCTURNA" y "Nocturna", "bogota" y "Bogotá", etc.
En genero, "M" es Masculino y "F" es Femenino, porque VALIDOS solo admite esos
dos valores.

**¿Hay alguna que no deba unificar?** Sí. "Otra ciudad" no se junta con ninguna
ciudad, porque agrupa ciudades que no están en la lista y no sé sabe cuáles son.
Tampoco convierto los nulos de ciudad en una ciudad: son datos faltantes y los
trato en el paso 7.

**Recomendación:** si el formulario de inscripción usara una lista desplegable
de ciudades en vez de texto libre, estos errores de escritura no existirían.

Resultado: programa quedó con 8 valores (260 celdas corregidas), jornada con 3
(485), genero con 2 (559) y ciudad_procedencia con 7 ciudades (542). Los 103
nulos de ciudad se mantienen para tratarlos en el paso 7.

### Paso 5: fechas
fecha_matricula tenía 3052 fechas en formato DD/MM/AAAA y el resto en
AAAA-MM-DD. Convertí cada formato por separado y los junté con fillna().
Ninguna fecha quedó sin convertir, y el rango va de 2021-01-15 a 2025-09-10.

### Paso 6: duplicados
Eliminé 150 filas duplicadas. Tenían el mismo id_estudiante y todos los datos
iguales, así que eran el mismo estudiante registrado dos veces; si las dejaba,
contarían doble en las tasas. El dataset quedó con 10000 estudiantes y ningún
id repetido.

### Paso 7: faltantes reales
**¿Puedo inventar una nota?** No. Si a un desertor con nota baja le pongo el promedio general, el dato es falso y esconde la relación entre nota y deserción.
Por eso eliminé las filas sin promedio_acumulado; son cerca del 3 % del total.

**¿Eliminar o marcar 'Sin dato' en ciudad y tipo de colegio?** Marcar 'Sin dato'.
Si elimino al estudiante, pierdo su nota, su asistencia y su estado, que sí
sirven para el análisis.

**¿Los nulos de motivo_retiro son errores?** No. Esa columna solo aplica a los desertores; para activos y graduados la pregunta no existe. Los dejo como nulos.

Resultado: eliminé 298 filas sin promedio y quedaron 9702 estudiantes. Marqué
96 ciudades y 145 tipos de colegio como 'Sin dato'. Verifiqué que ningún
desertor quedó sin motivo de retiro y que ningún activo o graduado tiene motivo,
así que los 6562 nulos de motivo_retiro son todos esperados.

### Paso 8: valores imposibles
**¿Qué haría con un promedio de 45?** Convertirlo a la escala correcta. Solo había tres valores fuera de rango (45, 62 y 78), repetidos varias veces, lo que parece un error sistemático de registro en escala 0-100. Al dividirlos entre 20 quedan en 2.25, 3.1 y 3.9, notas dentro del rango normal. Corregí 15 filas.

**¿Qué valor pondría a una edad de 150?** La mediana de las edades válidas (22).
Las 12 edades imposibles eran 12 y 150 años. Usé la mediana y no la media porque no se afecta por valores extremos, y la calculé sin las edades imposibles. Ahora la edad va de 17 a 29 años.

**¿Cuántas horas trabaja quien no trabaja?** Cero. Comprobé que los 2707 nulos
de horas eran todos de estudiantes con trabaja = "no": el guion significaba "no aplica". Además, 29 valores mayores a 100 horas los reemplacé por la mediana de quienes trabajan (24 horas). Ahora las horas van de 0 a 40.

Verifiqué que ningún estudiante con trabaja = "no" quedó con horas mayores a 0.

### Paso 9: variables nuevas
**¿Por qué usar cuartiles y no valores exactos de asistencia?** Porque con
valores exactos habría muchos grupos con pocos estudiantes, y en un grupo
pequeño un solo desertor cambia mucho la tasa. Los cuartiles reparten a todos
los estudiantes en cuatro grupos de tamaño parecido (unos 2400 cada uno), así
que las tasas son más confiables y el patrón se ve más claro.

Resultado: la columna desertor marca 3140 desertores de 9702 estudiantes (tasa
general de 32,4 %). Los cuartiles quedaron con entre 2355 y 2390 estudiantes:
Q1 va de 48 % a 80,5 % de asistencia, Q2 de 80,6 % a 87,8 %, Q3 de 87,9 % a
95 % y Q4 de 95,1 % a 100 %. Los 197 estudiantes sin asistencia no quedan en
ningún cuartil.

## Gráficos

**Mapa de faltantes:** los huecos más visibles están en promedio_acumulado,
distancia_km, ciudad_procedencia y tipo_colegio, y coinciden con los nulos del paso 6.1. motivo_retiro aparece casi vacío porque solo aplica a desertores.
asistencia_pct y horas_trabajo_semana no muestran huecos aunque tenían guiones: el mapa solo ve nulos reales, no faltantes disfrazados.

**Boxplots antes y después:** antes, los promedios de 45, 62 y 78 y las edades de 150 estiraban el eje y aplastaban la caja. Después, el promedio va de 1.17 a 5 y la edad de 17 a 29. Dejé los puntos sueltos que quedan (promedios bajos y
edades de 28 y 29) porque son valores posibles, no errores.

**Tasa por programa:** Ingeniería Industrial tiene la tasa más alta y Psicología la más baja. Ningún programa es tan pequeño como para que su tasa no sea confiable (el más pequeño tiene más de 800 estudiantes).

**Tasa por cuartil de asistencia:** la deserción baja en cada cuartil, de cerca del 62 % en Q1 a cerca del 9 % en Q4.

## 3. Respuestas a las cinco preguntas

### Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
Ingeniería Industrial, con una tasa de 0.403 (40,3 %) sobre 1274 estudiantes.
Le siguen Ingeniería de Sistemas (0.382, 1388 estudiantes) y Diseño Gráfico (0.356, 850 estudiantes). La más baja es Psicología (0.260, 1137 estudiantes).
El programa más pequeño es Diseño Gráfico con 850 estudiantes, un grupo lo
bastante grande para que su tasa sea confiable.

### Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
Sí. Los no becados desertan más (0.364, 7011 estudiantes) que los becados (0.219, 2691 estudiantes): una diferencia de unos 14,5 puntos.
Pero esto no prueba que la beca cause la permanencia. Las becas suelen darse a estudiantes con buen rendimiento, que ya tenían menos riesgo de desertar. La diferencia puede deberse a quién recibe la beca y no a la beca misma.

### Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
La jornada Nocturna, con un promedio de 3.465 (2672 estudiantes). Las otras dos son muy parecidas: Fin de semana con 3.704 (950 estudiantes) y Diurna con 3.724 (6080 estudiantes).

### Pregunta 4: ¿Cuántas materias reprobadas tienen los desertores frente a los activos?
Los desertores tienen en promedio 3.068 materias reprobadas (3140 estudiantes) y los activos 0.622 (5703 estudiantes): casi cinco veces más.
Excluí a los graduados porque no pertenecen a ninguno de los dos grupos que se comparan: ya terminaron la carrera. Si los dejaba, la comparación mezclaría un tercer grupo que no responde la pregunta.

### Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
Sí. La tasa baja en cada cuartil a medida que sube la asistencia:

| Cuartil | Asistencia promedio | Tasa de deserción | Estudiantes |
|---|---|---|---|
| Q1 | 73,9 % | 0.619 | 2386 |
| Q2 | 84,4 % | 0.367 | 2390 |
| Q3 | 91,3 % | 0.208 | 2355 |
| Q4 | 98,7 % | 0.094 | 2374 |

Los estudiantes con menor asistencia desertan unas seis veces más que los de mayor asistencia. Aun así, no es una prueba de causa: la baja asistencia puede ser un síntoma y no la razón. Un estudiante que trabaja muchas horas o tiene
problemas personales puede faltar a clase y también abandonar por esa misma causa. También puede pasar al revés: quien ya decidió retirarse deja de asistir.

## 4. Reflexión: asociación y causalidad
No se puede concluir que la beca cause la permanencia. Los becados desertan
menos (21,9 % frente a 36,4 %), pero para recibir y mantener una beca el
estudiante debe tener buen promedio y buena asistencia, y esas mismas
características ya están asociadas a menos deserción. Es decir, la beca y la
permanencia pueden tener la misma causa: ser un estudiante con buen rendimiento.
Para saber si la beca realmente causa la permanencia habría que comparar
estudiantes con el mismo promedio y la misma asistencia, unos con beca y otros
sin ella. Si aun así los becados desertan menos, habría más evidencia de que la
beca ayuda por sí misma.

## 5. Reflexión: motivo_retiro y la predicción
motivo_retiro no se puede usar para predecir la deserción, porque solo se
registra después de que el estudiante se retira. Lo comprobé en el paso 7:
ningún activo ni graduado tiene motivo, y ningún desertor está sin él. Un modelo
que la use acertaría siempre, pero solo porque el dato ya revela que el
estudiante desertó; para una alerta temprana llegaría demasiado tarde.
Las columnas estado y desertor tienen el mismo problema: son el resultado que
se quiere predecir, no una característica previa del estudiante.

## 6. Reflexión: variables sensibles
Género, estrato y ciudad pueden servir para entender dónde hay desigualdad y
diseñar programas generales, pero no deberían usarse para decidir a qué
estudiante específico se le da apoyo. Una asociación en un grupo no dice nada
seguro de cada persona: usar el estrato excluiría a estudiantes de otros
estratos que sí están en riesgo, y etiquetaría a otros por algo que no
eligieron. Además, si un beneficio depende de un dato declarado por el
estudiante, alguien podría dar información falsa para acceder a él.
Es mejor usar señales de lo que le está pasando al estudiante, como la
asistencia y las materias reprobadas. En este análisis son las más
relacionadas con la deserción: la tasa baja de 61,9 % en Q1 a 9,4 % en Q4, y
los desertores tienen 3,07 materias reprobadas frente a 0,62 de los activos.
Además, las registra la institución, así que son más difíciles de suplantar.
