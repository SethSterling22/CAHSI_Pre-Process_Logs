import pandas as pd
import os
import zlib

def prepare_slade_data(user_path, output_name):
    output_dir = "Results_SLADE"
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)

    all_events = []
    
    # 1. Recursive search for .txt log files in User folders
    for root, dirs, files in os.walk(user_path):
        for file in files:
            if file.endswith('.txt'):
                # Identify attack logs based on the folder name
                # label = 1 for 'Attack', 0 for normal traffic
                label = 1 if 'Attack' in root else 0
                try:
                    # Using '|' as the separator based on WUIL log structure
                    df = pd.read_csv(os.path.join(root, file), sep='|', header=None, on_bad_lines='skip')
                    df['label'] = label
                    all_events.append(df)
                except Exception as e:
                    print(f"Error loading {file}: {e}")

    if not all_events: 
        print(f"No logs found for {output_name}")
        return
        
    df_total = pd.concat(all_events)

    # --- 2. Temporal Normalization ---
    # Standardizing time by removing regional suffixes (p.m./a.m.)
    time_clean = df_total[2].astype(str).str.replace('p.m.', '', regex=False).str.replace('a.m.', '', regex=False).str.strip()
    
    # Convert string dates (DD/MM/YYYY) and times to datetime objects
    df_total['dt'] = pd.to_datetime(df_total[1] + ' ' + time_clean, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Drop invalid dates and sort chronologically to preserve the stream order
    df_total = df_total.dropna(subset=['dt']).sort_values('dt')
    
    # Convert to Unix Epoch (seconds) for SLADE compatibility
    df_total['ts_unix'] = (df_total['dt'].astype('int64') // 10**9).astype(int)

    # --- 3. Deterministic Hashing for SLADE Compatibility ---
    # SLADE requires integer nodes. We hash the full file path to ensure uniqueness.
    def string_to_int_hash(s):
        # CRC32 provides a consistent 32-bit integer representation of the string
        return zlib.crc32(str(s).encode('utf-8')) & 0xffffffff

    # src: UserID (Column 4) | dst: Full Directory Path (Column 5)
    df_total['src_id'] = df_total[4].apply(string_to_int_hash)
    df_total['dst_id'] = df_total[5].apply(string_to_int_hash)

    # --- 4. Exporting to SLADE Format ---
    # SLADE format: source_id, destination_id, timestamp, label
    slade_final = df_total[['src_id', 'dst_id', 'ts_unix', 'label']]
    
    # Saving as a standard CSV (SLADE usually reads comma-separated files)
    output_file = f"{output_dir}/{output_name}_slade.csv"
    slade_final.to_csv(output_file, index=False, header=False)

    print(f"--- Export Summary for {output_name} ---")
    print(f"File saved to: {output_file}")
    print(f"Total records: {len(slade_final)}")
    print(f"Attack samples: {df_total['label'].sum()}")
    print(f"Attack Density: {(df_total['label'].sum()/len(slade_final))*100:.2f}%")
    print("-------------------------------------------\n")

# Run processing for User 8 as requested
# Adjust the path to your WUIL_Logs directory accordingly
prepare_slade_data('../../WUIL_Logs/User8/', 'user7')
prepare_slade_data('../../WUIL_Logs/User8/', 'user8')