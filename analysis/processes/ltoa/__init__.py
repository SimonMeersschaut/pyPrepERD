import struct
import os

# Constants (same as in the original C code)
MAX_NADC = 16
ADC_SIZE = 2  # bytes per ADC value
NFBYTES = 1048576  # 1 MB
MAXEVENT = 1000000


class LtoaParser:
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
    
    def parse(self):
        output = []

        nadc_length = self.nadc
        active = [False] * MAX_NADC
        printarray = [0] * MAX_NADC
        event = [0] * MAX_NADC

        while datafile_read_event(self, event, active):
            j = 0
            for i in range(nadc_length):
                if active[i]:
                    printarray[i] = event[j]
                    j += 1
                else:
                    printarray[i] = 0
            
            if printarray[nadc_length - 1] != 0:
                output.append(" ".join(map(str, printarray[:nadc_length])))

        self.close()
        
        return output
    
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


def nactive_adc(w, active):
    n = 0
    for j in range(len(active)):
        if w & (1 << j):
            active[j] = True
            n += 1
        else:
            active[j] = False
    return n


def datafile_read_event(df, event, active):
    while True:
        dw_bytes = df.nextbytes(4)
        if len(dw_bytes) < 4:
            return False

        dw = struct.unpack("<I", dw_bytes)[0]
        hw = dw >> 16
        lw = dw & 0xFFFF

        if dw == 0xFFFFFFFF:
            continue  # Sync event
        elif hw == 0x4000:
            df.ntimer += 1
        else:
            n = nactive_adc(lw, active)
            if dw & 0x10000000:
                rtc_bytes = df.nextbytes(6)
                if len(rtc_bytes) < 6:
                    return False
                df.nrtc += 1
            if dw & 0x80000000:
                dummy = df.nextbytes(2)
                if len(dummy) < 2:
                    return False
                if not (hw & 0x8000):
                    df.nerrors += 1
            adc_bytes = df.nextbytes(n * ADC_SIZE)
            if len(adc_bytes) < n * ADC_SIZE:
                return False
            for i in range(n):
                event[i] = struct.unpack_from("<H", adc_bytes, i * 2)[0]
            df.nevents += 1
            return True