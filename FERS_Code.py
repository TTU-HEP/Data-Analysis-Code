import ROOT
import numpy as np
#import matplotlib.pyplot as plt

# Open the ROOT file
file = ROOT.TFile("/home/gvetters/CaloX_Work/data-files/run749_4500.root", "READ")
output_file = ROOT.TFile("FERS_run3.root", "RECREATE")

# Get the tree from the file
tree = file.Get("EventTree")

# Loop over the entries in the tree
cnt = 0

#Define dictionaries for FERS and 1D Histograms
df = {} 
h1 = {}

channel_map = {
    0: 3, 1: 1, 2: 2, 3: 0,
    4: 7, 5: 5, 6: 6, 7: 4,
    8: 9, 9: 11, 10: 8, 11: 10,
    12: 13, 13: 15, 14: 12, 15: 14,
    16: 19, 17: 17, 18: 18, 19: 16,
    20: 23, 21: 21, 22: 22, 23: 20,
    24: 25, 25: 27, 26: 24, 27: 26,
    28: 29, 29: 31, 30: 28, 31: 30,
    32: 35, 33: 33, 34: 34, 35: 32,
    36: 39, 37: 37, 38: 38, 39: 36,
    40: 41, 41: 43, 42: 40, 43: 42,
    44: 45, 45: 47, 46: 44, 47: 46,
    48: 51, 49: 49, 50: 50, 51: 48,
    52: 55, 53: 53, 54: 54, 55: 52,
    56: 57, 57: 59, 58: 56, 59: 58,
    60: 61, 61: 63, 62: 60, 63: 62
}

def get_data(entry):
    global df
    df["hg1"] = np.array(entry.FERS_Board1_energyHG)
    

def book_hist():
    global h1, df
    for k in df.keys():
        for ch in np.arange(64):
            s = k + "_" + str(ch)
            h1[s] = ROOT.TH1D(s, "FERS Board "+s+";Energy(ADC);Count", 100, 0, 7999)


for entry in tree:
    if cnt > 4500:  #change value to loop over a certain amount of entries.
        break
    cnt += 1
    get_data(entry)
    if len(h1) == 0:
        book_hist()
        #print(len(df["hg1"]))
    for k in df.keys():
        for ch in np.arange(64):
            if df[k][ch] < 8000:
                s = k + "_" + str(ch)
                h1[s].Fill(df[k][ch])

            #Handle overflow: add the overflow to the last bin
            overflow_bin = h1[s].GetNbinsX() + 1
            last_bin = h1[s].GetNbinsX()
            overflow_content = h1[s].GetBinContent(overflow_bin)
            last_bin_content = h1[s].GetBinContent(last_bin)
            h1[s].SetBinContent(last_bin, last_bin_content + overflow_content)
            #h1[s].SetBinContent(overflow_bin, 0)  # Optionally clear the overflow bin

# Create a multi-page PDF
output_pdf = "FERS_output_histograms4.pdf"

# Open the PDF file
c = ROOT.TCanvas("c", "Canvas", 3400, 4400)
c.Print(f"{output_pdf}[")

# Sort histograms based on channel_map
sorted_keys = sorted(h1.keys(), key=lambda k: channel_map[int(k.split('_')[1])])

# Create canvases and draw histograms
hist_count = 0
total_histograms = len(sorted_keys)
max_histograms_per_page = 32  # Number of histograms per page

while hist_count < total_histograms:
    c.Clear()
    c.Divide(4, 8)
    
    for pad_num in range(1, 33):  # 32 pads (4x8 grid)
        if hist_count < total_histograms:
            hist_key = sorted_keys[hist_count]
            hist = h1[hist_key]
            c.cd(pad_num)
            ROOT.gPad.SetLogy()
            hist.Draw()
            hist_count += 1

    # Print the current canvas page
    c.Print(f"{output_pdf}")

# Finalize the PDF
c.Print(f"{output_pdf}]")

# Save histograms to the output ROOT file
output_file.Write()
output_file.Close()

# Close the input file
file.Close()