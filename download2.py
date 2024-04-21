import os
import requests
from concurrent.futures import ThreadPoolExecutor

def download_file(url, output_dir):
    file_name = url.split('/')[-1]
    file_path = url.split(base_url)[1].split(file_name)[0]
    file_dir = os.path.join(output_dir, file_path)

    # Crear directorios si no existen
    if not os.path.exists(file_dir):
        try:
            os.makedirs(file_dir)
        except FileExistsError:
            pass
    response = requests.get(url)
    if response.status_code == 200:
        print(" OUT DIR: "+output_dir)
        print(" PATH: "+file_path)
        print(" NAME: "+file_name)
        with open(os.path.join(output_dir, file_path, file_name), 'wb') as f:
            f.write(response.content)
        print(f"Descargado: {file_name}")
    else:
        print(f"No se pudo descargar el archivo: {file_name}")

def parse_m3u8_file(url, output_dir):
    
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.splitlines()
        with ThreadPoolExecutor() as executor:
            futures = []
            for line in lines:
                if line.endswith('.m3u8'):
                    line=base_url+line
                    download_file(line, output_dir)
                    futures.append(executor.submit(parse_m3u8_file(line, output_dir)))
                if line.endswith('.ts'):
                    #output_dir_file = "/"+line.split('bitrate')[0]
                    line=base_url+line
                    futures.append(executor.submit(download_file, line, output_dir))
                if line.endswith('.webvtt'):
                    line=base_url+line
                    futures.append(executor.submit(download_file, line, output_dir))
                if line.startswith('#EXT-X-MEDIA') and 'URI="' in line:
                    audio_url = base_url + line.split('URI="')[1].split('"')[0]
                    futures.append(executor.submit(download_file, audio_url, output_dir))
                    futures.append(executor.submit(parse_m3u8_file, audio_url, output_dir))
            for future in futures:
                if future.result() is not None:
                    future.result()
                

if __name__ == "__main__":
    main_m3u8_url = "http://directes-tv-cat.ccma.cat/live-origin/tv3-hls/master.m3u8"
    output_dir = "downloaded_files"
    base_url= "http://directes-tv-cat.ccma.cat/live-origin/tv3-hls/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    parse_m3u8_file(main_m3u8_url, output_dir)
