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
                # Use the '|' separator found in your logs
                df = pd.read_csv(os.path.join(root, file), sep='|', header=None, on_bad_lines='skip')
                df['label'] = label
                all_events.append(df)

    if not all_events: return
    df_total = pd.concat(all_events)

    # ######## 1. Time Cleaning ########
    # Your logs contain "13:46:06 p.m.". The "p.m." is redundant if it's 24h format.
    # We remove it and parse using an explicit format.
    time_clean = df_total[2].astype(str).str.replace('p.m.', '', regex=False).str.replace('a.m.', '', regex=False).str.strip()
    
    # Explicit format to avoid UserWarning and calculation errors
    df_total['dt'] = pd.to_datetime(df_total[1] + ' ' + time_clean, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df_total = df_total.dropna(subset=['dt']).sort_values('dt')
    
    # Real Unix Epoch (Seconds since 1970)
    df_total['ts_unix'] = (df_total['dt'].astype('int64') // 10**9).astype(int)

    # ######## 2. Node Factorization (Ensures variability) ########
    # src: Column 3 (User ID in the log)
    # dest: Column 5 (Full path)
    df_total['src_id'], _ = pd.factorize(df_total[3])
    df_total['dst_id'], _ = pd.factorize(df_total[5])

    # ######## 3. Export ########
    midas_final = df_total[['src_id', 'dst_id', 'ts_unix']]
    midas_final.to_csv(f"{output_dir}/{output_name}_data.csv", index=False, header=False)
    df_total['label'].to_csv(f"{output_dir}/{output_name}_labels.csv", index=False, header=False)
    
    # Meta file with the total record count
    with open(f"{output_dir}/{output_name}_meta.txt", 'w') as f:
        f.write(str(len(midas_final)))

    print(f"✅ {output_name} processed.")
    print(f"ID Sample (variability check!):")
    print(midas_final.head(5).values.tolist())
    
    # Attack verification
    print(f"Attacks found: {df_total['label'].sum()} out of {len(df_total)} records.")

prepare_user_data('../../WUIL_Logs/User5/', 'user5')
prepare_user_data('../../WUIL_Logs/User6/', 'user6')
prepare_user_data('../../WUIL_Logs/User7/', 'user7')