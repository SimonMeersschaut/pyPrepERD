import glob
import analysis
from gui.plot import ERDPlot
import os
import shutil
import utils


def handle_folder(path: str):
    """
    This function will open a folder and perform all actions required to go from .lst files
    to the desired folder structure.
    """
    if os.path.exists(path+"/Tof.in"):
        print("""
        This folder already contains a `Tof.in` file, 
        so it has (probably) already been analysed.
        Skipping this folder.
        """)
        return
    
    lst_files = glob.glob(path + "/*.lst")

    for lst_file in lst_files:
        print(f"Handling {lst_file}")

        lst_data = analysis.load_lst_file(lst_file)
        # analysis.
        ns_ch, t_offs = analysis.load_tof_file(utils.TOF_FILE_PATH)
        B0, B1, B2 = analysis.load_bparams_file(utils.BPARAMS_FILE_PATH)
        extended_data = analysis.extend_flt_data(lst_data, B0, B1, B2, ns_ch, t_offs)

        # Create plots
        title = lst_file.replace(".lst", ".evt.png")
        pixels, _ = utils.create_grid(extended_data, x_index=1, y_index=2)
        plot = ERDPlot()
        plot.set_data(pixels, extended_data, title)
        plot.save(title)

        title = lst_file.replace(".lst", ".mvt.png")
        pixels, _ = utils.create_grid(extended_data, x_index=1, y_index=4)
        plot = ERDPlot()
        plot.set_data(pixels, extended_data, title)
        plot.save(title)

        # Move .flt file to subdirectory
        lst_filename = lst_file.split('/')[-1].split('\\')[-1]
        new_dir_name = lst_filename.split('.')[0].split('_')[-1] # e.g. "01A"
        try:
            os.mkdir(path+f"/{new_dir_name}")
        except FileExistsError:
            pass

        # copy Tof.in to this folder
        if not os.path.exists(path+f"/{new_dir_name}/Tof.in"):
            shutil.copyfile(utils.TOF_FILE_PATH, path+f"/{new_dir_name}/Tof.in")
            
        # Move flt files to subdirectories
        new_filename = path + '/' + new_dir_name + '/' + lst_filename
        os.rename(lst_file, new_filename)

        # Write .mvt & .evt files
        analysis.dump_dataframe(extended_data[:, [0, 4]], new_filename.replace(".lst", ".mvt.flt")) # mvt
        analysis.dump_dataframe(extended_data[:, [2, 4]], new_filename.replace(".lst", ".evt.flt")) # evt
    
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