# POLITI-FUCKER

Pipeline en Python para recolectar, extraer, limpiar y preparar programas de gobierno para análisis político estructurado con NLP.

El proyecto parte de una idea simple: los programas de gobierno suelen publicarse como PDFs heterogéneos, muchas veces mal estructurados, escaneados, llenos de branding de campaña, footers repetidos y ruido visual. Eso hace muy difícil compararlos de forma reproducible y menos aún cuantificar rasgos como coherencia, concreción, plausibilidad o viabilidad.

Este repositorio construye el **primer tramo del pipeline**: pasar de documentos crudos a un **corpus textual limpio y trazable**, listo para análisis posterior.

---

## Objetivo del proyecto

El objetivo no es decir qué candidato es “mejor” o “peor”.

El objetivo es construir una herramienta que permita evaluar **la calidad estructural de un programa de gobierno** con criterios lo más explícitos y auditables posibles.

En su estado conceptual completo, el sistema busca medir al menos estos ejes:

1. **Coherencia interna**
   Que el plan no se contradiga y que exista consistencia entre diagnóstico, propuestas, restricciones y enfoque general.

2. **Definición del problema**
   Qué tan claramente identifica qué problema existe, por qué existe y en qué contexto se formula.

3. **Políticas concretas y objetivos medibles**
   Si hay medidas, instrumentos, metas, responsables, plazos o indicadores.

4. **Seriedad presupuestaria**
   Si el plan sugiere costos, restricciones fiscales, prioridades o mecanismos de financiación.

5. **Viabilidad institucional**
   Si las propuestas se pueden ejecutar dentro del marco estatal, administrativo y legal disponible.

6. **Mecanismos de evaluación**
   Si el programa propone cómo monitorear, medir o corregir la implementación.

7. **Señales de programa fuerte o débil**
   Por ejemplo:
   - lenguaje abstracto excesivo
   - ausencia de números
   - objetivos no medibles
   - contradicciones fiscales
   - plazos irreales

Este repositorio todavía **no implementa todo ese scoring**, pero ya construye la base indispensable para hacerlo bien: **un corpus de texto limpio, reproducible y documentado**.

---

## Estado actual del proyecto

Actualmente el proyecto implementa:

- descubrimiento manual/semiestructurado de fuentes
- descarga de documentos oficiales
- ingestión de PDFs
- extracción de texto con `PyMuPDF`
- fallback a OCR cuando el PDF no contiene texto utilizable
- generación de metadata por documento
- limpieza básica del texto extraído
- almacenamiento ordenado por etapas del pipeline

En otras palabras: hoy el proyecto ya resuelve bien la fase de **document preparation**.

---

## Qué problema resuelve este pipeline

Los programas de gobierno en la práctica traen problemas como:

- PDFs con texto digital normal
- PDFs escaneados
- PDFs con imágenes y sin capa textual
- footers con redes sociales
- branding repetido
- portadas contaminando el texto
- números de página
- URLs, teléfonos y handles
- OCR con artefactos
- líneas rotas por maquetación

Antes de hacer NLP serio, todo eso debe resolverse o al menos controlarse.

Este proyecto lo trata como un problema de pipeline:

```text
fuente → descarga → extracción → OCR fallback → metadata → limpieza → corpus
Estructura del proyecto
politi-fucker/
│
├── data/
│   ├── manifests/
│   │   └── sources.csv
│   ├── raw/
│   │   ├── ivan_cepeda/
│   │   ├── claudia_lopez/
│   │   ├── sergio_fajardo/
│   │   └── ...
│   ├── processed/
│   │   ├── programa_gobierno_cepeda.txt
│   │   ├── programa_gobierno_cepeda.meta.json
│   │   ├── programa_gobierno_claudia_lopez.txt
│   │   ├── programa_gobierno_claudia_lopez.meta.json
│   │   └── ...
│   └── cleaned/
│       ├── programa_gobierno_cepeda.clean.txt
│       ├── programa_gobierno_claudia_lopez.clean.txt
│       └── ...
│
├── public/
│
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ocr_utils.py
│   │   └── utils.py
│   ├── candidate_registry.py
│   ├── config.py
│   ├── downloader.py
│   ├── ingestion.py
│   ├── pdf_text_extractor.py
│   ├── source_discovery.py
│   └── text_processing.py
│
├── app.py
├── requirements.txt
└── README.md

```

---

Arquitectura del pipeline

0.  Corpus validation

    Antes de analizar nada, el proyecto distingue entre:

    documentos oficiales completos

    páginas de propuestas

    fragmentos de campaña

    materiales incompletos o no comparables

    La lógica metodológica es simple: no toda fuente oficial es una unidad analítica válida.

    Un homepage de campaña puede ser oficial, pero no necesariamente sirve para análisis programático.

1.  Source discovery

    Archivo principal:

    src/source_discovery.py

    Su función es construir el manifest inicial de fuentes a partir de candidatos y documentos identificados manualmente o semiautomáticamente.

    El archivo sources.csv contiene la metadata documental base, por ejemplo:

        - candidate_id
        - candidate_name
        - bloc
        - country
        - election_year
        - source_priority
        - source_type
        - document_level
        - document_type
        - access_method
        - title
        - url
        - file_type
        - local_filename
        - is_official
        - status
        - notes

    ## Lógica de source_priority

    A: documento programático completo y comparable

    B: página programática o documento parcial

    C: material fragmentario o aún no localizado

2.  Downloader

    Archivo principal:

    src/downloader.py

    Lee sources.csv, descarga los documentos y los almacena en data/raw/.

    Características principales:

    usa nombres locales controlados (local_filename)

    evita depender del nombre de la URL

    permite trabajar con fuentes directas y Google Drive

    deja trazabilidad por candidato

    Salida esperada:

    data/raw/sergio_fajardo/programa_gobierno_fajardo.pdf
    data/raw/claudia_lopez/programa_gobierno_claudia_lopez.pdf
    data/raw/ivan_cepeda/programa_gobierno_cepeda.pdf

3.  Ingestion

    Archivo principal:

    src/ingestion.py

    La ingestión no significa todavía “analizar políticas”.
    Aquí ingestion significa:

    convertir documentos fuente en texto y metadata estructurada.

    Qué hace ingestion.py

    recorre todos los PDFs de data/raw

    intenta extraer texto con PyMuPDF

    evalúa si el resultado es suficiente

    si falla, activa OCR como fallback

    guarda:

    .txt

    .meta.json

    Salida esperada:

    data/processed/programa_gobierno_fajardo.txt
    data/processed/programa_gobierno_fajardo.meta.json

4.  Text extraction

    Archivo principal:

    src/pdf_text_extractor.py

    Este módulo maneja la extracción “normal” de texto desde PDFs digitales usando PyMuPDF.

    Devuelve:

    texto completo

    número de páginas

    caracteres

    número de palabras

    conteo de caracteres por página

    páginas vacías

    método de extracción usado

5.  OCR fallback

    Archivo principal:

    src/utils/ocr_utils.py

    Cuando un PDF no contiene texto usable, el pipeline lo detecta y pasa al carril OCR.

    Cuándo se activa

    Actualmente, si por ejemplo:

    text_chars == 0

    hay demasiadas páginas vacías

    el resultado de extracción es anormalmente pobre

    Entonces el documento queda marcado como:

        "status": "needs_ocr",
        "needs_ocr": true

    y el sistema intenta OCR.

    OCR actual

    render de página a imagen con PyMuPDF

    OCR con pytesseract

    metadata que registra:

    extraction_method: "ocr"

    fallback_used: true

    status: "ok_after_ocr"

    Esto permitió rescatar, por ejemplo, documentos como el de Claudia López, que no tenían capa textual utilizable pero sí pudieron recuperarse con OCR.

6.  Metadata generation

    Cada documento procesado genera un .meta.json.

    Ejemplo real simplificado:

    {
    "source_file": "programa_gobierno_claudia_lopez.pdf",
    "pages": 35,
    "text_chars": 80330,
    "word_count": 11864,
    "page_char_counts": [67, 1821, 1089, 3108],
    "empty_pages": 0,
    "extraction_method": "ocr",
    "fallback_used": true,
    "status": "ok_after_ocr",
    "needs_ocr": false,
    "ocr_language": "default"
    }
    Distinción importante

    Hay dos tipos de metadata en el proyecto:

    A. Metadata documental

        Guardada en sources.csv.
        Describe qué documento es.

    B. Metadata de extracción

        Guardada en .meta.json.
        Describe cómo salió la extracción.

    Esta separación permite trazabilidad y depuración mucho más claras.

7.  Text processing

    Archivo principal:

    src/text_processing.py

    Toma los .txt crudos de data/processed y produce versiones limpias en data/cleaned.

    Qué limpia?
    - saltos de línea inconsistentes
    - artefactos OCR frecuentes
    - URLs
    - dominios web
    - handles de redes sociales
    - teléfonos
    - espacios múltiples
    - footers de campaña
    - branding repetido
    - líneas ruidosas con símbolos
    - líneas cortas irrelevantes
    - líneas en blanco repetidas

    Salida esperada
    data/cleaned/programa_gobierno_claudia_lopez.clean.txt
    data/cleaned/programa_gobierno_fajardo.clean.txt

    Importante:

    La limpieza actual es heurística y progresiva.
    No pretende “arreglar todo el OCR”, sino dejar el texto lo suficientemente usable para pasos posteriores.

---

Flujo de ejecución

1. Generar el manifest de fuentes
   python src/source_discovery.py

Esto crea:

data/manifests/sources.csv

2. Descargar los documentos
   python src/downloader.py

Esto descarga los PDFs en data/raw/.

3. Ejecutar la ingestión
   python src/ingestion.py

Esto genera:

texto crudo en data/processed

metadata de extracción en data/processed

4. Ejecutar la limpieza
   python src/text_processing.py

Esto genera:

texto limpio en data/cleaned

Instalación
Requisitos Python

Instala dependencias desde:

pip install -r requirements.txt
Dependencias principales

    requests

    pymupdf

    pytesseract

    pillow

    Requisito extra para OCR

    Además de la librería Python, OCR necesita Tesseract OCR instalado en el sistema.

    Windows

    Instala Tesseract y asegúrate de que exista algo como:

    C:\Program Files\Tesseract-OCR\tesseract.exe

    Si quieres OCR en español, también necesitas el archivo de idioma:

    spa.traineddata

    dentro de:

    C:\Program Files\Tesseract-OCR\tessdata\
    Si falta el idioma español

El pipeline puede usar fallback por defecto, pero la calidad será peor.

Ejemplo de problema real que el pipeline ya resuelve
Caso 1: PDF textual normal

Sergio Fajardo

extracción con PyMuPDF

texto limpio

sin necesidad de OCR

Caso 2: PDF sin capa textual utilizable

Claudia López

extracción textual inicial falló

activación de OCR

recuperación exitosa del documento

limpieza posterior para remover branding y ruido visual

Esto demuestra que el pipeline ya maneja dos carriles de ingestión:

text-native

ocr-recovered

---

Decisiones metodológicas importantes

1. Primero PDFs, no páginas web

   La estrategia principal de recolección está orientada a PDFs programáticos, no a páginas HTML de campaña.

   Razón:
   los PDFs suelen ser el documento base real
   son más completos
   son más estables
   son más comparables
   son más procesables para NLP

2. No toda fuente oficial entra al análisis principal

   Se distingue entre:

   program
   policy_page
   fragment
   missing

   y más adelante conviene agregar cosas como:

   analysis_eligibility: core / secondary / exclude

   para no comparar injustamente un programa completo contra una landing page.

3. OCR es fallback, no camino principal

   OCR se usa solo cuando hace falta.

   Razón:

   es más lento

   es más ruidoso

   mete errores ortográficos

   requiere limpieza adicional

4. El proyecto no busca ranking ideológico

   No se quiere producir una respuesta del tipo:

   “este candidato es mejor que este otro”

   Se quiere evaluar rasgos estructurales del documento programático.

   Estado actual del pipeline
   Ya implementado

   registro de candidaturas

   source manifest

   descarga de PDFs

   nombres de archivo controlados

   extracción textual con PyMuPDF

   OCR fallback con Tesseract

   generación de metadata

   limpieza de texto

   separación por etapas (raw, processed, cleaned)

   Pendiente

   parser de secciones/capítulos

   segmentación por políticas

   detección de dominios temáticos

   extracción de medidas concretas

   scoring de coherencia

   scoring de concreción

   scoring de plausibilidad

   radar final tipo FIFA

   visualización comparativa

-\*-
Próximos módulos sugeridos

1.  section_parser.py

    Detectar estructuras como:

        capítulo

        acuerdo

        propuesta

        tema

        subsección

    y pasar de texto plano a estructura JSON.

2.  policy_extractor.py

    Extraer bloques de política pública.

3.  scoring_engine.py

    Aplicar reglas cuantitativas por eje.

4.  visualization.py

    Construir el output tipo radar/telaraña.

    Limitaciones actuales

    la limpieza OCR todavía es heurística

    algunos artefactos de portada o branding pueden sobrevivir

    todavía no hay segmentación estructural automática

    el corpus aún depende parcialmente de curaduría manual de fuentes

    la extracción no corrige ortografía OCR de forma semántica

    Estas limitaciones son esperables en esta fase.

    Cómo leer este repositorio

    Este proyecto está pensado como una mezcla de:

    pipeline reproducible

    herramienta práctica

    base para un sistema mayor de análisis político

    La lógica general es:

    base de investigación por dentro, salida práctica por fuera

    Es decir:

    método claro

    trazabilidad documental

    limpieza reproducible

    posibilidad futura de visualización accesible

    Uso esperado a futuro

    Este pipeline puede escalarse a:

    elecciones presidenciales en otros países

    programas legislativos

    planes de desarrollo

    manifiestos partidarios

    comparaciones longitudinales entre ciclos electorales
