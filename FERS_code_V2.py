# Import ROOT and numpy
import ROOT
import numpy as np

# Open the ROOT files
file1 = ROOT.TFile("/home/gvetters/CaloX_Work/data-files/run749_4500.root", "READ")
file2 = ROOT.TFile("/home/gvetters/CaloX_Work/data-files/run742_V22000.root", "READ")
output_file = ROOT.TFile("FERS_run3.root", "RECREATE")

# Get the trees from the files
tree1 = file1.Get("EventTree")
tree2 = file2.Get("EventTree")

# Define dictionaries for histograms with unique names
h1 = {}
h2 = {}

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

# Function to fill histograms from tree entries
def get_data(entry, h_dict):
    hg1 = np.array(entry.FERS_Board1_energyHG)
    for ch in np.arange(64):
        if hg1[ch] < 8000:
            h_dict[ch].Fill(hg1[ch])

# Function to book histograms
def book_histograms(h_dict, color, file_tag):
    for ch in np.arange(64):
        hist_name = f"{file_tag}_Channel_{ch}"
        h_dict[ch] = ROOT.TH1D(hist_name, f"Channel {ch};Energy(ADC);Count", 100, 0, 8000)
        h_dict[ch].SetLineColor(color)
        h_dict[ch].SetStats(False)  # Disable default legend (stats box)

# Book histograms for both ROOT files with unique tags
book_histograms(h1, ROOT.kBlue, "File1")  # Blue for first file
book_histograms(h2, ROOT.kRed, "File2")   # Red for second file

# Loop over the entries in the first tree
cnt = 0
for entry in tree1:
    if cnt > 4500:  # Loop over a certain number of entries
        break
    cnt += 1
    get_data(entry, h1)

# Loop over the entries in the second tree
cnt = 0
for entry in tree2:
    if cnt > 4500:  # Loop over a certain number of entries
        break
    cnt += 1
    get_data(entry, h2)

# Normalize the histograms
for ch in np.arange(64):
    if h1[ch].Integral() > 0:
        h1[ch].Scale(1.0 / h1[ch].Integral())
    if h2[ch].Integral() > 0:
        h2[ch].Scale(1.0 / h2[ch].Integral())

# Create a multi-page PDF
output_pdf = "FERS_output_histograms_individual.pdf"
c = ROOT.TCanvas("c", "Canvas", 800, 600)
c.Print(f"{output_pdf}[")  # Start the PDF file

# Loop through histograms and print them individually
for ch in np.arange(64):
    c.Clear()
    ROOT.gPad.SetLogy()
    h1[ch].Draw("HIST")
    h2[ch].Draw("HIST SAME")
    
    # Create and draw the legend
    legend = ROOT.TLegend(0.6, 0.7, 0.9, 0.9)
    #legend.SetBorderSize(0)
    legend.AddEntry(h1[ch], "run_749 data", "l")
    legend.AddEntry(h2[ch], "run_742 data", "l")
    legend.Draw()
    
    # Print the current histogram to the PDF
    c.Print(f"{output_pdf}")

# Close the PDF file
c.Print(f"{output_pdf}]")

# Write all histograms to the output ROOT file
output_file.cd()
for ch in np.arange(64):
    h1[ch].Write()
    h2[ch].Write()

# Close the output file
output_file.Close()

# Close the input files
file1.Close()
file2.Close()