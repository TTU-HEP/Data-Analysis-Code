#For Tomorrow: try to get # of entries from each bins for FERS. Try to make a plot of that to see which bins have more entries and which have less
#Use GetMaximumBin(), FindBin(), and Integral() to make this happen.
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
df = {} 
h1 = {}

def get_data(entry):
    global df
    #df["hg0"] = np.array(entry.FERS_Board0_energyHG)
    df["hg1"] = np.array(entry.FERS_Board1_energyHG)
    #df["hg2"] = np.array(entry.FERS_Board2_energyHG)

    #df["lg0"] = np.array(entry.FERS_Board0_energyLG)
    #df["lg1"] = np.array(entry.FERS_Board1_energyLG)
    #df["lg2"] = np.array(entry.FERS_Board2_energyLG)

max_bin = []
min_bin = []
Integral_bin = []

def book_hist():
    global h1, df
    for k in df.keys():
        for ch in np.arange(64):
            s = k + "_" + str(ch)
            h1[s] = ROOT.TH1D(s, "FERS Board "+s+";Energy;Count", 100, 10, 8000)


def analyze_hist(hist):
    global h1, max_bin, min_bin,integral_bin
    for hist in h1.values():
        max_bin.append(hist.GetMaximumBin())
        min_bin.append(hist.FindBin(50))
        integral_bin.append(hist.Integral(hist.FindBin(50),hist.GetMaximumBin()))

    print("maximum bin #:", max_bin, len(max_bin))
    print("minimum bin #:", min_bin, len(min_bin))


for entry in tree:
    if cnt > 22000:  #change value to loop over a certain amount of entries.
        break
    cnt += 1
    get_data(entry)
    if len(h1) == 0:
        book_hist()
    for k in df.keys():
        for ch in np.arange(64):
            s = k + "_" + str(ch)
            h1[s].Fill(df[k][ch])

            # Handle overflow: add the overflow to the last bin
            overflow_bin = h1[s].GetNbinsX() + 1
            last_bin = h1[s].GetNbinsX()
            overflow_content = h1[s].GetBinContent(overflow_bin)
            last_bin_content = h1[s].GetBinContent(last_bin)
            h1[s].SetBinContent(last_bin, last_bin_content + overflow_content)
            h1[s].SetBinContent(overflow_bin, 0)  # Optionally clear the overflow bin


# Analyze the histograms after filling them
analyze_hist(h1)

# Create a multi-page PDF
output_pdf = "FERS_output_histograms.pdf"

# Open the PDF file
c = ROOT.TCanvas("c", "Canvas", 3400, 4400)
c.Print(f"{output_pdf}[")

# Create canvases and draw histograms
canvas_num = 1
hist_count = 0

for i, (key, hist) in enumerate(h1.items()):
    if hist_count % 32 == 0:  # New canvas every 16 histograms
        c.Clear()
        c.Divide(4, 8)
    
    pad_num = (hist_count % 32) + 1
    c.cd(pad_num)
    ROOT.gPad.SetLogy()
    hist.Draw()
    
    if pad_num == 32 or i == len(h1) - 1:  # If it's the last pad or the last histogram
        c.Print(f"{output_pdf}")  # Print the current canvas page
    
    hist_count += 1

# Close the PDF file
c.Print(f"{output_pdf}]")

# Save histograms to the output ROOT file
output_file.Write()
output_file.Close()

# Close the input file
file.Close()