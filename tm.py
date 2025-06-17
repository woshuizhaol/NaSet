import os
import subprocess
import re
import csv

def compute_tm_score(pdb_file, cif_file):
    """
    Call TMscore executable to calculate TM-score between pdb_file and cif_file.
    Returns a tuple (score, full_output):
      - score: parsed TM-score value (float), returns None if parsing fails;
      - full_output: complete output text from TMscore program, for debugging.
    """
    # Modify command to include -seq option
    command = f"./TMscore -seq {pdb_file} {cif_file}"
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout

        # Modify regex to allow spaces or "-" between "TM" and "score", and ignore case
        match = re.search(r"TM[-\s]*score\s*=\s*([\d\.]+)", output, re.IGNORECASE)
        if match:
            score = float(match.group(1))
            return score, output
        else:
            print(f"[Warning] Unable to parse TM-score output for {pdb_file} and {cif_file}:\n{output}")
            return None, output
    except subprocess.CalledProcessError as e:
        print(f"[Error] Error running TMscore: {pdb_file} and {cif_file}\nError message: {e}")
        return None, None

def main():
    # Reference structure folder
    reference_folder = "/Users/wangyuxuan/Desktop/final_results/all"
    
    # Target folder list
    target_folders = [
        "/Users/wangyuxuan/Desktop/final_results/alphafold3",
        "/Users/wangyuxuan/Desktop/final_results/chai",
        "/Users/wangyuxuan/Desktop/final_results/helixfold3",
        "/Users/wangyuxuan/Desktop/final_results/protenix"
    ]
    
    # Output directory
    output_dir = "/Users/wangyuxuan/Desktop/final_results/metrics/tm-score"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .pdb files in reference folder
    pdb_files = [f for f in os.listdir(reference_folder) if f.lower().endswith('.pdb')]
    if not pdb_files:
        print("No PDB files found in reference folder.")
        return
    
    # Process each target folder
    for target_folder in target_folders:
        folder_name = os.path.basename(target_folder)
        print(f"\nStarting to process target folder: {folder_name}")
        
        # Create output file for current target folder
        output_file = os.path.join(output_dir, f"tm_score_{folder_name}.csv")
        results = []  # For storing calculation results, each element is (pdbid, score)
        
        for pdb_filename in pdb_files:
            # Get base filename without extension (e.g., "7d8o")
            base_name = os.path.splitext(pdb_filename)[0]
            # Corresponding CIF filename
            cif_filename = base_name + ".cif"
            pdb_path = os.path.join(reference_folder, pdb_filename)
            cif_path = os.path.join(target_folder, cif_filename)

            # Check if corresponding CIF file exists in target folder
            if not os.path.exists(cif_path):
                print(f"Skipping {base_name}: Corresponding CIF file not found in {folder_name}.")
                continue

            print(f"Calculating TM-score for {base_name} in {folder_name} ...")
            score, tm_output = compute_tm_score(pdb_path, cif_path)
            if score is not None:
                results.append((base_name, score))
                print(f"TM-score for {base_name} in {folder_name}: {score}")
            else:
                print(f"Failed to calculate TM-score for {base_name} in {folder_name}.")

        # Sort results by pdbid (base filename)
        results.sort(key=lambda x: x[0])

        # Write results to CSV file
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Structure", "TM-score"])
            for base_name, score in results:
                writer.writerow([base_name, score])

        print(f"All results for {folder_name} saved to {output_file}")
    
    print(f"\nTM-score calculation completed for all folders, results saved to {output_dir}")

if __name__ == "__main__":
    main()
