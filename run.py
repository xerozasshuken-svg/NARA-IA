from audio import record_to_wav
from speech import speak


def main():
    """Entry point for the NARA IA assistant."""
    speak("NARA IA esta lista. Grabare tres segundos de audio.")
    recording_path = record_to_wav(3)
    speak("Grabacion completada.")
    print(f"Audio grabado en: {recording_path}")


if __name__ == "__main__":
    main()
