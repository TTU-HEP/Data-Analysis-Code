import ROOT
import numpy as np
import matplotlib.pyplot as plt

# Dictionary to store histogram configurations
hist_config = {
    "h5": {"title": "x slice average per z bin in h5 (scintillating)", "xlabel": "Bin number (in z)", "ylabel": "Slice average of x"},
    "h6": {"title": "x slice average per z bin in h6 (cherenkov)", "xlabel": "Bin number (in z)", "ylabel": "Slice average of x"},
    "h9": {"title": "y slice average per x bin in h9 (scintillating)", "xlabel": "Bin number (in x)", "ylabel": "Slice average of y"},
    "h10": {"title": "y slice average per x bin in h10 (cherenkov)", "xlabel": "Bin number (in x)", "ylabel": "Slice average of y"},
    "h11": {"title": "z slice average per y bin in h11 (scintillating)", "xlabel": "Bin number (in y)", "ylabel": "Slice average of z"},
    "h12": {"title": "z slice average per y bin in h12 (cherenkov)", "xlabel": "Bin number (in y)", "ylabel": "Slice average of z"}
}

# Open your ROOT file
file = ROOT.TFile("/home/gvetters/CaloX_Work/ROOT_code/GV_code/pi+_hists/sim_data2_pi+.root", "READ")

# Function to analyze and plot a specific histogram
def analyze_histogram(hist_name):
    hist = file.Get(hist_name)
    config = hist_config[hist_name]
    
    # Initialize numpy array to store the weighted means
    x_slices_weighted_avg = np.zeros(hist.GetNbinsX())
    
    # Loop over each bin on the x-axis
    for i in range(1, hist.GetNbinsX() + 1):
        # Initialize arrays to store y-bin contents and weights for the current x-bin
        y_values = np.zeros(hist.GetNbinsY())
        weights = np.zeros(hist.GetNbinsY())
        
        # Loop over each bin on the y-axis
        for j in range(1, hist.GetNbinsY() + 1):
            y_values[j-1] = hist.GetYaxis().GetBinCenter(j)
            weights[j-1] = hist.GetBinContent(i, j)
        
        # Calculate the weighted mean for this x-axis slice
        if np.sum(weights) != 0:
            weighted_avg_y = np.average(y_values, weights=weights)
        else:
            weighted_avg_y = 0  # Handle cases where the sum of weights is zero
        
        # Store the weighted average in the numpy array
        x_slices_weighted_avg[i-1] = weighted_avg_y
    print("slices =", x_slices_weighted_avg)

    # Plotting
    z_bin = np.arange(1, hist.GetNbinsX() + 1)
    plt.plot(z_bin, x_slices_weighted_avg, linestyle='-', marker='o', color='blue')
    plt.title(config["title"])
    plt.xlabel(config["xlabel"])
    plt.ylabel(config["ylabel"])
    plt.xticks(np.arange(1, hist.GetNbinsX() + 1, step=1))
    plt.show()

hist_names =  ["h5", "h6", "h9", "h10", "h11", "h12"] 
for hist_name in hist_names:
    analyze_histogram(hist_name)

x1 = np.array([11.0, 11.0, 14.0, 14.0, 11.0, 11.0])
x2 = np.array([18.0, 18.0, 20.0, 20.0, 18.0, 18.0])
y1 = np.array([17.53, 17.83, 8.23, 8.20, 7.20, 7.02])
y2 = np.array([15.12, 15.10, 8.67, 8.58, 9.02, 9.02])

for num in x1, x2, y1, y2:
    slope=-(y2-y1)*16.0/((x2-x1)*125.0)
    print("slope=",slope)

    theta=np.arctan(slope)*180.0/np.pi
    
for name, angle in zip(hist_names, theta):
    print(f"Histogram: {name}, Theta: {angle:.2f} degrees")



#slopes: [ 2.52331054  2.85783298 -0.53780059 -0.46446761 -1.90610004 -2.09445508]