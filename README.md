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

Transcribir con Vosk:

```powershell
.\venv\Scripts\python.exe -m speech.stt --duration 3
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
