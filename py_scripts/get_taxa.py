import sys
import csv
from Bio import Entrez
import multiprocessing as mp

# Set your email address (required by NCBI Entrez)
Entrez.email = "reinis.muiznieks1@gmail.com"
INPUT_FILE = "/zhome/85/8/203063/a3_fungi/data_out/busco_results.csv"
OUTPUT_FILE = "/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv"

def fetch_phylum(accession):
    # First get assembly info to get taxid
    search_handle = Entrez.esearch(db="assembly", term=accession)
    search_record = Entrez.read(search_handle)
    search_handle.close()
    if not search_record["IdList"]:
        return "Not Found"

    # Get assembly summary to extract taxid
    asm_id = search_record["IdList"][0]
    sum_handle = Entrez.esummary(db="assembly", id=asm_id)
    sum_record = Entrez.read(sum_handle)
    sum_handle.close()
    
    doc = sum_record["DocumentSummarySet"]["DocumentSummary"][0]
    taxid = doc.get("Taxid", "")
    if not taxid:
        return "No Taxid Found"

    # Get taxonomy information
    tax_handle = Entrez.efetch(db="taxonomy", id=taxid)
    tax_record = Entrez.read(tax_handle)
    tax_handle.close()
    
    if not tax_record:
        return "No Taxonomy Found"
    
    # Extract phylum from lineage
    lineage = tax_record[0].get("LineageEx", [])
    for item in lineage:
        if item.get("Rank") == "phylum":
            return item.get("ScientificName", "Unknown")
    
    return "Phylum Not Found"

def get_processed_accessions(output_file):
    """Read already processed accessions from output file"""
    processed = set()
    try:
        with open(output_file, 'r') as f:
            csv_reader = csv.reader(f)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                if row:  # Check if row is not empty
                    processed.add(row[0])
    except FileNotFoundError:
        pass
    return processed

def main():
    # Create results directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Get already processed accessions
    processed_accessions = get_processed_accessions(OUTPUT_FILE)
    
    # Open output file in CSV format
    with open(OUTPUT_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not processed_accessions:
            writer.writerow(['Accession', 'Phylum'])
        
        # Read input file and process each line
        with open(INPUT_FILE, 'r') as infile:
            next(infile)  # Skip the first line
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                
                accession = line[:15]  # Take first 15 characters
                if accession in processed_accessions:
                    print(f"Skipping already processed accession: {accession}")
                    continue
                
                print(f"Fetching phylum for: {accession}")
                try:
                    phylum = fetch_phylum(accession)
                    print(phylum)
                    writer.writerow([accession, phylum])
                except Exception as e:
                    print(f"Error fetching phylum for {accession}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
