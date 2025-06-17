import os
import subprocess

# Path to the lddt executable (modify to full path if not in PATH, e.g., "/path/to/openstructure/bin/lddt")
LDDT_EXECUTABLE = "lddt"

# Reference structure folder
REFERENCE_FOLDER = "/Users/wangyuxuan/Desktop/final_results/all"

# List of target folders
TARGET_FOLDERS = [
    "/Users/wangyuxuan/Desktop/final_results/alphafold3",
    "/Users/wangyuxuan/Desktop/final_results/chai",
    "/Users/wangyuxuan/Desktop/final_results/helixfold3",
    "/Users/wangyuxuan/Desktop/final_results/protenix"
]

# Output results folder
OUTPUT_FOLDER = "./lddt_results"

def calculate_lddt_for_folders():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print(f"Reference structure folder: {REFERENCE_FOLDER}")
    print(f"Target folders: {TARGET_FOLDERS}")
    print(f"Results will be saved to: {OUTPUT_FOLDER}")

    # Get all PDB files in the reference folder
    reference_files = {f for f in os.listdir(REFERENCE_FOLDER) if f.endswith(".pdb")}

    for target_folder in TARGET_FOLDERS:
        print(f"\nProcessing target folder: {target_folder}")
        model_files = [f for f in os.listdir(target_folder) if f.endswith(".pdb")]

        for model_file in model_files:
            model_path = os.path.join(target_folder, model_file)
            # Assume reference file has the same name as the model file
            reference_file_name = model_file # Or adjust based on actual naming rules

            if reference_file_name in reference_files:
                reference_path = os.path.join(REFERENCE_FOLDER, reference_file_name)
                output_filename = f"{os.path.basename(target_folder)}_{os.path.splitext(model_file)[0]}.lddt.txt"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)

                command = [LDDT_EXECUTABLE, model_path, reference_path]
                print(f"Executing command: {' '.join(command)}")

                try:
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    with open(output_path, "w") as f:
                        f.write(result.stdout)
                    print(f"lddt results saved to: {output_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to execute lddt command, file: {model_file} vs {reference_file_name}")
                    print(f"Error output: {e.stderr}")
                except FileNotFoundError:
                    print(f"Error: lddt executable not found. Please check LDDT_EXECUTABLE path or ensure lddt is in your system PATH.")
                    return
            else:
                print(f"Warning: No reference file found for {model_file} in the reference folder.")

    print("\nAll lddt calculations completed.")

if __name__ == "__main__":
    calculate_lddt_for_folders()