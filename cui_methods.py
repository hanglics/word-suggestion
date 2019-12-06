import math
import csv

nCols = 20

# read the bin file and construct the matrix
# Thanks to Jimmy
def readCuiDistance(distanceFile):
    with open(distanceFile, "rb") as fb:
        b = fb.read()
        size = int.from_bytes(b[:4], byteorder='little', signed=False)
        
        j = 4
        k = 0
        currentCui = 0
        matrix = {}
        for i in range(0, size):
            if k == 0:
                idx = int.from_bytes(b[j:j+4], byteorder='little', signed=False)
                matrix[idx] = {}
            else:
                if currentCui == 0:
                    currentCui = int.from_bytes(b[j:j+4], byteorder='little', signed=False)
                else:
                    intVal = int.from_bytes(b[j:j+4], byteorder="little", signed=False)
                    fVal = float(intVal) / math.pow(10, math.ceil(math.log10(float(intVal))))
                    matrix[idx][currentCui] = fVal
                    currentCui = 0
            k += 1
            
            if k == nCols + 1:
                k = 0
            
            j += 4
            
    return matrix

# convert the cui to int
# Thanks to Jimmy
def cui2int(CUI):
    return int(CUI.replace("C", "").replace("c", ""))

# a method to read the cui -> term csv file and construct a dict
def readCuiTitle(titleFile):
    cui2titleDict = {}
    with open(titleFile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                cui2titleDict[row[0]] = row[1]
                line_count += 1
    return cui2titleDict