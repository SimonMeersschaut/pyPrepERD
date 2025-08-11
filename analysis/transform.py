import numpy as np
import os

# public functions

def load_bparams_file(filename: str) -> np.array:
    """
    Opens the bparams file and parses the contents into a numpy array.
    filename: bparams (B0, B1, B2)
    """

    tofchmin=1
    tofchmax=8192

    # check exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Bparam file {filename} not found.")
    
    # check extension
    ext = filename.split('.')[-1]
    if ext != "txt":
        raise NameError(f"`{filename}` has the wrong extension. Expected `txt`, got `{ext}`.")
    
    # parse file
    
    B0 = np.zeros(tofchmax+1)
    B1 = np.zeros(tofchmax+1)
    B2 = np.zeros(tofchmax+1)
    # B0[0] will be unused, equal to zero. (analog for B1[0], B2[0])

    try:
        with open(filename, 'r') as f:
            for i in range(tofchmin - 1, tofchmax):  # 0-based index
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
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Could not find tof file `{filename}`.")

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
        raise RuntimeError("calibration not found in tof.in")

def extend_flt_data(flt_data: np.array, B0, B1, B2, ns_ch, t_offs):
    """
    Extends the flt data with aditional columns (t_k, E_k) -> (t_k, t, E_k, m, m_k).
    `k` denotes that this unit is expressed per channel.
    """
    tofchmin=1
    tofchmax=8192

    nrlines = 0
    effnrlines = 0

    output_data = np.zeros((len(flt_data), 5))

    try:
        for index, line in enumerate(flt_data):
            nrlines += 1
            # parts = line.strip().split()
            if len(line) < 2:
                continue
            try:
                ToFch = int(line[0])
                Ench = int(line[1])
            except ValueError:
                continue

            if tofchmin <= ToFch <= tofchmax:
                idx = ToFch
                ToFns = 1.0e9 * (t_offs + ns_ch * ToFch)
                Iso_amu = B0[idx] + B1[idx]*Ench + B2[idx]*Ench*Ench
                Iso_ch = int(min(8000, max(1, int(Iso_amu * 100.0 + 0.5))))
                # 80 is the maximum atomic number allowed,
                # all data greather will be clipped

                output_data[index] = [ToFch, ToFns, Ench, Iso_amu, Iso_ch]
                # fout.write(f"{ToFch:7d} {ToFns:12.3f} {Ench:7d} {Iso_amu:11.4f} {Iso_ch:7d}\n")
                effnrlines += 1

        return output_data

    except IOError:
        raise IOError("Error reading input file or writing output file.")


def load_flt_file(filename: str) -> np.array:
    """
    """
    # check exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Bparam file {filename} not found.")
    
    # check extension
    ext = filename.split('.')[-1]
    if ext != "flt":
        raise NameError(f"`{filename}` has the wrong extension. Expected `flt`, got `{ext}`.")

    # Load file
    with open(filename, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    return np.asarray([[int(val) for val in line.split(' ')[:-1]] for line in lines[:-1]]) # ignore space at end of line and empty line at end of file
