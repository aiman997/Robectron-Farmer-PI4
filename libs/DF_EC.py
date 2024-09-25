import os
import sys
import time

_kvalue = 1.0
_kvalueLow = 1.0
_kvalueHigh = 1.0
_voltage = 0.0
_temperature = 25.0

class DFRobot_EC():
    def __init__(self):
        # Define the path to store ecdata.txt in the data directory
        self.ecdata_file = os.path.join('data', 'ecdata.txt')
        
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)

    def begin(self):
        global _kvalueLow
        global _kvalueHigh

        # Check if the file exists, if not create it with default values
        if not os.path.exists(self.ecdata_file):
            print(f"{self.ecdata_file} not found. Creating file with default values.")
            with open(self.ecdata_file, 'w') as f:
                f.write("kvalueLow=1.0\n")
                f.write("kvalueHigh=1.0\n")
        try:
            with open(self.ecdata_file, 'r') as f:
                kvalueLowLine = f.readline().strip('kvalueLow=')
                _kvalueLow = float(kvalueLowLine)
                kvalueHighLine = f.readline().strip('kvalueHigh=')
                _kvalueHigh = float(kvalueHighLine)
        except Exception as e:
            print(f"{self.ecdata_file} ERROR ! {e}. Please run DFRobot_EC_Reset")
            sys.exit(1)

    def readEC(self, voltage, temperature):
        """Read and calculate EC value."""
        global _kvalueLow
        global _kvalueHigh
        global _kvalue
        rawEC = 1000 * voltage / 820.0 / 200.0
        valueTemp = rawEC * _kvalue
        if valueTemp > 2.5:
            _kvalue = _kvalueHigh
        elif valueTemp < 2.0:
            _kvalue = _kvalueLow
        value = rawEC * _kvalue
        value = value / (1.0 + 0.0185 * (temperature - 25.0))
        return value

    def calibration(self, voltage, temperature):
        rawEC = 1000 * voltage / 820.0 / 200.0
        if 0.9 < rawEC < 1.9:
            compECsolution = 1.413 * (1.0 + 0.0185 * (temperature - 25.0))
            KValueTemp = 820.0 * 200.0 * compECsolution / 1000.0 / voltage
            print(f">>> Buffer Solution: 1.413 us/cm")
            with open(self.ecdata_file, 'r+') as f:
                flist = f.readlines()
                flist[0] = 'kvalueLow=' + str(KValueTemp) + '\n'
                f.seek(0)
                f.writelines(flist)
            print(">>> EC: 1.413 us/cm Calibration completed.")
        elif 9 < rawEC < 16.8:
            compECsolution = 12.88 * (1.0 + 0.0185 * (temperature - 25.0))
            KValueTemp = 820.0 * 200.0 * compECsolution / 1000.0 / voltage
            print(f">>> Buffer Solution: 12.88 ms/cm")
            with open(self.ecdata_file, 'r+') as f:
                flist = f.readlines()
                flist[1] = 'kvalueHigh=' + str(KValueTemp) + '\n'
                f.seek(0)
                f.writelines(flist)
            print(">>> EC: 12.88 ms/cm Calibration completed.")
        else:
            print(">>> Buffer Solution Error. Try again.")

    def reset(self):
        """Reset EC values to default."""
        global _kvalueLow, _kvalueHigh
        _kvalueLow = 1.0
        _kvalueHigh = 1.0
        try:
            with open(self.ecdata_file, 'r+') as f:
                flist = f.readlines()
                flist[0] = 'kvalueLow=' + str(_kvalueLow) + '\n'
                flist[1] = 'kvalueHigh=' + str(_kvalueHigh) + '\n'
                f.seek(0)
                f.writelines(flist)
            print(">>> Reset to default parameters <<<")
        except:
            with open(self.ecdata_file, 'w') as f:
                f.write('kvalueLow=1.0\n')
                f.write('kvalueHigh=1.0\n')
            print(">>> Reset to default parameters <<<")
