# Alfred Assistant — contexto para desarrollo

Asistente personal doméstico en Python, con interfaz web. Es un proyecto personal: se construye para un uso real en casa y se mantiene simple. Si alguien más lo usa, se adapta a lo que hay.

> Este documento resume las decisiones ya tomadas. Lo marcado como **propuesta** está sin confirmar. Lo marcado como **diferido** no se construye ahora.

## 1. Idea y principios

- **Todo va por la webapp**, desde el móvil o desde el ordenador. Un solo Alfred, un solo servidor, una sola interfaz. No hay agentes ni programas en otros equipos.
- **Núcleo pequeño y estable; minijobs enchufables.** Cada minijob es un módulo independiente que se añade sin tocar el núcleo.
- **Un minijob solo habla con el núcleo.** Nunca con otro minijob. Si hay que encadenar dos, lo orquesta el núcleo.
- **El minijob produce; el núcleo decide qué se hace con el resultado.**
- **Interfaz tonta.** La validación y las decisiones viven en el núcleo y en los minijobs, no en las pantallas. Así se puede añadir un chat en el futuro.
- **Instalación directa en el sistema** (sin contenedores), con entorno virtual de Python y comprobación de requisitos al arrancar.
- **Licencia GPL-3.0**, con aviso de autoría visible (pie de página y pantalla "Acerca de" del núcleo, texto fijo en `NOTICE`).
- **Nombre del repositorio y del software:** Alfred Assistant.

## 2. Arquitectura en una vista

```
Móvil / ordenador (navegador) ──► Servidor Alfred (Linux, siempre encendido)
                                   webapp + núcleo + minijobs
```

- Alfred corre siempre en el servidor de casa. Los ficheros se **suben** desde el navegador y los resultados se **descargan**.
- El acceso desde fuera de casa va por VPN doméstica (WireGuard o Tailscale), sin exponer Alfred a internet.

## 3. Contrato mínimo del minijob

Cada minijob declara (manifiesto):

- **Identidad:** identificador estable, nombre, descripción, categoría y versión.
- **Dependencias externas:** por conversión o capacidad. El núcleo ofrece solo lo que tenga las dependencias cumplidas.
- **Entradas declarativas:** campos, tipos, obligatorios y valores por defecto. De ahí se genera el formulario.
- **Peso:** ligero o pesado (para limitar concurrencia) y tiempo máximo.
- **Política de conservación** de sus resultados (con tiempos o sin ellos).

Cada minijob cumple:

- Recibe entradas validadas y devuelve un **informe**: resultados, resumen legible y fallos parciales.
- **Informa de progreso** al núcleo y es **cancelable** (limpia lo que deje a medias).
- Errores en dos niveles: mensaje claro para el usuario y detalle técnico para el log.
- No conoce usuarios ni cómo se entregan sus resultados.
- Escribe temporales solo en la carpeta aislada que le asigna el núcleo.

## 4. Ciclo de vida de un trabajo

Estados: `pendiente → en curso → terminado | terminado con avisos | fallido | interrumpido | cancelado` (con `cancelándose` como paso intermedio).

- **Solo el núcleo cambia estados.**
- Los trabajos se ejecutan **en procesos aparte**, lanzados y vigilados por el núcleo, para no bloquear ni tumbar la webapp. Sin sistema de colas externo.
- Cada trabajo tiene **su carpeta temporal aislada**.
- Cancelar: se pide parar, el minijob limpia; si no responde, el núcleo lo corta y limpia él.
- Tras un reinicio, los trabajos que estaban en curso pasan a **interrumpido** y se pueden reintentar (en lotes, solo los ficheros fallidos).
- El estado de los trabajos y la cola se guardan de forma **persistente**.
- El **historial de trabajos se conserva indefinidamente**; lo que caduca son los ficheros resultantes, según la política del minijob.

## 5. Primer minijob: `conversor_medios` (v1)

Versión 1 acotada a **HEIC → JPG**, por subida de ficheros.

- **Entrada:** desde la webapp, un selector de ficheros (varios a la vez, o una carpeta entera) donde se adjunta todo lo que se necesite convertir.
- **Catálogo de conversiones:** cada conversión declara entradas, salidas, opciones y dependencias. Añadir mp3, mp4, mkv, etc. es añadir entradas al catálogo. Los documentos (docx, pdf) irían en un minijob aparte, `conversor_documentos`.
- **Opciones:** calidad, conservar metadatos, GPS aparte, redimensionar, y qué hacer si el nombre ya existe (por defecto, numerar).
- **Informe:** convertidos, omitidos y fallidos; un fichero corrupto no detiene el lote.
- **Salida:** descarga de los ficheros convertidos (individualmente o en un único comprimido).
- **Conservación:** los resultados caducan a las 48 horas y el núcleo los limpia.

## 6. Qué entra ahora y qué queda diferido

**Ahora (alcance real):**

1. Núcleo pequeño: página de inicio con catálogo, registro de minijobs, ejecución de trabajos en segundo plano con progreso y cancelación, zona temporal con limpieza y registro de actividad.
2. Un único usuario administrador.
3. Conversor HEIC → JPG por subida de ficheros y descarga.

**Diferido** (el diseño lo permite, no se construye hasta necesitarlo): varios usuarios con permisos, carpetas del servidor como origen y destino de ficheros, almacenes y reglas automáticas con etiquetas, conectores de nube (Google Drive, OneDrive, iCloud), API para automatizaciones, chat en lenguaje natural, actualizaciones asistidas con migraciones, aviso de versión nueva, downloader de vídeos (segundo minijob).

## 7. Estructura propuesta del repositorio (`alfred-assistant`)

```
alfred-assistant/
├── README.md              qué es, requisitos, instalación, soporte
├── LICENSE                GPL-3.0
├── NOTICE                 aviso de autoría visible (texto fijo)
├── CHANGELOG.md
├── pyproject.toml         dependencias de Python y metadatos
├── .gitignore             config real, datos, subidas, credenciales
├── config.ejemplo/
│   └── servidor.ejemplo.toml
├── docs/
│   ├── contexto.md        este documento
│   └── contrato-minijob.md
├── alfred/
│   ├── comun/             contrato del minijob y utilidades compartidas
│   ├── nucleo/            servidor (ver sección 8)
│   └── minijobs/
│       └── conversor_medios/
│           ├── manifiesto.*     identidad, entradas, dependencias
│           ├── catalogo/        una entrada por conversión (heic_a_jpg, …)
│           └── ejecutar.*       lógica del minijob
├── minijobs_personales/   ignorada por git; minijobs propios sin tocar el proyecto
├── scripts/               instalación y arranque en Linux
└── tests/
```

Regla de dependencias: un minijob solo depende de `alfred/comun` y del contrato; nunca de otro minijob ni de los detalles internos del núcleo.

## 8. Estructura propuesta del núcleo del servidor (`alfred/nucleo/`)

```
nucleo/
├── arranque/              inicio de la app y comprobación de requisitos
├── puerta/                punto único de entrada de todas las acciones
├── web/
│   ├── plantillas/        shell: navegación, catálogo, formularios generados
│   ├── estaticos/
│   └── acerca_de          pie de página y pantalla con el aviso de autoría
├── minijobs/              registro: descubre, valida y activa los minijobs
├── trabajos/
│   ├── estados            ciclo de vida y transiciones
│   ├── cola               orden, límites de concurrencia, persistencia
│   ├── lanzador           procesos de trabajo aparte, vigilancia y cancelación
│   └── recuperacion       marca interrumpidos tras un reinicio
├── zona_temporal/         subidas y resultados; carpeta aislada por trabajo y limpieza por caducidad
├── actividad/             registro de acciones y errores
├── datos/                 modelos y persistencia (trabajos, ajustes)
└── config/                lectura y validación de la configuración
```

Cuando se necesiten carpetas del servidor, usuarios o reglas, se añaden como carpetas nuevas del núcleo (`ubicaciones/`, `usuarios/`, `reglas/`) sin reorganizar lo existente.

## 9. Propuestas técnicas a confirmar

Pendientes de decidir en el chat de código (la estructura anterior no depende de ellas):

- **Python:** una versión reciente y estable como mínima.
- **Framework web** del servidor y cómo se construye el formulario a partir del manifiesto.
- **Persistencia:** una base de datos embebida simple, suficiente para uso doméstico.
- **Subidas grandes:** tamaño máximo por fichero y por lote, y cómo se configuran los límites del servidor web para lotes de muchas fotos.
- **Mecanismo de procesos de trabajo** y de cancelación en Linux.
- **Soporte HEIC** en Python: qué librería usar.

## 10. Orden de construcción sugerido

1. **Cimientos:** repositorio con esta estructura, licencia, `NOTICE`, README, configuración de ejemplo y comprobación de requisitos. Criterio: un clon nuevo arranca y muestra un catálogo vacío.
2. **Núcleo mínimo:** registro de minijobs, trabajos en procesos aparte con estados, progreso y cancelación, zona temporal, registro de actividad.
3. **Conversor v1:** HEIC → JPG con selector de ficheros en la webapp, formulario generado, progreso, fallos parciales y descarga.

Cada paso debe terminar con algo que se use de verdad, no solo con pruebas.
