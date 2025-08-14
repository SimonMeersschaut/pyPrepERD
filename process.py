import glob
import analysis
from gui.plot import Plot
import os
import utils

# WORK_DIR = "\\\\winbe.imec.be\\wasp\\ruthelde\\Simon\\test"


def handle_folder(path: str):
    """
    This function will open a folder and perform all actions required to go from .flt files
    to the desired folder structure.
    """
    
    flt_files = glob.glob(path + "/*.flt")

    if len(flt_files) > 1:
        # multiple files, sort each file to a different file

        for flt_file in flt_files:
            print(f"Handling {flt_file}")

            flt_data = analysis.load_flt_file(flt_file)
            ns_ch, t_offs = analysis.load_tof_file("tests/analysis/transform/Tof.in")
            B0, B1, B2 = analysis.load_bparams_file(path+"/Bparams.txt")
            extended_data = analysis.extend_flt_data(flt_data, B0, B1, B2, ns_ch, t_offs)

            # Create plots
            title = flt_file.replace(".flt", ".evt.png")
            pixels = utils.create_grid(extended_data, x_index=1, y_index=2)
            plot = Plot()
            plot.set_data(pixels, extended_data, title)
            plot.save(title)

            title = flt_file.replace(".flt", ".mvt.png")
            pixels = utils.create_grid(extended_data, x_index=1, y_index=4)
            plot = Plot()
            plot.set_data(pixels, extended_data, title)
            plot.save(title)

            # Move .flt file to subdirectory
            flt_filename = flt_file.split('/')[-1].split('\\')[-1]
            new_dir_name = flt_filename.split('.')[0].split('_')[-1] # e.g. "01A"
            try:
                os.mkdir(path+f"/{new_dir_name}")
            except FileExistsError:
                pass
                
            # Move flt files to subdirectories
            new_filename = path + '/' + new_dir_name + '/' + flt_filename
            os.rename(flt_file, new_filename)
        
        # Move all other files to a raw directory
        # e.g. job.json, any_trends.csv, erd_trends.csv, ERD25_090_01A.meta ...
        other_files = glob.glob(path + "/*.flt")
        if len(other_files) > 0:
            try:
                os.mkdir(path+f"/raw")
            except FileExistsError:
                pass
            
            for other_file in other_files:
                other_filename = other_file.split('/')[-1].split('\\')[-1]
                new_filename = path + "/raw/" + other_filename

                

def main():
    handle_folder("\\\\winbe.imec.be\\wasp\\ruthelde\\Simon\\test")

if __name__ == "__main__":
    main()