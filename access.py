#Michael O'Donnell
#8/8/2024
#General ROOT to Histogram access code

import ROOT

# Open the ROOT file
file = ROOT.TFile("/home/michaelod/CaloXWork/datafiles/run742_V22000.root", "READ")

# Get the tree from the file
tree = file.Get("EventTree")

# Number of channels
num_channels = 3

# Create histograms
hist1D_dict = {}
hist2D_dict = {}

for ch in range(num_channels):
    # Create 1D histogram for each channel
    hist1D_dict[ch] = ROOT.TH1F(f"hist1D_{ch}", f"FERS Board 1 Channel {ch};Energy HG;Counts", 100, 0, 1000)
    
    # Create 2D histograms for each pair of channels
    for ch2 in range(ch + 1, num_channels):
        hist2D_dict[(ch, ch2)] = ROOT.TH2F(f"hist2D_{ch}_{ch2}", f"FERS Board 1;Ch{ch};Ch{ch2}", 100, 0, 1000, 100, 0, 1000)

# Print number of entries
print(tree.GetEntries())

# Loop over the entries in the tree
cnt = 0

for entry in tree:
    if cnt >= 100: # Process only 100 events
        break
    cnt += 1
    
    for ch in range(num_channels):
        hist1D_dict[ch].Fill(entry.FERS_Board1_energyHG[ch])
    
    for ch1 in range(num_channels):
        for ch2 in range(ch1 + 1, num_channels):
            hist2D_dict[(ch1, ch2)].Fill(entry.FERS_Board1_energyHG[ch1], entry.FERS_Board1_energyHG[ch2])

# Create a new ROOT file to save histograms
output_file = ROOT.TFile("histograms.root", "RECREATE")

# Write histograms to the file
for hist in hist1D_dict.values():
    hist.Write()

for hist in hist2D_dict.values():
    hist.Write()

# Close the output file
output_file.Close()

# Create a canvas to draw histograms
canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)

# Draw 1D histograms
for ch in range(num_channels):
    canvas.Clear()
    hist1D_dict[ch].Draw()
    canvas.SaveAs(f"hist1D_{ch}.pdf")
    canvas.SaveAs(f"hist1D_{ch}.png")

# Draw 2D histograms
for (ch1, ch2) in hist2D_dict.keys():
    canvas.Clear()
    hist2D_dict[(ch1, ch2)].Draw("COLZ")
    canvas.SaveAs(f"hist2D_{ch1}_{ch2}.pdf")
    canvas.SaveAs(f"hist2D_{ch1}_{ch2}.png")

# Close the input file
file.Close()

#end
