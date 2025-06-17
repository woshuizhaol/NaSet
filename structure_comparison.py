from pymol import cmd, stored
import os

# Configure paths
base_dir = "/Users/wangyuxuan/Desktop/final_results"
model_folders = ["alphafold3", "chai-1", "hdock", "hdock_nt", "helixfold3","protenix"]
exp_dir = os.path.join(base_dir, "all")
output_dir = os.path.join(base_dir, "figures")
pdb_ids = ["7yr7", "8ht7", "7sp1", "8fti", "8bf8"]

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Set display parameters
cmd.set("ray_opaque_background", 0)
cmd.set("antialias", 2)
cmd.set("orthoscopic", "on")

for model in model_folders:
    for pdb_id in pdb_ids:
        # Choose file extension based on model type
        if model in ["hdock", "hdock_nt"]:
            file_ext = "pdb"
        else:
            file_ext = "cif"
            
        # Construct file path, special handling for chai-1 filename
        if model == "chai-1":
            model_filename = f"chai_{pdb_id}.{file_ext}"
        else:
            model_filename = f"{model}_{pdb_id}.{file_ext}"
            
        model_path = os.path.join(base_dir, model, model_filename)
        exp_path = os.path.join(exp_dir, f"{pdb_id}.pdb")
        
        # Check file existence
        if not all(map(os.path.exists, [model_path, exp_path])):
            print(f"File missing: {model_path} or {exp_path}")
            continue

        try:
            # Initialize new session
            cmd.reinitialize()
            
            # Load structures
            exp_obj = f"exp_{pdb_id}"
            model_obj = f"model_{model}_{pdb_id}"
            cmd.load(exp_path, exp_obj)
            cmd.load(model_path, model_obj)

            # Remove water molecules
            cmd.remove("solvent")

            # Align structures
            cmd.super(f"{model_obj} & name CA", 
                     f"{exp_obj} & name CA", 
                     cycles=5)

            # Set colors
            cmd.color("gray80", exp_obj)
            cmd.color("skyblue", f"({model_obj}) and polymer.protein")
            cmd.color("raspberry", f"({model_obj}) and polymer.nucleic")

            # Set display parameters
            cmd.show_as("cartoon")
            cmd.set("cartoon_transparency", 0.5, exp_obj)
            cmd.set("spec_reflect", 0.5)
            cmd.set("bg_rgb", [1, 1, 1])

            # Optimize view
            cmd.orient(exp_obj)
            cmd.zoom(buffer=2)

            # Render output
            output_file = os.path.join(output_dir, f"{model}_{pdb_id}.png")
            cmd.png(output_file, width=3000, height=2000, dpi=600, ray=1)
            
            # Force clear all objects
            cmd.delete("*")  # Explicitly delete all objects
            cmd.refresh()    # Force refresh interface
            
            print(f"Successfully generated: {output_file}")
            
        except Exception as e:
            print(f"Error processing {model}_{pdb_id}: {str(e)}")
            # Clear structures even in case of exception
            cmd.reinitialize()
            continue

print("All processing completed!")