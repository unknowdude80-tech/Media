# Guía de @yusted.queopina (Instagram)

Esta guía la sigue la tarea semanal que prepara los posts. Si cambias algo aquí, la siguiente corrida lo toma en cuenta.

## Línea editorial

- Cuenta de noticias políticas y económicas de México (más lo internacional que impacte al país).
- **Noticias:** neutrales, sin adjetivos cargados, con fuentes citadas. Cada dato se verifica en al menos 2 fuentes confiables. Si un dato solo aparece en una fuente, se dice en la nota para el dueño y no se presenta como confirmado.
- **Opinión:** solo en posts con la etiqueta ANÁLISIS. Postura de centro-derecha: libre mercado, seguridad, Estado de derecho, contrapesos al poder, instituciones.
- Nunca sacar declaraciones de contexto, ni titulares engañosos, ni ataques personales o burlas.
- Temas de violencia (ataques, víctimas): sin detalles gráficos, nombres de menores, ni imágenes del hecho.
- Trato de "usted". Cada post cierra con una pregunta al público.

## Formato de cada lote semanal

- 3 o 4 posts: al menos 2 de noticias y como máximo 1 de ANÁLISIS.
- **Al menos 1 post de DEBATE por lote:** un tema que divida opiniones de verdad (por ejemplo: reformas, impuestos, seguridad, programas sociales, regulación, relación con EE.UU.) y que provoque comentarios a favor y en contra.
  - Etiqueta `DEBATE` (o `ANÁLISIS` si toma postura).
  - Presenta con honestidad los mejores argumentos de **ambos lados**, con datos verificados, y cierra con una pregunta directa que obligue a tomar posición. Ejemplos: "¿A favor o en contra?", "¿Usted qué haría?", o encuestas tipo "Comente SÍ o NO".
  - La polémica viene del tema, no de trucos: nada de datos falsos o exagerados, titulares engañosos, insultos, burlas a personas o grupos, ni temas que expongan a víctimas.
  - Puede ir en ese mismo post si es el de ANÁLISIS de la semana.
- Carruseles de 4 a 6 diapositivas, 1080x1350.
- **Visual en cada post:** la portada lleva mapa o ícono, y al menos una diapositiva más es gráfica, mapa o cita. Las gráficas solo con cifras reales y con su fuente.
- El caption lleva un resumen breve, la pregunta, las fuentes y 4 a 6 hashtags.
- Recuerda que el plan gratis de Metricool permite 20 publicaciones al mes.

## Cómo se generan las imágenes

1. Escribe un JSON por post en `lotes/AAAA-MM-DD/<slug>.json` (formato en `kit/generar.py`, ejemplo en `kit/ejemplo.json`).
2. Ejecuta `python3 kit/generar.py lotes/AAAA-MM-DD/<slug>.json`. Requiere Playwright y Chromium; las fuentes, íconos y mapa ya vienen en `kit/`.
3. Revisa visualmente cada PNG (que no haya texto cortado ni encimado) antes de subirlo.
4. Haz commit y push a `main`. URL pública: `https://raw.githubusercontent.com/unknowdude80-tech/media/main/lotes/AAAA-MM-DD/<archivo>.png`

## Fotos reales (opcional)

- Solo fotos con licencia libre de Wikimedia Commons (dominio público o CC BY / CC BY-SA). Nunca fotos de agencias o medios (AP, Reuters, Cuartoscuro, periódicos).
- Antes de usar una foto, verifica su licencia y autor en la página del archivo en Commons.
- Se agrega como una diapositiva más pasando la URL directa de `upload.wikimedia.org` en el arreglo `media` de Metricool, en medio del carrusel (nunca como portada, porque la portada fija el formato 4:5).
- El crédito va en el caption, con este formato: `Foto: Autor / Wikimedia Commons, CC BY-SA 4.0`.

## Metricool

- Marca (blogId): `7221480`. Red: Instagram. Zona horaria: America/Mexico_City.
- Todos los posts se crean con `draft: true`. El dueño los revisa y los programa él.
- Horario por defecto: 7:30 pm, un post por día empezando el lunes. Si Metricool ya tiene datos de mejor horario (`getBestTimeToPostByNetwork`), úsalos.
