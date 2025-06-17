import os
import subprocess
import re
import csv

def compute_rmsd(pdb_file, cif_file):
    """
    Call TMscore executable to calculate RMSD between pdb_file and cif_file.
    Returns a tuple (rmsd, full_output):
      - rmsd: parsed RMSD value (float), returns None if parsing fails;
      - full_output: complete output text from TMscore program, for debugging.
    """
    # Assume TMscore executable is in the current directory, named "TMscore"
    # Add -seq option to consider sequence order for structure alignment
    command = f"./TMscore -seq {pdb_file} {cif_file}"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout

        # Modify regex to match the value after "RMSD of the common residues="
        match = re.search(r"RMSD of\s+the common residues=\s*([\d\.]+)", output)
        if match:
            rmsd = float(match.group(1))
            return rmsd, output
        else:
            print(f"[Warning] Unable to parse RMSD output for {pdb_file} and {cif_file}:\n{output}")
            return None, output
    except subprocess.CalledProcessError as e:
        print(f"[Error] Error running TMscore: {pdb_file} and {cif_file}\nError message: {e}")
        return None, None

def main():
    # Reference folder path
    reference_folder = "/Users/wangyuxuan/Desktop/final_results/all"
    
    # List of folders to compare
    target_folders = [
        "/Users/wangyuxuan/Desktop/final_results/alphafold3",
        "/Users/wangyuxuan/Desktop/final_results/chai",
        "/Users/wangyuxuan/Desktop/final_results/helixfold3",
        "/Users/wangyuxuan/Desktop/final_results/protenix"
    ]
    
    # Create output directory (if it doesn't exist)
    output_dir = "/Users/wangyuxuan/Desktop/final_results/metrics/rmsd"
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .pdb files in the reference folder
    pdb_files = [f for f in os.listdir(reference_folder) if f.lower().endswith('.pdb')]
    if not pdb_files:
        print("No PDB files found in the reference folder.")
        return
    
    # Calculate for each target folder
    for target_folder in target_folders:
        folder_name = os.path.basename(target_folder)
        print(f"\nStarting to process folder: {folder_name}")
        
        # Output CSV filename
        output_file = os.path.join(output_dir, f"rmsd_{folder_name}.csv")
        results = []  # For storing calculation results, each element is (pdbid, rmsd)
        
        for pdb_filename in pdb_files:
            # Get base filename without extension (e.g., "7d8o")
            base_name = os.path.splitext(pdb_filename)[0]
            # Corresponding CIF filename
            cif_filename = base_name + ".cif"
            pdb_path = os.path.join(reference_folder, pdb_filename)
            cif_path = os.path.join(target_folder, cif_filename)

            # Check if corresponding CIF file exists in target folder
            if not os.path.exists(cif_path):
                print(f"Skipping {base_name}: Corresponding CIF file not found in {folder_name} folder.")
                continue

            print(f"Calculating RMSD for {base_name} ...")
            rmsd, tm_output = compute_rmsd(pdb_path, cif_path)
            if rmsd is not None:
                results.append((base_name, rmsd))
                print(f"RMSD for {base_name}: {rmsd}")
            else:
                print(f"Failed to calculate RMSD for {base_name}.")

        # Sort results by pdbid (base filename)
        results.sort(key=lambda x: x[0])

        # Write results to CSV file
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Structure", "RMSD"])
            for base_name, rmsd in results:
                writer.writerow([base_name, rmsd])

        print(f"Results for {folder_name} saved to {output_file}")
    
    print("\nRMSD calculation completed for all folders!")

if __name__ == "__main__":
    main()