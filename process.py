import glob
import analysis
from gui.plot import Plot
import utils

WORK_DIR = "\\\\winbe.imec.be\\wasp\\ruthelde\\Simon\\test"


def main():
    flt_files = glob.glob(WORK_DIR + "/*.flt")

    for flt_file in flt_files:
        flt_data = analysis.load_flt_file(flt_file)
        ns_ch, t_offs = analysis.load_tof_file(WORK_DIR+"/Tof.in")
        B0, B1, B2 = analysis.load_bparams_file(WORK_DIR+"/Bparams.txt")
        extended_data = analysis.extend_flt_data(flt_data, B0, B1, B2, ns_ch, t_offs)

        pixels = utils.create_grid(extended_data, x_index=1, y_index=2)
        plot = Plot(pixels, "Project Graph")
        plot.save(flt_file.replace(".flt", ".evt.png"))

        pixels = utils.create_grid(extended_data, x_index=1, y_index=4)
        plot = Plot(pixels, "Project Graph")
        plot.save(flt_file.replace(".flt", ".mvt.png"))


if __name__ == "__main__":
    main()