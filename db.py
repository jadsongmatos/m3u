import mimetypes
import os
from tqdm import tqdm
from pathlib import Path
import textdistance
import re

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
                return False

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

# Inserir dados


def find_music(directory):
    print("Listando as músicas neste diretório:", directory)
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    with tqdm(total=total_files) as pbar:
        musicas = []
        for root, _, files in os.walk(directory):
            pbar.update(1)
            for file in files:
                # Obtém o tipo MIME do arquivo
                mime_type, _ = mimetypes.guess_type(file)
                if mime_type.startswith('audio'):
                    try:
                        path = os.path.join(root, file)
                        metadata = read_audio_metadata(path)
                        if metadata:
                            metadata['title'] = clean_string(metadata['title'])
                            metadata['artist'] = clean_string(
                                metadata['artist'])
                            metadata['path'] = path
                            musicas.append(metadata)

                    except Exception as e:
                        print(f"Error processing file {file}: {e}")
        pbar.close()
        return musicas


def clean_string(s):
    """Remove spaces, line breaks, and convert to lowercase."""
    return re.sub(r'\s+', '', s).lower()


def normalized_similarity(s1, s2):
    """Calculate normalized similarity between two strings."""
    # JaroWinkler 0.7
    # DamerauLevenshtein 0.5
    return textdistance.JaroWinkler(external=True).normalized_similarity(s1, s2)


music_directory = '/home/jadson/Músicas/sync/'
musicas = find_music(music_directory)

# Realizar uma pesquisa FTS e obter a relevância (BM25)
duration_search = 140
title_search = 'jailhouse'
artist_search = 'presley'

similarity_max = 0
busca = ""
for musica in musicas:
    duration_similarity = 1 / (1 + abs(duration_search - musica['duration']))
    title_similarity = normalized_similarity(title_search, musica['title'])
    artist_similarity = normalized_similarity(artist_search, musica['artist'])
    average_similarity = (title_similarity*2 +
                          artist_similarity*2 + duration_similarity) / (2+2+1)

    if average_similarity > 0.5:
        print(average_similarity,
              musica['title'], title_similarity, musica['artist'], artist_similarity)

        if average_similarity > similarity_max:
            similarity_max = average_similarity
            busca = musica['title']


print(similarity_max, busca)
