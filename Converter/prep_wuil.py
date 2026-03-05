# import pandas as pd
# import os


# def format_unique_node(path_str):
#     # Convert strings and divide with "_"
#     parts = str(path_str).split('\\')
    
#     if len(parts) > 1:
#         # Take everything except the last one (ex: ['0', '1', '2']) and join: '012'
#         directory_prefix = "".join(parts[:-1])
#         # El último elemento es el archivo/recurso: '33'
#         resource = parts[-1]
#         # Result: '012_33'
#         return f"{directory_prefix}_{resource}"
    
#     # If there's nothing, return the path
#     return path_str


# def prepare_user_data(user_path, output_name):
#     # Create Directory
#     output_dir = "Results"
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         print(f"Directorio creado: {output_dir}")

#     data_frames = []
#     print(f"Buscando datos en: {user_path}")

#     for root, dirs, files in os.walk(user_path):
#         for file in files:
#             if file == 'log.txt' or file.endswith('.txt'):
#                 file_path = os.path.join(root, file)
#                 label = 1 if 'Attack' in root else 0

#                 try:
#                     # Read specifying name and columns to prevent confusions especificando nombres de columnas para evitar confusiones
#                     # 0: ID, 1: Fecha, 2: Hora, 3: UserID, 4: Depth, 5: Path
#                     df = pd.read_csv(file_path, sep='|', header=None, on_bad_lines='skip')
#                     df['label'] = label
#                     data_frames.append(df)
#                     print(f" Cargado: {file_path} (Eventos: {len(df)})")
#                 except Exception as e:
#                     print(f" Error en {file_path}: {e}")

#     if not data_frames:
#         print("No se encontraron datos.")
#         return

#     full_data = pd.concat(data_frames)

#     # --- Date and time fix ---
#     # .str before strip() to work on the entire column
#     full_data['dt_str'] = (
#         full_data[1].astype(str) + ' ' + 
#         full_data[2].astype(str)
#         .str.replace('p.m.', '', regex=False)
#         .str.replace('a.m.', '', regex=False)
#         .str.strip()
#     )

#     full_data['datetime'] = pd.to_datetime(full_data['dt_str'], dayfirst=True, errors='coerce')

#     # Delete rows where date date wrong (just in case)
#     full_data = full_data.dropna(subset=['datetime'])

#     # Order chronologically (Stretegic Injection)
#     full_data = full_data.sort_values('datetime')

#     # --- Pre-process for MIDAS/SLADE ---
#     # src: UserID (Col 3)
#     # dest: The last resource were visited in the route (Col 5) 
#     # Nota: If Col 5 is "0\1\2\33", we take '33' as dest node - 33 is only unique in the same directory - add hash or concatenate the entire path and before the file add "_" ex: 0\1\2\33 = 012_33!!!
#     # full_data['destination_node'] = full_data[5].astype(str).apply(lambda x: x.split('\\')[-1])

#     # midas_df = pd.DataFrame({
#     #     'src': full_data[3],
#     #     'dest': full_data['destination_node'],
#     #     'ts': (full_data['datetime'] - full_data['datetime'].min()).dt.total_seconds().astype(int)
#     # })

#     # Apply function to generate Unique IDs
#     # 1. Crear el identificador de texto único
#     full_data['dest_string'] = full_data[5].apply(format_unique_node)

#     # 2. FACTORIZAR: Convertir strings a números enteros únicos
#     # Esto asigna un ID numérico (0, 1, 2...) a cada ruta única
#     full_data['src_id'], _ = pd.factorize(full_data[3])
#     full_data['dest_id'], _ = pd.factorize(full_data['dest_string'])

#     # 3. Crear el DataFrame con IDs numéricos
#     midas_df = pd.DataFrame({
#         'src': full_data['src_id'],
#         'dest': full_data['dest_id'],
#         'ts': (full_data['datetime'] - full_data['datetime'].min()).dt.total_seconds().astype(int)
#     })

#     # Append save directory
#     data_path = os.path.join(output_dir, f"{output_name}_data.csv")
#     label_path = os.path.join(output_dir, f"{output_name}_labels.csv")
#     meta_path = os.path.join(output_dir, f"{output_name}_meta.txt")

#     # Save files
#     midas_df.to_csv(data_path, index=False, header=False)
#     full_data['label'].to_csv(label_path, index=False, header=False)

#     with open(meta_path, 'w') as f:
#         f.write(str(len(midas_df)))

#     # Success message
#     print(f"{len(midas_df)} Rows Saved sucessfully on ./{output_dir}")
#     print(f"Done: {output_name} ready.")

# # Execution
# prepare_user_data('../../WUIL_Logs/User1/', 'user1')
# prepare_user_data('../../WUIL_Logs/User2/', 'user2')
# prepare_user_data('../../WUIL_Logs/User3/', 'user3')





import pandas as pd
import os

def prepare_user_data(user_path, output_name):
    output_dir = "Results"
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    all_events = []
    for root, dirs, files in os.walk(user_path):
        for file in files:
            if file.endswith('.txt'):
                label = 1 if 'Attack' in root else 0
                # Usamos el separador '|' de tus logs
                df = pd.read_csv(os.path.join(root, file), sep='|', header=None, on_bad_lines='skip')
                df['label'] = label
                all_events.append(df)

    if not all_events: return
    df_total = pd.concat(all_events)

    # --- 1. Limpieza de Tiempo (El problema del 1329214) ---
    # Tus logs tienen "13:46:06 p.m.". El "p.m." es redundante si es formato 24h.
    # Vamos a quitarlo y parsear con formato explícito.
    time_clean = df_total[2].astype(str).str.replace('p.m.', '', regex=False).str.replace('a.m.', '', regex=False).str.strip()
    
    # Formato explícito para evitar el UserWarning y errores de cálculo
    df_total['dt'] = pd.to_datetime(df_total[1] + ' ' + time_clean, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df_total = df_total.dropna(subset=['dt']).sort_values('dt')
    
    # Unix Epoch real (Segundos desde 1970)
    df_total['ts_unix'] = (df_total['dt'].astype('int64') // 10**9).astype(int)

    # --- 2. Factorización de Nodos (Asegurar variabilidad) ---
    # src: Columna 3 (ID de usuario en el log)
    # dest: Columna 5 (Ruta completa)
    df_total['src_id'], _ = pd.factorize(df_total[3])
    df_total['dst_id'], _ = pd.factorize(df_total[5])

    # --- 3. Exportar ---
    midas_final = df_total[['src_id', 'dst_id', 'ts_unix']]
    midas_final.to_csv(f"{output_dir}/{output_name}_data.csv", index=False, header=False)
    df_total['label'].to_csv(f"{output_dir}/{output_name}_labels.csv", index=False, header=False)
    
    with open(f"{output_dir}/{output_name}_meta.txt", 'w') as f:
        f.write(str(len(midas_final)))

    print(f"✅ {output_name} procesado.")
    print(f"Muestra de IDs (debe haber variedad!):")
    print(midas_final.head(5).values.tolist())
    
    # Verificación de ataques
    print(f"Ataques encontrados: {df_total['label'].sum()} de {len(df_total)} registros.")

prepare_user_data('../../WUIL_Logs/User1/', 'user1')
prepare_user_data('../../WUIL_Logs/User2/', 'user2')
prepare_user_data('../../WUIL_Logs/User3/', 'user3')