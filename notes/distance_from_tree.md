Yes! **FastTree** can compute a **distance matrix** before constructing a tree. However, it does not output the matrix directly in a standard format. You have two options to extract it:

---

### **1. Using FastTree’s Internal Distance Matrix (Pairwise Distances)**
FastTree can compute **pairwise distances** using the `-noml -nome -log logfile.txt` options:

```bash
FastTree -wag -noml -nome input.aln > tree.nwk 2> logfile.txt
```
- `-noml` → Disables maximum likelihood (ML) branch length optimization.  
- `-nome` → Disables minimum evolution (ME) post-processing.  
- `-wag` → Uses the WAG model (for proteins).  
- `2> logfile.txt` → Redirects log output to a file.  

After running this, **logfile.txt** will contain a **pairwise distance matrix** that you can extract.

---

### **2. Extracting the Distance Matrix from a Newick Tree**
FastTree outputs a tree in **Newick format**, which does not directly include a distance matrix. However, you can compute it from the tree using **Biopython**:

#### **Python Script to Convert Newick Tree to Distance Matrix**
```python
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix
import numpy as np

# Load the FastTree Newick tree
tree = Phylo.read("tree.nwk", "newick")

# Get all terminal node names
terminals = [term.name for term in tree.get_terminals()]

# Initialize distance matrix
matrix_size = len(terminals)
dist_matrix = np.zeros((matrix_size, matrix_size))

# Compute pairwise distances
for i, seq1 in enumerate(terminals):
    for j, seq2 in enumerate(terminals):
        if i <= j:
            distance = tree.distance(seq1, seq2)
            dist_matrix[i][j] = distance
            dist_matrix[j][i] = distance  # Symmetric matrix

# Print the matrix
print("Distance Matrix:")
print(dist_matrix)
```
- This reads the **Newick tree** and extracts pairwise distances.  
- The result is a symmetric **distance matrix** with evolutionary distances between sequences.  

---

### **Which Method Should You Use?**
- If you just want **raw pairwise distances**, use **`-noml -nome` and extract from `logfile.txt`**.  
- If you need **phylogenetic distances**, extract from the **Newick tree** using Biopython.  

Would you like an example output from either method? 😊