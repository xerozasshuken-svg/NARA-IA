# NARA IA

NARA IA es un asistente de voz modular, local y pensado para ejecutarse sin conexion.

## Instalacion portable

No copies la carpeta `venv` entre computadoras. Los entornos virtuales guardan rutas absolutas del Python local y suelen fallar cuando se mueven a otro equipo.

En cada dispositivo, copia el proyecto sin depender del `venv` anterior y crea un entorno nuevo.

Windows PowerShell:

```powershell
.\setup.ps1
.\start.ps1
```

Si PowerShell bloquea scripts, usa CMD:

```bat
setup.bat
start.bat
```

Linux o Raspberry Pi:

```bash
bash setup.sh
bash start.sh
```

Si ya tienes todas las dependencias instaladas en el Python del sistema, tambien puedes ejecutar:

```bash
python run.py
```

## Estructura

- `audio/`: captura de microfono y guardado WAV.
- `speech/`: texto a voz, voz a texto y palabra de activacion.
- `brain/`: flujo del asistente, intenciones y respuestas.
- `models/`: modelos locales de Piper y Vosk.
- `utils/`: rutas compartidas y limpieza de archivos generados.
- `data/recordings/`: grabaciones locales generadas durante pruebas y comandos.
- `tests/`: futuras pruebas automatizadas.

## Modelos

Piper espera por defecto:

```text
models/voice.onnx
models/voice.onnx.json
```

Vosk busca automaticamente una carpeta dentro de `models/` cuyo nombre incluya `vosk`, por ejemplo:

```text
models/vosk-model-small-es-0.42/
```

Tambien puedes definir:

```text
NARA_PIPER_MODEL
NARA_PIPER_COMMAND
NARA_VOSK_MODEL
NARA_AUDIO_PLAYER
NARA_WAKE_WORD
```

## Uso

Iniciar el loop de escucha:

```powershell
.\start.ps1
```

O directamente:

```powershell
.\venv\Scripts\python.exe run.py
```

En Linux o Raspberry Pi:

```bash
./venv/bin/python run.py
```

Por defecto NARA escucha hasta detectar silencio, con un maximo de 8 segundos por turno. El modo normal evita avisos hablados largos para empezar a escuchar mas rapido. Para ajustar la sensibilidad:

```powershell
.\venv\Scripts\python.exe run.py --silence-threshold 0.012 --silence-seconds 1.2
```

Para activar avisos hablados extra durante debug:

```powershell
.\venv\Scripts\python.exe run.py --verbose-prompts
```

Para el inicio mas rapido posible:

```powershell
.\venv\Scripts\python.exe run.py --quiet-start
```

Si quieres volver a grabacion fija:

```powershell
.\venv\Scripts\python.exe run.py --fixed-duration --duration 3
```

Para detener el loop por voz, di una frase como:

```text
Nara termina
Nara salir
Nara detente
```

## Pruebas manuales

Texto a voz:

```powershell
.\venv\Scripts\python.exe -c "from speech import speak; speak('Hola, soy NARA.')"
```

Grabar microfono:

```powershell
.\venv\Scripts\python.exe -m audio.recorder --duration 3
```

Grabar microfono hasta detectar silencio:

```powershell
.\venv\Scripts\python.exe -m audio.recorder --silence --duration 8
```

Transcribir con Vosk:

```powershell
.\venv\Scripts\python.exe -m speech.stt --duration 3
```

Transcribir usando corte por silencio:

```powershell
.\venv\Scripts\python.exe -m speech.stt --silence --duration 8
```

## Brain basico

Las respuestas preformuladas viven en:

```text
brain/responses.json
```

Para agregar nuevas preguntas y respuestas:

```json
{
  "id": "ejemplo",
  "patterns": ["frase que puede decir el usuario", "otra variante"],
  "response": "Respuesta que NARA dira por voz."
}
```

Los comandos dinamicos, como hora y fecha, viven en `brain/intents.py`.

## Debug y limpieza

El loop imprime tiempos aproximados por turno:

- escucha/transcripcion
- decision del brain
- sintesis de voz
- tiempo total

Vosk se carga una vez y se reutiliza durante el proceso para reducir latencia. Las grabaciones se guardan en `data/recordings/` y el loop conserva por defecto las 20 mas recientes.

## Cache de voz

NARA usa una cache de audios para respuestas repetidas. No es entrenamiento del modelo: Piper no aprende frases nuevas, solo evita regenerar audios que ya existen.

Los audios se guardan en:

```text
data/tts_cache/
```

Cada frase genera un archivo `.wav` con un hash estable, y `manifest.json` registra texto, ruta, usos y si la ultima reproduccion fue cache hit.

Preparar audios frecuentes:

```powershell
.\venv\Scripts\python.exe run.py --warm-tts-cache
```

Comprobar una frase manualmente:

```powershell
.\venv\Scripts\python.exe -m speech.tts "Hola. Estoy lista para ayudarte." --synthesize-only
```

La primera vez debe mostrar `Cache: MISS`; la segunda vez debe mostrar `Cache: HIT`. Si es `HIT`, NARA reutiliza el audio y evita invocar Piper para esa frase.

Estados principales del flujo por consola:

- `Inicializando`: carga modelos antes de escuchar.
- `Lista`: el sistema ya puede empezar.
- `Escuchando`: el microfono esta capturando voz.
- `Turno terminado`: la captura termino y NARA ya respondio.
