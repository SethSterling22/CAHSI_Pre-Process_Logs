import pandas as pd
import os

def prepare_user_data(user_path, output_name):
    # Create Directory
    output_dir = "Results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directorio creado: {output_dir}")

    data_frames = []
    print(f"Buscando datos en: {user_path}")

    for root, dirs, files in os.walk(user_path):
        for file in files:
            if file == 'log.txt' or file.endswith('.txt'):
                file_path = os.path.join(root, file)
                label = 1 if 'Attack' in root else 0
                
                try:
                    # Leemos especificando nombres de columnas para evitar confusiones
                    # 0: ID, 1: Fecha, 2: Hora, 3: UserID, 4: Depth, 5: Path
                    df = pd.read_csv(file_path, sep='|', header=None, on_bad_lines='skip')
                    df['label'] = label
                    data_frames.append(df)
                    print(f" Cargado: {file_path} (Eventos: {len(df)})")
                except Exception as e:
                    print(f" Error en {file_path}: {e}")

    if not data_frames:
        print("No se encontraron datos.")
        return

    full_data = pd.concat(data_frames)

    # --- CORRECCIÓN DE FECHA Y HORA ---
    # Usamos .str antes de strip() para que funcione sobre toda la columna
    full_data['dt_str'] = (
        full_data[1].astype(str) + ' ' + 
        full_data[2].astype(str)
        .str.replace('p.m.', '', regex=False)
        .str.replace('a.m.', '', regex=False)
        .str.strip()
    )
    
    # El resto sigue igual
    full_data['datetime'] = pd.to_datetime(full_data['dt_str'], dayfirst=True, errors='coerce')
    
    # Eliminar filas donde la fecha falló (si las hay)
    full_data = full_data.dropna(subset=['datetime'])
    
    # Ordenar cronológicamente (Inyección estratégica)
    full_data = full_data.sort_values('datetime')

    # --- TRATAMIENTO PARA MIDAS/SLADE ---
    # src: UserID (Col 3)
    # dest: El último recurso visitado en la ruta (Col 5)
    # Nota: Si Col 5 es "0\1\2\33", tomamos el '33' como el nodo destino
    full_data['destination_node'] = full_data[5].astype(str).apply(lambda x: x.split('\\')[-1])

    midas_df = pd.DataFrame({
        'src': full_data[3],
        'dest': full_data['destination_node'],
        'ts': (full_data['datetime'] - full_data['datetime'].min()).dt.total_seconds().astype(int)
    })

    # Append save directory
    data_path = os.path.join(output_dir, f"{output_name}_data.csv")
    label_path = os.path.join(output_dir, f"{output_name}_labels.csv")
    meta_path = os.path.join(output_dir, f"{output_name}_meta.txt")

    # Save files
    midas_df.to_csv(data_path, index=False, header=False)
    full_data['label'].to_csv(label_path, index=False, header=False)

    with open(meta_path, 'w') as f:
        f.write(str(len(midas_df)))

    # Success message
    print(f"{len(midas_df)} Rows Saved sucessfully on ./{output_dir}")
    print(f"Done: {output_name} ready.")

# Ejecución
prepare_user_data('../../WUIL_Logs/User1/', 'user1')
prepare_user_data('../../WUIL_Logs/User2/', 'user2')
prepare_user_data('../../WUIL_Logs/User3/', 'user3')