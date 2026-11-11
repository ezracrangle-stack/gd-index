# Cómo publicar The G&D Index en gd.ezrasnotes.com

Son los mismos pasos que hiciste para letters.ezrasnotes.com. Calcula unos 20 minutos, más la espera del DNS.

## 1. Crea el repositorio vacío

1. Entra a GitHub con tu cuenta **ezracrangle-stack**.
2. Arriba a la derecha: **+** → **New repository**.
3. Repository name: `gd-index`
4. Elige **Public**. GitHub Pages gratis necesita repositorio público.
5. **No** marques "Add a README", ni .gitignore, ni licencia. Tiene que quedar vacío.
6. **Create repository**.

## 2. Sube los archivos

Tienes dos caminos:

**A. Lo subo yo (recomendado).** Dime "ya está creado" en la conversación con Claude. Conecto el repositorio con permiso de escritura y subo todo de una vez, con la carpeta oculta `.github`, que es la que lleva el proceso semanal.

**B. A mano.** En la página del repositorio vacío, haz clic en **uploading an existing file**. Descomprime `gd-index.zip` y arrastra **todo su contenido**, no la carpeta que lo contiene. Revisa que entre la carpeta `.github`: en Mac, las carpetas que empiezan con punto están ocultas (Cmd+Shift+. las muestra). Abajo, **Commit changes**.

## 3. Da permiso de escritura al proceso semanal

1. En el repositorio: **Settings** → **Actions** → **General**.
2. Baja a **Workflow permissions** y elige **Read and write permissions**.
3. **Save**.

Sin esto, el proceso no puede guardar resultados ni abrirte issues.

## 4. Activa GitHub Pages

1. **Settings** → **Pages**.
2. En **Build and deployment** → **Source**, elige **Deploy from a branch**.
3. En **Branch**, elige `main` y la carpeta `/docs`. **Save**.
4. En **Custom domain**, escribe `gd.ezrasnotes.com` y **Save**.

## 5. Configura el subdominio en GoDaddy

1. Entra a GoDaddy → **My Products** → junto a ezrasnotes.com, **DNS**.
2. **Add New Record**:
   - Type: **CNAME**
   - Name: `gd`
   - Value: `ezracrangle-stack.github.io`
   - TTL: el que venga por defecto
3. **Save**.

Es igual al registro `letters` que ya tienes; solo cambia el nombre.

## 6. Espera el DNS y activa HTTPS

1. Vuelve a **Settings** → **Pages**. Cuando el DNS esté listo verás "DNS check successful". Puede tardar de minutos a unas horas.
2. Marca **Enforce HTTPS**. Si la casilla aparece gris, espera un poco más; GitHub está emitiendo el certificado.
3. Abre https://gd.ezrasnotes.com.

## 7. Corre la revisión semanal una vez a mano

1. **Actions** → a la izquierda, **Weekly G&D check** → **Run workflow** → **Run workflow**.
2. Espera unos 2 minutos.
   - Palomita verde y ningún issue nuevo: todo bien. Desde aquí corre solo cada lunes a las 7:41 am.
   - Si se abre un issue que dice que no pudo leer la página de Columbia, probablemente Cloudflare bloquea a GitHub. Avísame y vemos otra salida. No se borra nada.

## 8. Asegúrate de recibir los avisos por correo

Arriba en el repositorio, botón **Watch** → **All Activity**. Así cada issue del proceso (número nuevo o problema) te llega por correo.

## 9. Google Analytics

1. En Google Analytics, en tu propiedad, ve a **Admin** → **Data streams** → **Add stream** → **Web**.
2. URL: `https://gd.ezrasnotes.com`. Nombre: `G&D Index`.
3. Copia el **Measurement ID** (empieza con `G-`).
4. En GitHub, abre `site.yaml` → ícono de lápiz → en la línea `ga_id: ""` pega el ID entre las comillas → **Commit changes**.

El proceso reconstruye el sitio solo en un par de minutos.

Search Console: si ezrasnotes.com está dada de alta como propiedad de dominio, el subdominio gd ya queda cubierto. Si la diste de alta como prefijo de URL, agrega `https://gd.ezrasnotes.com` como propiedad nueva.
