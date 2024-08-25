import os
import shutil
import hashlib
from datetime import datetime, timedelta

def remove_readonly_recursively(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Verifica os atributos do arquivo
                attributes = os.stat(file_path).st_mode
                
                # Remove o atributo de "somente leitura" se estiver ativo
                if not attributes & 0o200:  # Verifica se o bit de escrita está desativado
                    os.chmod(file_path, attributes | 0o200)  # Ativa o bit de escrita
                    print(f"Atributo 'somente leitura' removido: {file_path}")
                #else:
                    #print(f"O arquivo já tem permissão de escrita: {file_path}")
            except Exception as e:
                print(f"Erro ao processar o arquivo {file_path}: {e}")
                continue

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
    print("Iniciando o processamento. Aguarde!...")

    remove_readonly_recursively (backup_dir)  #remover "somente leitura" no destino (bkp)    
    
    """Arquivos de backup modificados desde o último backup, preservando a estrutura de diretórios."""
    last_backup_time = get_last_backup_time(backup_dir)
    if last_backup_time is None:
        last_backup_time = datetime.min

    error_files = []
    atualizados_files = []
    
    total_files = count_total_files(source_dir)
    #processed_files = 0

    start_time = datetime.now()
    
    for foldername, subfolders, filenames in os.walk(source_dir):
        rel_path = os.path.relpath(foldername, source_dir)
        backup_subdir = os.path.join(backup_dir, rel_path)
        if not os.path.exists(backup_subdir):
            os.makedirs(backup_subdir)

        for filename in filenames:
            print("Analisando: " + source_dir+"\\"+filename)            
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
                    print(f'\rBackup atualizado para: {filename}')
                    print(f'\r{backup_file} foi atualizado no backup...\n', end='')  
                    atualizados_files.append(backup_file)   
                    
                # Atualizar o contador de arquivos processados e mostrar progresso
                #processed_files += 1
                #progress = (processed_files / total_files) * 100
                #print(f'\rProgresso: {progress:.2f}%', end='')

            except Exception as e:
                print(f'Erro do tipo: {e} em {source_file}')		
                error_files.append(source_file)				
                continue

    # Atualiza a data do último backup
    set_last_backup_time(backup_dir)

    # Salvar arquivos com erros em erros_backup.txt
    if error_files:
        error_file_path = os.path.join(backup_dir, 'erros_backup.txt')
        with open(error_file_path, 'w') as file:
            for error_file in error_files:
                file.write(f'{error_file}\n')
        print(f'\nLista de arquivos com erros salva em {error_file_path}')

    # Calcular e exibir a duração do backup
    end_time = datetime.now()
    duration = end_time - start_time
    duration_in_s = duration.total_seconds()
    hours, remainder = divmod(duration_in_s, 3600)
    minutes, seconds = divmod(remainder, 60)
    print("\nArquivos com Erros: ".join(error_files))
    print("\nArquivos atualizados no backup: ".join(atualizados_files))    
    print(f'\nBackup concluído em {int(hours)} horas, {int(minutes)} minutos e {int(seconds)} segundos.')

    # Abrir o arquivo em modo de escrita
    with open(backup_dir+"/arquivos_erros.txt", 'w') as file:
        for item in error_files:
            file.write(f"\n{item}\n")  # Grava cada item do array em uma nova linha

    # Abrir o arquivo em modo de escrita
    with open(backup_dir+"/arquivos_atualizados.txt", 'w') as file:
        for item in atualizados_files:
            file.write(f"\n{item}\n")  # Grava cada item do array em uma nova linha  
            
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
