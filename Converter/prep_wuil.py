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

prepare_user_data('../../WUIL_Logs/User4/', 'user4')
# prepare_user_data('../../WUIL_Logs/User2/', 'user2')
# prepare_user_data('../../WUIL_Logs/User3/', 'user3')