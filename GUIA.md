# Guía de @yusted.queopina (Instagram)

Esta guía la sigue la tarea semanal que prepara los posts. Si cambias algo aquí, la siguiente corrida lo toma en cuenta.

## Logo

- Logo oficial: monograma ¿Y? (`logo/perfil.png`, `logo/portada_facebook.png`). El pie de cada diapositiva ya lo usa.

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

## Portadas y cuadrícula del perfil

Las portadas son lo único que se ve en el perfil, así que deben distinguirse entre sí y leerse en miniatura.

- Cada post lleva `"seccion"` en su JSON, que define el color de la portada y del cierre:
  - `politica`: azul
  - `economia`: crema
  - `debate`: dorado
  - `analisis`: negro
- No pongas dos portadas seguidas del mismo color. Al ordenar las fechas del lote, alterna secciones.
- Portada = **una sola idea**: un número gigante (`cifra`, por ejemplo "70%" o "−3.6%") o un título corto de 4 a 8 palabras, más un ícono, mapa o foto. Sin subtítulo largo.
- Si la portada usa `cifra`, la diapositiva 2 no repite ese número: da el siguiente dato.
- La portada no lleva pie con logo: el perfil ya lo muestra y ahí Instagram encima sus contadores.
- No uses colores asociados a partidos (guinda, rojo, verde, naranja) como color de sección.

## Cómo se generan las imágenes

1. Escribe un JSON por post en `lotes/AAAA-MM-DD/<slug>.json` (formato en `kit/generar.py`, ejemplo en `kit/ejemplo.json`).
2. Ejecuta `python3 kit/generar.py lotes/AAAA-MM-DD/<slug>.json`. Requiere Playwright y Chromium; las fuentes, íconos y mapa ya vienen en `kit/`.
3. Revisa visualmente cada PNG (que no haya texto cortado ni encimado) antes de subirlo.
4. Haz commit y push a `main`. URL pública: `https://raw.githubusercontent.com/unknowdude80-tech/media/main/lotes/AAAA-MM-DD/<archivo>.png`

## Fotos

- Las fotos viven en `fotos/` y cada una tiene su línea en `fotos/CREDITOS.md` (qué muestra, crédito y fuente). Si una foto no está en esa tabla, no se usa.
- Solo fotos propias del dueño, de gob.mx (Términos de Libre Uso MX) o de Wikimedia Commons con licencia libre. Nunca fotos de periódicos ni agencias, aunque se estilicen.
- Siempre se estilizan con la marca, usando la diapositiva tipo `foto` (estilos: `duotono` por defecto, `poster`, `grabado`). Con personas reales se usa `duotono` o `grabado`; nada de caricaturas.
- El crédito aparece sobre la foto y también en el caption.
- Usa una foto solo cuando venga al caso de la nota (lugar, persona o institución de la que se habla). No la fuerces.

## Publicación con TARDIS (reemplaza a Metricool)

- Marca: `9fff447b-1aec-438a-b549-3d9246534e0d` (zona America/Monterrey, modo revisión).
- Cuentas: Instagram `36c3883d-84f7-4f02-900e-05f3dc9f3f32` y Facebook `763c6a10-a3d8-42bb-bbfe-2b02b0bbc129`. Cada post va a las dos.
- Crea con `create_post_for_review`. Todo queda **"Por revisar"** hasta que el dueño lo apruebe: nunca le digas que ya está programado o publicado.
- **Imágenes:** solo JPEG (Instagram rechaza PNG), máximo 8 MB, proporción entre 4:5 y 1.91:1, carruseles de 2 a 10. El generador ya exporta JPEG 1080x1350.
- **URLs:** solo `https://raw.githubusercontent.com/unknowdude80-tech/media/<hash del commit>/lotes/...jpg`, con el hash del commit (no `main`) para evitar caché. Nunca `github.com/.../blob/...`. Antes de crear el post, verifica que cada URL responda 200.
- Para reutilizar una misma imagen en varios posts, súbela una vez con `upload_media_from_url` y usa el id que devuelve.
- **client_request_id** único y estable: `semana-AAAA-SS-post-N` para el lote semanal y `diario-AAAA-MM-DD` para el resumen matutino. Repetirlo con el mismo contenido devuelve el mismo post. Si cambias el contenido de un post tuyo que siga por revisar, usa `update_post`.
- Si una creación devuelve error, revisa primero con `get_scheduled_posts` si el post ya existe antes de reintentar. Si TARDIS lista problemas de la media, corrígelos y vuelve a intentar; nunca reportes como creado algo que falló.
- Límites por token: 20 descargas de media por hora, 10 posts por cuenta en 24 h, 30 posts por revisar por marca y 50 creaciones al día por marca.
- Solo puedes modificar o cancelar posts creados por ti que el dueño no haya editado ni aprobado.
- Caption: máximo 2,200 caracteres, 30 hashtags y 20 menciones.
- Horario del lote semanal: un post por día a las 7:30 pm (hora de Monterrey), de lunes a jueves.

## Vigencia de las noticias

- El lote semanal se arma el domingo para lunes a jueves. Pon primero los temas que más rápido pueden cambiar (casos en curso, renuncias, votaciones pendientes) y al final los que no caducan (datos, explicaciones, debates de fondo).
- Evita en el lote semanal noticias que muy probablemente cambien en horas; esas van en el resumen matutino.

## Resumen matutino "Las 5 de hoy" (lunes a viernes)

- Lo prepara una tarea a las 6 am y se publica a las **8:00 am** (hora de Monterrey), en Instagram y Facebook.
- **Se crea con `create_scheduled_post`, no "Por revisar":** el dueño pidió que este post se publique solo. (Si la marca sigue en modo revisión, TARDIS lo deja pendiente igual; en ese caso díselo al dueño.)
- `"seccion": "resumen"`. Diapositivas: 1 portada tipo `resumen` (fecha y 5 titulares de 3 a 7 palabras), 5 diapositivas tipo `nota` (número, tag del tema, titular, 2 o 3 líneas, fuente) y un `cierre` que pida elegir un número ("¿Cuál le preocupa más? Díganos el número").
- Noticias del día anterior y de la madrugada, de México (política, economía, seguridad) más lo internacional que impacte al país. Mezcla de temas: no las 5 de lo mismo.
- **Como se publica sin revisión humana, las reglas son más estrictas:**
  - Solo hechos confirmados en al menos 2 fuentes confiables. Si algo no se puede confirmar, no entra.
  - Cero opinión: nada de ANÁLISIS ni DEBATE en el resumen.
  - Personas señaladas: solo lo que dicen fuentes oficiales o la investigación, con "presunto" cuando aplique. Nada de acusaciones de redes sociales.
  - Sin violencia gráfica, víctimas identificables ni menores.
  - Si hay duda razonable sobre alguna nota, cámbiala por otra. Si no logras 5 notas sólidas, usa `create_post_for_review` en lugar de publicar directo y avisa al dueño.
- client_request_id: `diario-AAAA-MM-DD`.
- La misma tarea revisa el post de las 7:30 pm de ese día: si una noticia cambió (renuncia, votación, fallo), y el post sigue sin aprobar y fue creado por ti, corrígelo con `update_post`; si ya está aprobado, avisa al dueño qué cambió.
