from Bio import SeqIO
import json

def fasta_to_af_json(fasta_file, output_file, job_name):
    # Read sequences from FASTA file
    sequences = []
    for record in SeqIO.parse(fasta_file, "fasta"):
        seq_entry = {
            "protein": {
                "sequence": str(record.seq),
                "name": record.id,
                "description": record.description
            }
        }
        sequences.append(seq_entry)
    
    # Create AlphaFold JSON structure
    af_json = {
        "name": job_name,
        "modelSeeds": [1, 2],
        "sequences": sequences,
        "dialect": "alphafold3",
        "version": 2
    }
    
    # Write JSON to file
    with open(output_file, 'w') as f:
        json.dump(af_json, f, indent=2)

# Remove main() function and replace with direct usage example
if __name__ == "__main__":
    # Example usage - modify these values as needed
    input_fasta = "/zhome/85/8/203063/a3_fungi/data/s_cer_query.fasta"
    output_json = input_fasta.replace(".fasta", ".json")
    job_name = "s_cer_query"
    
    fasta_to_af_json(input_fasta, output_json, job_name)
