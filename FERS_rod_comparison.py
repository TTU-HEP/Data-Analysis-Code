import ROOT
import numpy as np

# Function to get data from the tree
def get_data(entry):
    df["hg1"] = np.array(entry.FERS_Board1_energyHG)

# Function to book 2D histograms
def book_hist(selected_channel, correlated_channel):
    global h2
    k1 = "hg1"
    
    # Sort the channel numbers to avoid duplicates
    ch1, ch2 = sorted([selected_channel, correlated_channel])
    
    s1 = f"{k1}_{ch1}"
    s2 = f"{k1}_{ch2}"
    s = f"{s1}_vs_{s2}"

    if s in h2:
        hist = h2[s]
        if hist.GetListOfFunctions().FindObject("stats"):
            stats = hist.GetListOfFunctions().FindObject("stats")
            stats.SetX1NDC(0.7)  # Move the legend to the right
            stats.SetX2NDC(0.9)
            stats.SetY1NDC(0.7)  # Move the legend to the top
            stats.SetY2NDC(0.9)

    # Book the histogram if it doesn't exist
    if s not in h2:
        h2[s] = ROOT.TH2D(s, f"FERS Board Comparison {s1} vs {s2};{s1};{s2}", 100, 300, 2000, 100, 300, 2000)
        print(f"Booked histogram: {s}")
    return s

# Function to generate 2D histograms based on specified pairs
def generate_2D_histograms(tree):
    # Define pairs to compare based on the 4x2 groups
    pairs = []
    for group_start in range(0, 64, 8):  # Start each group at multiples of 8 (0, 8, 16, ..., 56)
        for i in range(4):  # Compare the first 4 channels in each group with the next 4 channels
            pairs.append((group_start + i, group_start + i + 4))

    # Loop over the entries in the tree
    cnt = 0
    for entry in tree:
        if cnt > 4500:  # Change value to loop over a certain amount of entries.
            break
        cnt += 1
        get_data(entry)
        
        for selected_channel, correlated_channel in pairs:
            # Book and get the histogram name
            s = book_hist(selected_channel, correlated_channel)
            
            # Apply the cut: Include only events where both values are less than 2000 and greater than 300
            if df["hg1"][selected_channel] < 2000 and df["hg1"][correlated_channel] < 2000:
                if df["hg1"][selected_channel] > 300 and df["hg1"][correlated_channel] > 300:
                    h2[s].Fill(df["hg1"][selected_channel], df["hg1"][correlated_channel])
                    #print(f"Filled histogram: {s} with values ({df['hg1'][selected_channel]}, {df['hg1'][correlated_channel]})")

# Main function to execute the workflow
def main():
    file = ROOT.TFile(file_path, "READ")
    tree = file.Get("EventTree")
    output_file = ROOT.TFile("FERS_rod_comparison_run2.root", "RECREATE")
    c = ROOT.TCanvas("c", "Canvas", 1200, 900)

    generate_2D_histograms(tree)

    # PDF output
    output_pdf = "FERS_2D_output_rod_histograms_run2.pdf"
    c.Print(f"{output_pdf}[")  # Open the PDF

    for k in h2.keys():
        if h2[k].GetEntries() > 0:
            c.Clear()  # Clear the canvas before drawing a new histogram
            h2[k].Draw("COLZ")
            c.Update()
            c.Print(output_pdf)  # Print the current canvas to the PDF

    c.Print(f"{output_pdf}]")  # Close the PDF

    output_file.Write()
    output_file.Close()
    file.Close()

# Global variables
file_path = "/home/gvetters/CaloX_Work/data-files/run749_4500.root"
df = {} 
h2 = {}

if __name__ == "__main__":
    main()