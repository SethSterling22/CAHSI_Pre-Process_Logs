import datetime
import sys
import os

# Diccionarios para mapear nodos si no son numéricos (opcional, pero recomendado)
node_map = {}
next_id = 0


def get_node_id(node_str):
    global next_id
    if node_str not in node_map:
        node_map[node_str] = next_id
        next_id += 1
    return node_map[node_str]



def convert(input_file):
    file_name_only = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"midas_{file_name_only}_input.csv"
    with open(input_file, 'r') as f, open(output_file, 'w') as out:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) < 5:
                continue
                
            # 1. Extraer Nodos (Source y Destination)
            # Si ya son números y quieres mantenerlos, quita el get_node_id
            src = parts[3] 
            dest = parts[4]
            
            # 2. Procesar Timestamp
            # Combinamos fecha y hora. Limpiamos 'p.m.' para que Python lo entienda
            date_str = parts[1]
            time_str = parts[2].replace('p.m.', 'PM').replace('a.m.', 'AM')
            full_time = f"{date_str} {time_str}"
            
            try:
                dt = datetime.datetime.strptime(full_time, "%d/%m/%Y %H:%M:%S %p")
                # Convertimos a Unix Timestamp (segundos totales)
                timestamp = int(dt.timestamp())
            except ValueError:
                # Si el formato de hora falla, intentamos sin AM/PM
                try:
                    dt = datetime.datetime.strptime(f"{date_str} {parts[2]}", "%d/%m/%Y %H:%M:%S")
                    timestamp = int(dt.timestamp())
                except:
                    continue

            # 3. Escribir al archivo final (formato: src,dest,timestamp)
            out.write(f"{src},{dest},{timestamp}\n")

    print(f"Conversión completada. Archivo guardado como: {output_file}")


def main():
    input_file = sys.argv[1]
    convert(input_file)

if __name__ == "__main__":
    main()
