import pandas as pd
import os

def prepare_user_data(user_path, output_name):
    # 1. Load normal files and attack files
    # Adjust filenames based on User
    normal_files = [f for f in os.listdir(user_path) if 'Attack' not in f and f.endswith('.txt')]
    attack_files = [f for f in os.listdir(user_path) if 'Attack' in f and f.endswith('.txt')]
    
    data_frames = []
    
    # Load normal files
    for f in normal_files:
        df = pd.read_csv(os.path.join(user_path, f), sep='|', header=None)
        df['label'] = 0
        data_frames.append(df)
        
    # Load Attacks
    for f in attack_files:
        df = pd.read_csv(os.path.join(user_path, f), sep='|', header=None)
        df['label'] = 1
        data_frames.append(df)
    
    full_data = pd.concat(data_frames)
    
    # 2. Conversión de Tiempo a segundos (Epoch o relativo)
    # WUIL: Col 1: Fecha, Col 2: Hora
    full_data['datetime'] = pd.to_datetime(full_data[1] + ' ' + full_data[2].str.replace('p.m.', 'PM').str.replace('a.m.', 'AM'))
    full_data = full_data.sort_values('datetime') # Orden cronológico
    
    # 3. Formateo para MIDAS (src, dest, ts)
    # src: Col 3 (ID), dest: Col 4 (Recurso/Página), ts: Segundos
    midas_df = pd.DataFrame({
        'src': full_data[3],
        'dest': full_data[4],
        'ts': (full_data['datetime'] - full_data['datetime'].min()).dt.total_seconds().astype(int)
    })
    
    midas_df.to_csv(f"{output_name}_data.csv", index=False, header=False)
    full_data['label'].to_csv(f"{output_name}_labels.csv", index=False, header=False)
    
    # Archivo Meta para MIDAS Demo
    with open(f"{output_name}_meta.txt", 'w') as f:
        f.write(str(len(midas_df)))

# Ejecutar para 3 usuarios
prepare_user_data('../WUIL_Logs/User1/', 'user1')
prepare_user_data('../WUIL_Logs/User2/', 'user2')
prepare_user_data('../WUIL_Logs/User3/', 'user3')