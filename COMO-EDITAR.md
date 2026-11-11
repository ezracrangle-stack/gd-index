# Cómo editar The G&D Index (sin programar)

Cada número de Graham & Doddsville es un archivo dentro de la carpeta **data/issues/**. El nombre es año y temporada: `2026-spring.yaml`, `2025-fall.yaml`, `2014-winter.yaml`.

Cuando guardas un cambio en GitHub, el sitio se reconstruye solo. Tarda 2 o 3 minutos en verse en gd.ezrasnotes.com.

## Abrir y guardar un archivo

1. Entra a github.com/ezracrangle-stack/gd-index → carpeta **data** → **issues** → clic en el número que quieres cambiar.
2. Clic en el **lápiz** (Edit this file), arriba a la derecha.
3. Haz tu cambio. Ctrl + F te ayuda a encontrar un nombre.
4. Botón verde **Commit changes** → **Commit changes**.

Reglas de oro:
- Respeta los espacios al principio de cada línea. Usa la barra espaciadora, nunca Tab.
- Los textos van entre comillas `"..."`. Si el texto lleva comillas por dentro, usa comillas simples dentro: `"He calls it 'the moat'."`
- En los resúmenes no uses guiones largos (—). La revisión automática los rechaza.

## Corregir un resumen

Busca la entrevista o el pitch y cambia el texto de la línea `summary:`.

```yaml
    summary: "Eagle's two CIOs on finding ideas through capital flows..."
    summary_status: approved
```

- `summary_status: approved` → el resumen se ve en el sitio.
- `summary_status: draft` → el resumen se oculta. Úsalo si un resumen no te convence y quieres quitarlo mientras lo reescribes.

## Corregir un nombre, una firma o una página

Todo está a la vista en el bloque de cada entrevista:

```yaml
  - type: interview
    page: 18
    investors:
      - {name: Jeff O'Donohue, firm: Starfort Capital Management}
    companies:
      - {name: Cuckoo Holdings}
```

- `page:` es la página del visor del PDF (la que ves en la barra del navegador), no la impresa en la hoja.
- Si cambias el nombre de un inversionista o de una empresa, cámbialo igual en todos los números donde aparece. Si no, el sitio lo trata como dos personas o dos empresas distintas.
- Los pitches tienen `company:`, `direction: long` o `direction: short`, `students:` y `context:` (el concurso y el lugar).

## Las notas "check"

Algunas entradas tienen una línea `check:` con una duda que quedó abierta al leer el PDF. Por ejemplo:

```yaml
    check: "The welcome letter says 'Tonya', the pitch page says 'Tanya'."
```

Estas notas no aparecen en el sitio. Cuando resuelvas la duda, corrige el dato y borra la línea `check:` completa. Hoy hay nueve, en estos archivos:

- `2009-summer`: la firma de Steve Moyer.
- `2014-winter`: la firma de Ken Shubin Stein.
- `2014-spring`: la firma de Kevin Byun.
- `2018-fall`: Scheid o Schein Vineyards.
- `2019-winter`: Tonya o Tanya.
- `2019-spring`: los nombres de los estudiantes del pitch de Dean Foods.
- `2021-fall`: Rachita o Richita.
- `2025-fall`: el número imprime "Advanced Auto Parts".
- `2026-spring`: si el pitch de Celsius tiene un tercer estudiante.

## Cuando sale un número nuevo

El día 1 de cada mes se abre un issue en GitHub: "G&D Index: any new edition this month?". Te llega por correo.

1. Abre el enlace al archivo de Columbia que trae el issue.
2. Si no hay número nuevo, cierra el issue. Listo.
3. Si hay uno nuevo, abre una sesión con Claude y pega este mensaje:

```
Salió un número nuevo de Graham & Doddsville. Indéxalo en The G&D Index
(repo ezracrangle-stack/gd-index) igual que los 50 anteriores:

- Lee el PDF en el navegador integrado desde el archivo de Columbia:
  https://business.columbia.edu/heilbrunn/resources/graham-and-doddsville-newsletter
- Crea el archivo en data/issues/ con status: draft y cada resumen con
  summary_status: draft.
- Páginas = páginas del visor del PDF. Solo nombres de empresas, sin tickers.
  Temas solo de data/topics.yaml. Un resumen de una línea por entrevista y por pitch,
  en inglés y en mi voz, revisado contra mi archivo anti-ai-writing-style.
- El número del ejemplar sale de la carta de bienvenida, no del nombre del archivo.
- Marca con una línea check: cualquier dato dudoso.
- Corre validate.py, sube el archivo y enséñame el borrador antes de publicar.
```

4. Claude sube el número como borrador. Los borradores no se ven en el sitio, así que no pasa nada si tardas en revisarlo.
5. Revisa lo que te enseñe. Cuando estés conforme, publícalo: en el archivo del número cambia `status: draft` por `status: published`, y cada `summary_status: draft` por `summary_status: approved`. También puedes pedirle a Claude que lo haga.

Al publicarse, el número aparece en el home, en las páginas de cada inversionista, empresa y tema, en la búsqueda y en el RSS.

## Si algo sale mal

- Pestaña **Actions**: palomita verde = publicado. Cruz roja = el cambio tiene un error y el sitio en vivo se queda como estaba.
- Si falla, también se abre un issue "the site build failed". Casi siempre es una comilla o un espacio fuera de lugar. Abre la ejecución en Actions, copia el mensaje en rojo y mándamelo, o deshaz tu último cambio.
- Nada se borra solo. Si un PDF de Columbia cambia de dirección, el número sigue en el índice; solo hay que actualizar la línea `pdf:`.
