import ROOT
import numpy as np

# Open the ROOT file
file = ROOT.TFile("/home/gvetters/CaloX_Work/data-files/run742_V22000.root", "READ")
output_file = ROOT.TFile("test.root", "RECREATE")
c = ROOT.TCanvas("c", "Canvas", 1200, 900)

# Get the tree from the file
tree = file.Get("EventTree")

# Define dictionaries for FERS and 2D Histograms
df = {} 
h2 = {}

def get_data(entry):
    global df
    df["hg0"] = np.array(entry.FERS_Board0_energyHG)
    df["hg1"] = np.array(entry.FERS_Board1_energyHG)
    df["hg2"] = np.array(entry.FERS_Board2_energyHG)
    # Uncomment below if needed
    # df["lg0"] = np.array(entry.FERS_Board0_energyLG)
    # df["lg1"] = np.array(entry.FERS_Board1_energyLG)
    # df["lg2"] = np.array(entry.FERS_Board2_energyLG)

def book_hist():
    global h2, df
    while True:
        k1 = input("Please list a board number (Choices: hg0, hg1, hg2): ") 
        ch1 = input("Please list a channel (from 0 to 63): ")
        k2 = input("Please list a board number (Choices: hg0, hg1, hg2): ") 
        ch2 = input("Please list a channel (from 0 to 63): ")
        
        s1 = f"{k1}_{ch1}"
        s2 = f"{k2}_{ch2}"
        s = f"{s1}_vs_{s2}"

        h2[s] = ROOT.TH2D(s, f"FERS Board Comparison {s1} vs {s2}", 100, 0, 1000, 100, 0, 1000)

        print("Would you like to make another comparison plot? (y/n): ")
        ans = input().strip().lower()
        if ans != 'y':
            break

# Loop over the entries in the tree
cnt = 0
for entry in tree:
    if cnt > 22000:  #change value to loop over a certain amount of entries.
        break
    cnt += 1
    get_data(entry)
    if len(h2) == 0:
        book_hist()
    for k in h2.keys():
        s1, s2 = k.split('_vs_')
        board1, ch1 = s1.split('_')
        board2, ch2 = s2.split('_')
        h2[k].Fill(df[board1][int(ch1)], df[board2][int(ch2)])

# Create a multi-page PDF
output_pdf = "FERS_2D_output_histograms_1.pdf"

# Open the PDF file
c.Print(f"{output_pdf}[")

# Draw and save each histogram in the PDF
for k in h2.keys():
    h2[k].Draw("COLZ")
    c.Print(output_pdf)

# Close the PDF file
c.Print(f"{output_pdf}]")

# Save histograms to the output ROOT file
output_file.Write()
output_file.Close()

# Close the input file
file.Close()