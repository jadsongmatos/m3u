import sqlite3
import mimetypes
import os
from tqdm import tqdm
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4

# Conectar ao banco de dados SQLite
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Criar uma tabela FTS
cursor.execute("""
    CREATE TABLE IF NOT EXISTS musicas(
        id INTEGER PRIMARY KEY,
        title TEXT,
        artist TEXT,
        duration INTEGER
    );
""")

cursor.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS musicas_fts USING fts5(
    title,
    artist,
    content='musicas',
    content_rowid='id'
);
""")


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
                            # Insert into musicas table
                            cursor.execute("INSERT INTO musicas (duration, title, artist) VALUES (?, ?, ?);", (
                                metadata['duration'], metadata['title'], metadata['artist'],))

                            # Insert into musicas_fts table
                            cursor.execute("INSERT INTO musicas_fts (rowid, title, artist) VALUES (last_insert_rowid(), ?, ?);", (
                                metadata['title'], metadata['artist'],))

                    except Exception as e:
                        print(f"Error processing file {file}: {e}")
        pbar.close()


music_directory = '/home/jadson/Músicas/sync/'
find_music(music_directory)

# Realizar uma pesquisa FTS e obter a relevância (BM25)
termo_pesquisa = 'jail* OR house*'
# Executar a consulta FTS
#cursor.execute("SELECT * FROM musicas_fts WHERE title MATCH ?", (termo_pesquisa,))
cursor.execute("SELECT *, bm25(musicas_fts) FROM musicas_fts WHERE title MATCH ? ORDER BY bm25(musicas_fts)", (termo_pesquisa,))

# Fetch e print dos resultados
resultados = cursor.fetchall()
for resultado in resultados:
    print(resultado)

conn.close()
