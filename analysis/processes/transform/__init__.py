import os
import sys
import numpy as np

class TransformProcess():
    ...

def read_bparams(filename, tofchmin=1, tofchmax=8192):
    """
    filename: bparams (B0, B1, B2)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Bparam file {filename} not found.")
    B0 = np.zeros(tofchmax+1)
    B1 = np.zeros(tofchmax+1)
    B2 = np.zeros(tofchmax+1)
    # B0[0] will be unused, equal to zero. (analog for B1, B2)

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
        print("error opening Bparams.txt")
        print("  please verify if it was copied by _set_params.bat")
        print("  if not, check if you have network access")
        sys.exit(1)

    return B0, B1, B2

def read_tof_calibration(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Could not find tof file `{filename}`.")
    try:
        with open(filename, 'r') as f:
            for line in f:
                if 'TOF calibration' in line:
                    myindex = line.index(':')
                    ns_ch, t_offs = map(float, line[myindex+1:].strip().split())
                    print(f"      ns_ch : {ns_ch:11.4e}    t_offs : {t_offs:11.4e}")
                    return ns_ch, t_offs
    except IOError:
        pass
    
    raise RuntimeError("calibration not found in tof.in")

def process_file(input_filename, output_filename, B0, B1, B2, ns_ch, t_offs, tofchmin=1, tofchmax=8192):
    nrlines = 0
    effnrlines = 0

    try:
        with open(input_filename, 'r') as fin, open(output_filename, 'w') as fout:
            for line in fin:
                nrlines += 1
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                try:
                    ToFch = int(parts[0])
                    Ench = int(parts[1])
                except ValueError:
                    continue

                if tofchmin <= ToFch <= tofchmax:
                    idx = ToFch
                    ToFns = 1.0e9 * (t_offs + ns_ch * ToFch)
                    Iso_amu = B0[idx] + B1[idx]*Ench + B2[idx]*Ench*Ench
                    Iso_ch = int(min(8000, max(1, int(Iso_amu * 100.0 + 0.5))))
                    # 80 is the maximum atomic number allowed,
                    # all data greather will be clipped

                    fout.write(f"{ToFch:7d} {ToFns:12.3f} {Ench:7d} {Iso_amu:11.4f} {Iso_ch:7d}\n")
                    effnrlines += 1

    except IOError:
        print("Error reading input file or writing output file.")
        sys.exit(1)

    print(f"{nrlines} nrlines have been read")
    print("    mass artificially limited min 0.02 - max 99 amu")
    print(f"{effnrlines} effective lines written between TOFchmin and TOFchmax\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ApplyTransformation.py <input_filename>")
        sys.exit(1)

    input_filename = sys.argv[1]
    tofchmin = 1
    tofchmax = 8192

    B0, B1, B2 = read_bparams("Bparams.txt", tofchmin, tofchmax)
    ns_ch, t_offs = read_tof_calibration("tof.in")
    process_file(input_filename, B0, B1, B2, ns_ch, t_offs, tofchmin, tofchmax)

if __name__ == "__main__":
    main()
