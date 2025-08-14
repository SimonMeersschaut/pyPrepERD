import numpy as np
import os
from utils.config import Config

TOFCHMIN=Config.get_setting("tofchmin")
TOFCHMAX=Config.get_setting("tofchmax")

# public functions

def load_bparams_file(filename: str) -> np.array:
    """
    Opens the bparams file and parses the contents into a numpy array.
    filename: bparams (B0, B1, B2)
    """

    # check exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Bparam file {filename} not found.")
    
    # check extension
    ext = filename.split('.')[-1]
    if ext != "txt":
        raise NameError(f"`{filename}` has the wrong extension. Expected `txt`, got `{ext}`.")
    
    # parse file
    
    B0 = np.zeros(TOFCHMAX+1)
    B1 = np.zeros(TOFCHMAX+1)
    B2 = np.zeros(TOFCHMAX+1)
    # B0[0] will be unused, equal to zero. (analog for B1[0], B2[0])

    try:
        with open(filename, 'r') as f:
            for i in range(TOFCHMIN - 1, TOFCHMAX):  # 0-based index
                line = f.readline()
                if not line:
                    break
                parts = line.strip().split()
                if len(parts) < 6:
                    continue
                ch = int(parts[0])
                B0[ch] = float(parts[2])
                B1[ch] = float(parts[3])
                B2[ch] = float(parts[4])
    except IOError:
        raise IOError(f"Error while opening bparams `{filename}` please verify the file and if you have network access.")

    return B0, B1, B2

def load_tof_file(filename: str) -> tuple[float, float]:
    """
    Opens a `Tof.in` file and returns the TOF calibration data.
    Returns (ns_ch, t_offs)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Could not find `tof` file `{filename}`.")

    if not filename.split('\\')[-1].split('/')[-1] == "Tof.in":
        raise NameError(f"Unexpected name of file `{filename}`. Please follow the convention and rename this file to `Tof.in`.")

    try:
        with open(filename, 'r') as f:
            for line in f:
                if 'TOF calibration' in line:
                    myindex = line.index(':')
                    ns_ch, t_offs = map(float, line[myindex+1:].strip().split())
                    return (ns_ch, t_offs)
    except IOError:
        raise RuntimeError(f"calibration not found in `{filename}`")

def extend_flt_data(flt_data: np.array, B0, B1, B2, ns_ch, t_offs):
    """
    Extends the flt data with aditional columns (t_k, E_k) -> (t_k, t, E_k, m, m_k).
    `k` denotes that this unit is expressed per channel.
    """
    TOFCHMIN=1
    TOFCHMAX=8192


    output_data = []

    try:
        for line in flt_data:
            if len(line) < 2:
                continue
            try:
                ToFch = int(line[0])
                Ench = int(line[1])
            except ValueError:
                continue

            if TOFCHMIN <= ToFch <= TOFCHMAX:
                idx = ToFch
                ToFns = 1.0e9 * (t_offs + ns_ch * ToFch)
                Iso_amu = B0[idx] + B1[idx]*Ench + B2[idx]*Ench*Ench
                Iso_ch = int(min(8000, max(1, int(Iso_amu * 100.0 + 0.5))))
                # 80 is the maximum atomic number allowed,
                # all data greather will be clipped

                output_data.append([ToFch, ToFns, Ench, Iso_amu, Iso_ch])

        return np.asarray(output_data)

    except IOError:
        raise IOError("Error reading input file or writing output file.")


def load_flt_file(filename: str) -> np.array:
    """
    Loads an flt file and returns it columns.
    """
    # check exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"`flt` file {filename} not found.")
    
    # check extension
    ext = filename.split('.')[-1]
    if ext != "flt":
        raise NameError(f"`{filename}` has the wrong extension. Expected `flt`, got `{ext}`.")

    # Load file
    with open(filename, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    if len(lines) == 0:
        raise RuntimeError()
    return np.asarray([[int(val) for val in line.split(' ')[:-1]] for line in lines[:-1]]) # ignore space at end of line and empty line at end of file


def load_extended_file(filename: str) -> np.array:
    """
    Loads an .ext file and returns its columns as a numpy array.
    
    [
        [t_k, t, E_k, m, m_k],
        ...
    ]
    `k` denotes that this unit is expressed per channel.
    """
    # check exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Extended file {filename} not found.")
    
    # check extension
    ext = filename.split('.')[-1]
    if ext != "ext":
        raise NameError(f"`{filename}` has the wrong extension. Expected `ext`, got `{ext}`.")
    
    # Load file
    with open(filename, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    return np.asarray([[float(val) for val in line.split(' ')[:-1]] for line in lines[:-1]]) # ignore space at end of line and empty line at end of file


def dump_extended_file(data: np.array, filename: str) -> None:
    """
    TODO: unit tests
    Dumps the data into an extended file.

    [
        [t_k, t, E_k, m, m_k],
        ...
    ]
    `k` denotes that this unit is expressed per channel.
    """

    # check extension
    ext = filename.split('.')[-1]
    if ext != "ext":
        raise NameError(f"`{filename}` has the wrong extension. Expected `ext`, got `{ext}`.")

    dump_dataframe(data)

def dump_dataframe(data: np.array, filename: str) -> None:
    # check extension
    lines = [' '.join(str(number) for number in line) + ' ' for line in data] # original format has space at end of file
    with open(filename, 'w') as f:
        f.write(
            '\n'.join(lines)
        )