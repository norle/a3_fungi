from Bio import SeqIO
import os
import pandas as pd

def filter_fasta(fasta_path, names, output_path):
    # Keep track of found sequences
    found_names = set()
    
    # Filter sequences and write directly to output file
    sequences = SeqIO.parse(fasta_path, "fasta")
    filtered_sequences = []
    
    for seq in sequences:
        if seq.id in names:
            filtered_sequences.append(seq)
            found_names.add(seq.id)
    
    SeqIO.write(filtered_sequences, output_path, "fasta")
    
    # Report missing sequences
    missing_names = set(names) - found_names
    if missing_names:
        print(f"\nMissing sequences in {os.path.basename(fasta_path)}:")
        for name in missing_names:
            print(f"- {name}")
    
    return len(missing_names)

def main():
    main_dir = '/work3/s233201/enzyme_out_5'
    file_names = ["ACO2", "ARO8", "LYS1", "LYS2", "LYS4", "LYS9", "LYS12", "LYS20"]

    to_keep = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing_after_interpro.csv')

    names = to_keep['Accession'].tolist()
    
    # Create output directory if it doesn't exist
    out_dir = os.path.join(main_dir, 'filtered_fastas')
    os.makedirs(out_dir, exist_ok=True)

    # Process each file and track total missing sequences
    total_missing = 0
    for file_name in file_names:
        input_path = os.path.join(main_dir, file_name+'.fasta')
        output_path = os.path.join(out_dir, file_name+'_filtered.fasta')
        missing = filter_fasta(input_path, names, output_path)
        total_missing += missing
    
    print(f"\nTotal missing sequences across all files: {total_missing}")

if __name__ == "__main__":
    main()

