from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4


def read_audio_metadata(file_path):
    # Extrair a extensão do arquivo
    ext = Path(file_path).suffix.lower()

    try:
        # Determinar o tipo do arquivo e ler os metadados
        title = ""
        artist = ""
        if ext == '.mp3':
            audio = MP3(file_path)
            title = audio.get('TIT2', 'Desconhecido')[0]
            artist = audio.get('TPE1', 'Desconhecido')[0]
        else:
            if ext == '.flac':
                audio = FLAC(file_path)
            elif ext == '.wma':
                audio = ASF(file_path)
            elif ext == '.ogg':
                audio = OggVorbis(file_path)
            elif ext == '.opus':
                audio = OggOpus(file_path)
            elif ext in ['.m4a', '.mp4']:
                audio = MP4(file_path)
            else:
                return "Formato de arquivo não suportado."
            
            title = audio.get('title', ['Desconhecido'])[0]
            artist = audio.get('artist', ['Desconhecido'])[0]

        duration = audio.info.length      

        return {
            "title": title,
            "artist": artist,
            "duration": duration
        }

    except Exception as e:
        return f"Erro ao ler o arquivo: {e}"


# Exemplo de uso
metadata = read_audio_metadata("03_Pirates_of_the_Caribbean.mp3")
print(metadata)
