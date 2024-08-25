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

# Function to calculate correlation coefficients and save high correlations
def calculate_correlations(tree, total_channels):
    high_correlations = []
    for selected_channel in range(total_channels):
        for channel in range(selected_channel + 1, total_channels):  # Start from selected_channel + 1
            hist2D = ROOT.TH2D(f"hist2D_{selected_channel}_{channel}",
                               f"FERS Board 1 - Channel {selected_channel} vs Channel {channel};Ch{selected_channel};Ch{channel}",
                               100, 300, 2000, 100, 300, 2000)
            expression = f"FERS_Board1_energyHG[{selected_channel}]:FERS_Board1_energyHG[{channel}]>>{hist2D.GetName()}"
            tree.Draw(expression, "", "goff", 22000)

            # Calculate the correlation coefficient
            correlation_coefficient = hist2D.GetCorrelationFactor()

            if correlation_coefficient > 0.8:
                high_correlations.append((selected_channel, channel, correlation_coefficient))

            del hist2D

    # Convert the list to a numpy array and save it
    high_correlations_array = np.array(high_correlations, dtype=[('selected_channel', int), ('channel', int), ('correlation_coefficient', float)])
    np.save("high_correlations.npy", high_correlations_array)
    print(f"High correlation coefficients saved to 'high_correlations.npy'.")
    print(f"Number of high correlations: {len(high_correlations_array)}")
# Function to generate 2D histograms for high correlation pairs
def generate_2D_histograms(tree):
    # Load the high correlation pairs
    high_correlations_array = np.load("high_correlations.npy")
    
    # Loop over the entries in the tree
    cnt = 0
    for entry in tree:
        if cnt > 22000:  # Change value to loop over a certain amount of entries.
            break
        cnt += 1
        get_data(entry)
        
        for correlation in high_correlations_array:
            selected_channel = correlation['selected_channel']
            correlated_channel = correlation['channel']
            
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
    output_file = ROOT.TFile("FERS_Comparison_run3.root", "RECREATE")
    c = ROOT.TCanvas("c", "Canvas", 1200, 900)

    calculate_correlations(tree, 64)
    generate_2D_histograms(tree)

    # PDF output
    output_pdf = "FERS_2D_output_histograms_run3.pdf"
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
file_path = "/home/gvetters/CaloX_Work/data-files/run742_V22000.root"
df = {} 
h2 = {}

if __name__ == "__main__":
    main()