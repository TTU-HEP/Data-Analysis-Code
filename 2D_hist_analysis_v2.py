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
#file = ROOT.TFile("/home/gvetters/CaloX_Work/ROOT_code/GV_code/pi+_hists/sim_data2_pi+.root", "READ")
file = ROOT.TFile("/home/gvetters/CaloX_Work/ROOT_code/GV_code/pi+_hists/uw/sim_data_uw1_pi+.root", "READ")

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
            print("weights = ", weights[j-1])
        
        # Calculate the weighted mean for this x-axis slice
        if np.sum(weights) != 0:
            weighted_avg_y = np.average(y_values, weights=weights)
        else:
            weighted_avg_y = 0  # Handle cases where the sum of weights is zero
        
        # Store the weighted average in the numpy array
        x_slices_weighted_avg[i-1] = weighted_avg_y

    if hist.GetNbinsX() > 100:
        for i in np.arange(0, len(x_slices_weighted_avg), 10):
            print("slices of z_bin data (in groups of 10) =", x_slices_weighted_avg[i], "located at bin #", i)
    else:
        for i in np.arange(0, len(x_slices_weighted_avg), 1):
            print("slices =", x_slices_weighted_avg[i], "located at bin #", i)

    # Plotting
    z_bin = np.arange(1, hist.GetNbinsX() + 1)
    plt.plot(z_bin, x_slices_weighted_avg, linestyle='-', marker='o', color='blue')
    plt.title(config["title"])
    plt.xlabel(config["xlabel"])
    plt.ylabel(config["ylabel"])
    
    if hist.GetNbinsX() > 100:
        plt.xticks(np.arange(0, hist.GetNbinsX() + 1, step=10))
    else:
        plt.xticks(np.arange(0, hist.GetNbinsX() + 1, step=1))
        
    plt.show()

hist_names =  ["h5", "h6", "h9", "h10", "h11", "h12"] 
for hist_name in hist_names:
    analyze_histogram(hist_name)


#                h5     h6   *h9   *h10   h11    h12
x1 = np.array([140.0, 140.0, 14.0, 14.0, 140.0, 140.0])
x2 = np.array([220.0, 220.0, 20.0, 20.0, 220.0, 220.0])
y1 = np.array([17.94, 17.39, 8.86, 8.82, 7.71, 7.73])
y2 = np.array([15.44, 15.72, 9.21, 9.12, 9.54, 9.65])

for num in x1, x2, y1, y2:
    slope=-(y2-y1)*16.0/((x2-x1)*125.0)
    print("slope=",slope)

    theta=np.arctan(slope)*180.0/np.pi
    
for name, angle in zip(hist_names, theta):
    print(f"Histogram: {name}, Theta: {angle:.2f} degrees")


'''
slope= [ 0.004       0.002672   -0.00746667 -0.0064     -0.002928   -0.003072  ]
Histogram: h5, Theta: 0.23 degrees
Histogram: h6, Theta: 0.15 degrees
Histogram: h9, Theta: -0.43 degrees
Histogram: h10, Theta: -0.37 degrees
Histogram: h11, Theta: -0.17 degrees
Histogram: h12, Theta: -0.18 degrees
'''