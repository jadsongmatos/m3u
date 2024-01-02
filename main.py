import textdistance
import os
import urllib.parse
from mutagen.mp3 import MP3

damerau_levenshtein = textdistance.DamerauLevenshtein(external=True)

# audio = MP3('./01_Animals.mp3')
# print(audio.pprint())
# titulo = audio.get('TIT2')[0].replace(" ", "").replace('\n', "").lower()
# artist = audio.get('TPE2')[0].replace(" ", "").replace('\n', "").lower()
# tempo = int(audio.info.length)
# print(artist, titulo, tempo)

playlist = './Just Dance Unlimited - Todas as Músicas!.m3u'

with open(playlist, 'r') as file:
    linhas = file.readlines()

def ler_m3u(linhas):
    musicas = []
    for line in linhas:
        if line.startswith('#EXTINF:'):
            tmp = line.split(",")
            time = int(tmp[0].split(":")[1])  # 194208
            if time > 100000:
                time = int(time/1000)
            url_decodificada = urllib.parse.unquote(tmp[1]).split("-")
            artist = url_decodificada[0].replace(
                " ", "").replace('\n', "").lower()
            url_decodificada.pop(0)
            titulo = ''.join(url_decodificada).replace(
                " ", "").replace('\n', "").lower()
            musicas.append((titulo, artist, time))
    return musicas


def similar(s1, s2):
    result = damerau_levenshtein.normalized_similarity(s1, s2)
    # print(result,s1)
    return result


def encontrar_musica(diretorio, titulo_procurado, artist_procurado, tempo_procurado):
    for raiz, dirs, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith('.mp3'):
                caminho_completo = os.path.join(raiz, arquivo)
                audio = MP3(caminho_completo)
                tempo = int(audio.info.length)
                tempo_similar = 1 / (1 + abs(tempo_procurado - tempo))

                titulo = audio.get('TIT2')[0].replace(
                    " ", "").replace('\n', "").lower()
                titulo_similar = similar(titulo, titulo_procurado)

                artist = audio.get('TPE2')[0].replace(
                    " ", "").replace('\n', "").lower()
                artist_similar = similar(artist, artist_procurado)

                media_similar = (titulo_similar +
                                 artist_similar + tempo_similar)/3

                if media_similar > 0.8:
                    print(media_similar, artist, artist_similar, titulo,
                          titulo_similar, tempo_similar, tempo, tempo_procurado)
                    print(f"Arquivo encontrado: {caminho_completo}")

                    return (urllib.parse.quote(caminho_completo), urllib.parse.quote(caminho_completo.replace(diretorio, "")), urllib.parse.quote(arquivo))
                    # return caminho_completo.replace(diretorio, "")

    return None


musicas = ler_m3u(linhas)
print(musicas)
raiz = '/storage/emulated/0/Music/Sync/'

for i, musica in enumerate(musicas):
    result = encontrar_musica('/home/jadson/Músicas/sync/',
                              musica[0], musica[1], musica[2])
    if result:
        # Substitui a linha desejada
        linhas[1+(i*2+1)] = urllib.parse.quote(raiz+result[1])+'\n'+'\n'.join(result)+'\n'
        # linhas[1+(i*2+1)] = raiz+result+'\n'

# Escreve as linhas de volta no arquivo
with open('playlist.m3u', 'w') as file:
    file.writelines(linhas)
