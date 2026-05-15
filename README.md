# NARA IA

NARA IA es un proyecto de asistente de voz modular, pensado para funcionar sin conexión y orientado a Raspberry Pi.

## Estructura inicial

- `audio/`: manejo de entrada y salida de audio.
- `speech/`: módulos de voz a texto, texto a voz y palabra de activación.
- `brain/`: razonamiento del asistente, enrutamiento de intenciones y flujo de conversación.
- `models/`: archivos de modelos locales y notas de configuración de modelos.
- `utils/`: utilidades compartidas e infraestructura auxiliar.
- `data/recordings/`: grabaciones locales generadas durante pruebas y comandos.
- `tests/`: pruebas automatizadas para los módulos del proyecto.

## Objetivo

Construir un asistente local capaz de escuchar, comprender, razonar y responder por voz sin depender de una conexión a la nube.

El proyecto empieza intencionalmente con una estructura pequeña para que cada componente pueda reemplazarse o mejorarse de forma independiente.
