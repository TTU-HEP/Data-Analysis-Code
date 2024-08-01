import ROOT
import numpy as np

# Open the ROOT file
file = ROOT.TFile("/home/gvetters/CaloX_Work/data-files/run742_V22000.root", "READ")
output_file = ROOT.TFile("test.root", "RECREATE")

# Get the tree from the file
tree = file.Get("EventTree")

# Loop over the entries in the tree
cnt = 0

#Define dictionaries for FERS, DRS, and 1D Histograms
dfdrs = {}
h1 = {}

def get_data(entry):
    global dfdrs
    dfdrs["drs_000"] = np.array(entry.DRS_Board0_Group0_Channel0)
    dfdrs["drs_001"] = np.array(entry.DRS_Board0_Group0_Channel1)
    dfdrs["drs_002"] = np.array(entry.DRS_Board0_Group0_Channel2)
    dfdrs["drs_003"] = np.array(entry.DRS_Board0_Group0_Channel3)

def book_hist():
    global h1, dfdrs
    for k in dfdrs.keys():
        for ch in np.arange(64):
            s = k + "_" + str(ch)
            h1[s] = ROOT.TH1D(s, "DRS "+s+";Energy;Count", 100, 0, 1000)

for entry in tree:
    if cnt > 1000:  # Process only 1000 events
        break
    cnt += 1
    get_data(entry)
    if len(h1) == 0:
        book_hist()
    for k in dfdrs.keys():
        for ch in np.arange(64):
            s = k + "_" + str(ch)
            h1[s].Fill(dfdrs[k][ch])

# Create a multi-page PDF
output_pdf = "DRS_output_histograms.pdf"

# Open the PDF file
c = ROOT.TCanvas("c", "Canvas", 1200, 900)
c.Print(f"{output_pdf}[")

# Create canvases and draw histograms
canvas_num = 1
hist_count = 0

for i, (key, hist) in enumerate(h1.items()):
    if hist_count % 16 == 0:  # New canvas every 16 histograms
        c.Clear()
        c.Divide(4, 4)
    
    pad_num = (hist_count % 16) + 1
    c.cd(pad_num)
    ROOT.gPad.SetLogy()
    hist.Draw()
    
    if pad_num == 16 or i == len(h1) - 1:  # If it's the last pad or the last histogram
        c.Print(f"{output_pdf}")  # Print the current canvas page
    
    hist_count += 1

# Close the PDF file
c.Print(f"{output_pdf}]")

# Save histograms to the output ROOT file
output_file.Write()
output_file.Close()

# Close the input file
file.Close()