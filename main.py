import os
import re
from pathlib import Path
import urllib.parse
from tqdm import tqdm
import textdistance
import mimetypes

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4

# audio = MP3('./01_Animals.mp3')
# print(audio.pprint())
# titulo = audio.get('TIT2')[0].replace(" ", "").replace('\n', "").lower()
# artist = audio.get('TPE2')[0].replace(" ", "").replace('\n', "").lower()
# tempo = int(audio.info.length)
# print(artist, titulo, tempo)

def normalized_similarity(s1, s2):
    """Calculate normalized similarity between two strings."""
    return textdistance.DamerauLevenshtein(external=True).normalized_similarity(s1, s2)

def clean_string(s):
    """Remove spaces, line breaks, and convert to lowercase."""
    return re.sub(r'\s+', '', s).lower()


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

def parse_playlist_line(line):
    """Parse a line from the playlist to extract duration, artist, and title."""
    try:
        time, title_artist = line.split(",", 1)
        title_artist = urllib.parse.unquote(title_artist)
        print('\n',title_artist)
        duration = int(time.split(":")[1])
        if duration > 100000: # Adjust duration unit if needed
                print("Corrigindo a duração da musica",title_artist,duration)
                duration = int(duration / 1000)
                
        artist, title = title_artist.split("-", 1)
        return duration, clean_string(artist), clean_string(title)
    except ValueError:
        print("Error parsing line:", line)
        return None

def find_music(directory, title_search, artist_search, duration_search):
    """Find music file in the directory that matches the given criteria."""
    for root, _, files in os.walk(directory):
        for file in files:
            # Obtém o tipo MIME do arquivo
            mime_type, _ = mimetypes.guess_type(file)
            if mime_type.startswith('audio'):
                try:
                    path = os.path.join(root, file)
                    metadata = read_audio_metadata(path)
                    if metadata:
                        duration_similarity = 1 / (1 + abs(duration_search - metadata['duration']))

                        title = clean_string(metadata['title'])
                        title_similarity = normalized_similarity(title, title_search)

                        artist = clean_string(metadata['artist'])
                        artist_similarity = normalized_similarity(artist, artist_search)

                        average_similarity = (title_similarity + artist_similarity + duration_similarity) / 3

                        if average_similarity > 0.8:
                            return path
                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    return None

def update_line(line, new_path, output_directory):
    """Update a specific line in the playlist with the new path."""
    url_new_path = urllib.parse.quote(str(new_path))
    url_output_path = urllib.parse.quote(new_path.replace(music_directory, output_directory))
    url_file_name = urllib.parse.quote(Path(new_path).name)
    return f"{line}{url_output_path}\n{url_new_path}\n{url_file_name}\n"


def update_playlist(playlist_path, music_directory, output_directory):
    """Update playlist with new paths for music files."""
    try:
        with open(playlist_path, 'r') as file:
            lines = file.readlines()
    except IOError as e:
        print(f"Error opening playlist: {e}")
        return

    for i, line in tqdm(enumerate(lines), total=len(lines)):
        if line.startswith('#EXTINF:'):
            parsed_line = parse_playlist_line(line)
            if parsed_line:
                duration, artist, title = parsed_line
                new_path = find_music(music_directory, title, artist, duration)
                if new_path:
                    print(artist,title,new_path)
                    lines[i] = update_line(lines[i] , new_path, output_directory)

    """New file."""
    path_obj = Path(playlist_path)
    try:
        with open(f"{path_obj.stem}_updated{path_obj.suffix}", 'w') as file:
            file.writelines(lines)
    except IOError as e:
        print(f"Error writing updated playlist: {e}")

# Example Usage
music_directory = '/home/jadson/Músicas/sync/'
output_directory = '/storage/emulated/0/Music/Sync/'
playlist_path = './no pain, no gain .m3u'

update_playlist(playlist_path, music_directory, output_directory)
