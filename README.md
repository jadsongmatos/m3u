# Script de Atualização de Playlist

## Descrição

Este script Python é projetado para atualizar playlists no formato M3U(8), substituindo os caminhos antigos das músicas por novos, com base em um diretório fornecido. Ele lê os metadados dos arquivos de áudio, como título, artista e duração, para identificar as músicas na playlist e atualizar seus caminhos.

## Requisitos

- Python 3.x
- Bibliotecas Python:
  - `mutagen` para ler metadados de arquivos de áudio.
  - `textdistance` para calcular a similaridade entre strings.

## Uso

1. Modifique as variáveis `music_directory`, `output_directory` e `playlist_path` no script para corresponder aos seus diretórios e arquivo de playlist.
   
   - `music_directory`: Caminho do diretório onde suas músicas estão armazenadas.
   - `output_directory`: Caminho do diretório onde as músicas atualizadas serão referenciadas na playlist.
   - `playlist_path`: Caminho da playlist M3U(8) que você deseja atualizar.

2. Execute o script:
   ```bash
   python nome_do_script.py
   ```

## Funcionalidades

- **Leitura de Metadados**: Lê os metadados de arquivos de áudio em vários formatos, incluindo MP3, FLAC, WMA, OGG e MP4.
- **Análise de Playlist**: Analisa cada linha da playlist e extrai informações como duração, artista e título.
- **Busca de Músicas**: Procura no diretório fornecido por músicas que correspondam às informações da playlist.
- **Atualização de Playlist**: Atualiza a playlist com os novos caminhos das músicas encontradas.

## Observações

- O script assume que a playlist está no formato M3U(8) e que os metadados das músicas são suficientemente detalhados para permitir uma correspondência precisa.
- Ajuste a variável `similarity_max` na função `find_music` para modificar a sensibilidade da correspondência de músicas.
- O script cria uma nova playlist com o sufixo `_updated` em seu nome, mantendo a original inalterada.

## Contribuições

Contribuições para melhorar o script são bem-vindas. Por favor, sinta-se à vontade para fazer fork do projeto, fazer alterações e enviar pull requests.