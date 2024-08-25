import ROOT
import numpy as np
import matplotlib.pyplot as plt

# Open your ROOT file and retrieve the 2D histogram
file = ROOT.TFile("/home/gvetters/CaloX_Work/ROOT_code/GV_code/pi+_hists/sim_data2_pi+.root", "READ")
hist = file.Get("h5") 

# Initialize an array to store the averages
# Initialize a numpy array to store the weighted means
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

# Now x_slices_weighted_avg contains the weighted averages for each x-bin slice
print(x_slices_weighted_avg)

# You can now use this array for further analysis
print("x slices = ", x_slices_weighted_avg, "length of x_slices_avg = ", len(x_slices_weighted_avg))
z_bin = np.arange(1, 21)

plt.plot(z_bin, x_slices_weighted_avg, linestyle='-', marker='o', color='blue')
plt.title("x-slice averages per bin in x-z 2D histogram")
plt.xlabel("bin number (in z)")
plt.xticks(np.arange(1, 21, step=1))
plt.ylabel("x-slice average")
plt.show()

