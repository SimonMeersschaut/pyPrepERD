import struct
import os
import numpy as np

# public functions

def load_lst_file(filename: str) -> np.array:
    """
    Opens `filename`, reads the contents and parses the
    binary data to a numpy array with the following dimensions:
    [
        (time_k, energy_k),
        ...
    ].
    `k` denotes that this unit is expressed per channel.
    """
    # check file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"lst file `{filename}` was not found.")

    # check extension
    ext = filename.split('.')[-1]
    if ext != "lst":
        raise NameError(f"`{filename}` has the wrong extension. Expected `lst`, got `{ext}`.")

    p = LtoaProcess(filename)
    return p.run()


def dump_flt_file(data: np.array, filename: str) -> None:
    """
    Dumps the data into a flt file in a character-seperated format (analog to csv).
    The data is seperated by a space.

    For backwards compatability, we chose to add a space at the end of each line,
    together with a white line at the end of the file.
    """

    ext = filename.split('.')[-1]
    if ext != "flt":
        raise NameError(f"`{filename}` has the wrong extension. Expected `flt`, got `{ext}`.")

    y = data.shape[1]
    if not y == 2:
        raise ValueError(f"Shape of `data` is incompatible. Expected shape=(n, 2), got shape(n, {y}).")
    
    # save array into csv file
    rows = ["{} {} ".format(i, j) for i, j in data] + [""]
    text = "\n".join(rows)

    with open(filename, 'w') as f:
        f.write(text)


# helper functions


# Constants (same as in the original C code)
MAX_NADC = 16
ADC_SIZE = 2  # bytes per ADC value
NFBYTES = 1048576  # 1 MB
MAXEVENT = 1000000


class LtoaProcess:
    
    def __init__(self, fname):
        if not os.path.exists(fname):
            raise FileNotFoundError(f"{fname} was not found.")
        
        self.fname = fname
        self.fp = open(fname, "rb") if fname else os.fdopen(0, "rb")
        self.fbytes = self.fp.read(NFBYTES)
        self.fbi = 0  # index into fbytes
        self.nfbytes = len(self.fbytes)
        self.nevents = 0
        self.nerrors = 0
        self.ntimer = 0
        self.nrtc = 0
        self.nadc = 2  # fixed value from C code

        self.skip_header()
    
    def run(self) -> np.array:
        output = []

        nadc_length = self.nadc
        active = [False] * MAX_NADC
        printarray = [0] * MAX_NADC
        event = [0] * MAX_NADC

        while self.datafile_read_event(event, active):
            j = 0
            for i in range(nadc_length):
                if active[i]:
                    printarray[i] = event[j]
                    j += 1
                else:
                    printarray[i] = 0
            
            if printarray[nadc_length - 1] != 0:
                output.append(printarray[:nadc_length])

        self.close()
        
        return np.asarray(output, dtype=np.uint16)
    
    def skip_header(self):
        wordlen = 10
        word = bytearray(self.nextbytes(wordlen))
        while word.decode(errors='ignore') != "[LISTDATA]":
            word = word[1:] + self.nextbytes(1)
            if len(word) != wordlen:
                raise ValueError(f"Can't find beginning of listdata in file '{self.fname}'")
        self.nextbytes(2)  # skip linebreak

    def nextbytes(self, size):
        buffer = bytearray()
        while len(buffer) < size:
            if self.fbi < self.nfbytes:
                take = min(size - len(buffer), self.nfbytes - self.fbi)
                buffer += self.fbytes[self.fbi:self.fbi + take]
                self.fbi += take
            else:
                read_data = self.fp.read(size - len(buffer))
                if not read_data:
                    break
                buffer += read_data
        return bytes(buffer)

    def close(self):
        print(f"Read {self.nevents} events from {self.fname}")
        print(f"({self.ntimer} timer events)")
        self.fp.close()


    def nactive_adc(self, w, active):
        n = 0
        for j in range(len(active)):
            if w & (1 << j):
                active[j] = True
                n += 1
            else:
                active[j] = False
        return n


    def datafile_read_event(self, event, active):
        while True:
            dw_bytes = self.nextbytes(4)
            if len(dw_bytes) < 4:
                return False

            dw = struct.unpack("<I", dw_bytes)[0]
            hw = dw >> 16
            lw = dw & 0xFFFF

            if dw == 0xFFFFFFFF:
                continue  # Sync event
            elif hw == 0x4000:
                self.ntimer += 1
            else:
                n = self.nactive_adc(lw, active)
                if dw & 0x10000000:
                    rtc_bytes = self.nextbytes(6)
                    if len(rtc_bytes) < 6:
                        return False
                    self.nrtc += 1
                if dw & 0x80000000:
                    dummy = self.nextbytes(2)
                    if len(dummy) < 2:
                        return False
                    if not (hw & 0x8000):
                        self.nerrors += 1
                adc_bytes = self.nextbytes(n * ADC_SIZE)
                if len(adc_bytes) < n * ADC_SIZE:
                    return False
                for i in range(n):
                    event[i] = struct.unpack_from("<H", adc_bytes, i * 2)[0]
                self.nevents += 1
                return True