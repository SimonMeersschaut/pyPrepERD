from .a_params import extended_data_to_a_params
from analysis import load_lst_file, extend_flt_data, load_bparams_file, load_tof_file
import os
import glob

def generate_a_params(project: str) -> str:
    """
    Generates a file with a params based on measurements and a cut (polygon)
    all located in the project folder.
    """
    if not os.path.exists(project):
        raise FileNotFoundError(f"Project folder `{project}` not found.")

    # Per measurement, open the data
    subfolders = [f.path for f in os.scandir(project) if f.is_dir() and not "raw" in f.path[0]] # TODO: `in` aanpassen

    for subfolder in subfolders:
        # Open the .lst file
        lst_files = glob.glob(subfolder+"/*.lst")
        
        if len(lst_files) != 1:
            raise RuntimeError()
        lst_file  = lst_files[0]

        flt_data = load_lst_file(lst_file)
        B0, B1, B2 = load_bparams_file("tests/analysis/transform/Bparams.txt")
        ns_ch, t_offs = load_tof_file("tests/analysis/transform/Tof.in")
        extended_data = extend_flt_data(flt_data, B0, B1, B2, ns_ch, t_offs)

        extended_data_to_a_params(extended_data)