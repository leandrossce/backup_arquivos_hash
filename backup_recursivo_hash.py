import os
import shutil
import hashlib
from datetime import datetime

def get_last_backup_time(backup_dir):
    """Recuperar a hora do último backup de um arquivo."""
    last_backup_file = os.path.join(backup_dir, 'tempo_do_ultimo_backup.txt')
    if os.path.exists(last_backup_file):
        with open(last_backup_file, 'r') as file:
            return datetime.fromisoformat(file.read().strip())
    return None

def set_last_backup_time(backup_dir):
    """Salve a hora atual como a hora do último backup."""
    last_backup_file = os.path.join(backup_dir, 'tempo_do_ultimo_backup.txt')
    with open(last_backup_file, 'w') as file:
        file.write(datetime.now().isoformat())

def calculate_hash(file_path):
    """Calcular o hash SHA-256 de um arquivo."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def count_total_files(source_dir):
    """Contar o número total de arquivos no diretório e subdiretórios."""
    total_files = 0
    for _, _, filenames in os.walk(source_dir):
        total_files += len(filenames)
    return total_files

def backup_modified_files(source_dir, backup_dir):
    """Arquivos de backup modificados desde o último backup, preservando a estrutura de diretórios."""
    last_backup_time = get_last_backup_time(backup_dir)
    if last_backup_time is None:
        last_backup_time = datetime.min

    error_files = []

    total_files = count_total_files(source_dir)
    processed_files = 0
    
    for foldername, subfolders, filenames in os.walk(source_dir):
        rel_path = os.path.relpath(foldername, source_dir)
        backup_subdir = os.path.join(backup_dir, rel_path)
        if not os.path.exists(backup_subdir):
            os.makedirs(backup_subdir)

        for filename in filenames:
            source_file = os.path.join(foldername, filename)
            backup_file = os.path.join(backup_subdir, filename)

            try:
                # Calcular o hash dos arquivos de origem e destino
                source_hash = calculate_hash(source_file)
                if os.path.exists(backup_file):
                    backup_hash = calculate_hash(backup_file)
                else:
                    backup_hash = None

                # Comparar hashes e copiar se diferente
                if source_hash != backup_hash:
                    shutil.copy2(source_file, backup_file)
                    print(f'\rBackup atualizado para: {filename}\n')

                # Atualizar o contador de arquivos processados e mostrar progresso
                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f'\rProgresso: {progress:.2f}%', end='')

            except PermissionError:
                print(f'Erro de permissão: não foi possível copiar {source_file}')
                error_files.append(source_file)

    # Atualiza a data do último backup
    set_last_backup_time(backup_dir)

    # Salvar arquivos com erros em erros_backup.txt
    if error_files:
        error_file_path = os.path.join(backup_dir, 'erros_backup.txt')
        with open(error_file_path, 'w') as file:
            for error_file in error_files:
                file.write(f'{error_file}\n')
        print(f'Lista de arquivos com erros salva em {error_file_path}')

# Solicitar ao usuário os diretórios de origem e destino
source_directory = input("Digite o caminho completo do diretório de origem: ")
backup_directory = input("Digite o caminho completo do diretório de backup: ")

# Verifica se os diretórios fornecidos são válidos
if not os.path.isdir(source_directory):
    print("O caminho do diretório de origem não existe. Por favor, verifique e tente novamente.")
elif not os.path.isdir(backup_directory):
    print("O caminho do diretório de backup não existe. Por favor, verifique e tente novamente.")
else:
    # Executar o backup
    backup_modified_files(source_directory, backup_directory)
