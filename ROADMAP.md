# Hoja de ruta

## Fase 1: Base del proyecto

- Crear la estructura modular inicial de carpetas.
- Definir las responsabilidades de cada módulo.
- Añadir un punto de entrada simple para la aplicación.
- Establecer convenciones básicas de desarrollo y pruebas.

## Fase 2: Canal de audio

- Capturar entrada desde el micrófono.
- Reproducir respuestas de audio generadas.
- Validar compatibilidad con los dispositivos de audio de Raspberry Pi.

## Fase 3: Capa de voz

- Añadir soporte de voz a texto sin conexión con Vosk.
- Añadir soporte de texto a voz sin conexión.
- Evaluar opciones de detección de palabra de activación.

## Fase 4: Cerebro del asistente

- Definir el enrutamiento de intenciones.
- Añadir estado local de conversación.
- Conectar un modelo de lenguaje local ligero o un motor de comandos.

## Fase 5: Despliegue en Raspberry Pi

- Documentar los pasos de instalación.
- Añadir soporte para iniciar el asistente como servicio.
- Optimizar latencia, uso de memoria y fiabilidad.
- Reutilizar modelos cargados, medir tiempos por turno y limpiar grabaciones antiguas.
