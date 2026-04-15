import pandas as pd
import os
import zlib
import numpy as np

def prepare_ares_data(user_path, output_name):
    output_dir = "./Results_ARES"
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    all_events = []
    # 1. Recolección de logs (Misma lógica que MIDAS)
    for root, dirs, files in os.walk(user_path):
        for file in files:
            if file.endswith('.txt'):
                label = 1 if 'Attack' in root else 0
                try:
                    df = pd.read_csv(os.path.join(root, file), sep='|', header=None, on_bad_lines='skip')
                    df['label'] = label
                    all_events.append(df)
                except Exception as e:
                    print(f"Error loading {file}: {e}")

    if not all_events: return
    df_total = pd.concat(all_events)

    # --- 2. Limpieza de Tiempo ---
    time_clean = df_total[2].astype(str).str.replace('p.m.', '', regex=False).str.replace('a.m.', '', regex=False).str.strip()
    df_total['dt'] = pd.to_datetime(df_total[1] + ' ' + time_clean, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df_total = df_total.dropna(subset=['dt']).sort_values('dt')
    df_total['ts'] = (df_total['dt'].astype('int64') // 10**9).astype(int)

    # --- 3. Hashing Determinístico ---
    def string_to_int_hash(s):
        return zlib.crc32(str(s).encode('utf-8')) & 0xffffffff

    df_total['src'] = df_total[4].apply(string_to_int_hash)
    df_total['dst'] = df_total[5].apply(string_to_int_hash)

    # --- 4. Re-indexación para ARES (Optimización GNN) ---
    # ARES prefiere IDs secuenciales [0...N] para manejar las matrices de adyacencia
    nodes = pd.concat([df_total['src'], df_total['dst']]).unique()
    mapping = {node: i for i, node in enumerate(nodes)}
    df_total['src'] = df_total['src'].map(mapping)
    df_total['dst'] = df_total['dst'].map(mapping)

    # --- 5. Exportar Formato ARES ---
    # ARES suele requerir: src, dst, ts, label en un solo CSV con headers
    ares_final = df_total[['src', 'dst', 'ts', 'label']]
    # Busca esta línea en tu prep_wuil_ares.py y añade header=False
    ares_final.to_csv(f"{output_dir}/{output_name}_ares.csv", index=False, header=False)
    
    # Generar features dummy (ARES las requiere para inicializar su GNN)
    num_edges = len(ares_final)
    dummy_feats = np.zeros((num_edges, 8)) # 8 dimensiones de ceros por defecto
    np.save(f"{output_dir}/{output_name}_ares_features.npy", dummy_feats)

    print(f"✅ {output_name} para ARES listo. Nodos: {len(nodes)} | Ataques: {df_total['label'].sum()}")

# Run for Users
users = ['User1', 'User2', 'User3', 'User4', 'User5', 'User6', 'User7', 'User8', 'User9', 'User11']
for u in users:
    prepare_ares_data(f'../../WUIL_Logs/{u}/', u)
