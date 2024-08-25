import ROOT
import numpy as np

# Open the ROOT file
#file = ROOT.TFile("/home/gvetters/CaloX_Work/sim_data/GV_files/mc_xsim10Cu_run004_00_Test_10000evt_pi+_1.0_150.0.root", "READ")
file = ROOT.TFile("/home/gvetters/CaloX_Work/sim_data/GV_files/mc_xsim54Cu_run005_00_Test_10000evt_pi+_1.0_150.0.root", "READ")
#file = ROOT.TFile("/home/gvetters/CaloX_Work/sim_data/GV_files/mc_testjob_run001_003_Test_4500evt_mu+_5.0_150.0.root")
output_file = ROOT.TFile("sim_data_uw_pi+.root", "RECREATE")

# Get the tree from the file
tree = file.Get("tree;4") #4 or 1

# Initialize numpy arrays (empty initially)
id3dSS_array = np.array([], dtype=np.double)
ix3dSS_array = np.array([], dtype=np.double)
iy3dSS_array = np.array([], dtype=np.double)
iyy3dSS_array = np.array([], dtype=np.double)
iz3dSS_array = np.array([], dtype=np.double)

id3dCC_array = np.array([], dtype=np.double)
ix3dCC_array = np.array([], dtype=np.double)
iy3dCC_array = np.array([], dtype=np.double)
iyy3dCC_array = np.array([], dtype=np.double)
iz3dCC_array = np.array([], dtype=np.double)

ph3dSS_array = np.array([], dtype=np.double)
ph3dCC_array = np.array([], dtype=np.double)

# Loop over the entries in the tree
cnt = 0
for entry in tree:
    if cnt > 10000:
        break
    else:
        cnt += 1
        
        id3dSS = np.array(entry.id3dSS)
        id3dCC = np.array(entry.id3dCC)

        ph3dSS = np.array(entry.ph3dSS)
        ph3dCC = np.array(entry.ph3dCC)

        id3dSS_array = np.concatenate((id3dSS_array, id3dSS))
        id3dCC_array = np.concatenate((id3dCC_array, id3dCC))

        ph3dSS_array = np.concatenate((ph3dSS_array, ph3dSS))
        ph3dCC_array = np.concatenate((ph3dCC_array, ph3dCC))

# After all data is collected, manipulate the arrays
ix3dSS = np.rint(id3dSS_array / 10**7)
iy3dSS = np.rint((id3dSS_array / 10000) % 1000)
iyy3dSS = np.rint(id3dSS_array / 1000) % 10
iz3dSS = id3dSS_array % 1000
#ph3dSS_sc = ph3dSS_array / (1.766 * len(id3dSS_array))

ix3dCC = np.rint(id3dCC_array / 10**7)
iy3dCC = np.rint((id3dCC_array / 10000) % 1000)
iyy3dCC = np.rint((id3dCC_array / 1000) % 10)
iz3dCC = id3dCC_array % 1000
#ph3dCC_sc = ph3dCC_array / (2.764 * len(id3dCC_array))

'''
#Uncomment this block if lengths of np arrays need to be verified.
print("length of id3dSS_array:", len(id3dSS_array))
print("length of ix3dSS:", len(ix3dSS))
print("length of iy3dSS:", len(iy3dSS))
print("length of iyy3dSS:", len(iyy3dSS))
print("length of iz3dSS:", len(iz3dSS))

print("length of id3dCC_array:", len(id3dCC_array))
print("length of ix3dCC:", len(ix3dCC))
print("length of iy3dCC:", len(iy3dCC))
print("length of iyy3dCC:", len(iyy3dCC))
print("length of iz3dCC:", len(iz3dCC))

print("length of ph3dSS_array:", len(ph3dSS_array))
print("length of ph3dCC_array:", len(ph3dCC_array))
'''

def create_weighted_1d_histogram(name, title, x, weights, bins, x_min, x_max):
    # Create the histogram
    h = ROOT.TH1D(name, title, bins, x_min, x_max)
    #h.SetStats(False)
    
    # Fill the histogram with weights
    for i in range(len(x)):
        #h.Fill(x[i], weights[i])
        h.Fill(x[i])

    #print("Number of entries in", name, ": ", h.GetEntries())
    #print("Total integral of", name, ":", h.Integral())

    # Handle underflow and overflow
    #underflow = h.GetBinContent(0)
    #overflow = h.GetBinContent(h.GetNbinsX() + 1)

    #print("Underflow =", underflow)
    #print("Overflow =", overflow)

    # Customize histogram appearance
    h.SetLineWidth(2)
    h.SetLineColor(ROOT.kBlue)  # Color of the histogram outline
    h.SetFillColor(ROOT.kBlue)  # Color of the histogram fill
    
    # Save the histogram to the ROOT file
    h.Write()

    # Draw and save the histogram to a PDF file
    c = ROOT.TCanvas(name + "_canvas", "Canvas", 800, 600)
    ROOT.gPad.SetLogz()
    h.Draw()

    '''
    # Create a legend
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(h, f"{title}: {int(h.GetEntries())} entries", "l")
    
    # Create a TPaveText to hold underflow and overflow information
    pave_text = ROOT.TPaveText(0.7, 0.5, 0.9, 0.7, "NDC")
    pave_text.AddText(f"Underflow: {underflow}")
    pave_text.AddText(f"Overflow: {overflow}")
    pave_text.SetFillColor(0)  # Transparent background

    # Draw the legend
    legend.Draw()

    # Draw the TPaveText with underflow and overflow information
    pave_text.Draw()
    '''
    #c.SaveAs(f"{name}.pdf")

# Define function to create and save 2D histograms
def create_weighted_2d_histogram(name, title, x, y, weights, bins, x_min, x_max, y_min, y_max):
    h = ROOT.TH2D(name, title, bins, x_min, x_max, bins, y_min, y_max)
    #h.SetStats(False)
    # Fill the histogram using x and y values
    for i in range(len(x)):
        h.Fill(x[i], y[i], weights[i])

    # Save the histogram
    h.Write()
    
    # Draw and save the histogram to a PDF file
    c = ROOT.TCanvas(name, "Canvas", 1200, 800)
    ROOT.gPad.SetLogz()
    h.Draw("COLZ")  # Use "COLZ" for color mapping
    #c.SaveAs(f"{name}.pdf")

# Create 2D histograms and save them
bin_num = 50

x_min1 = ix3dSS.min() - 1
x_max1 = ix3dSS.max() + 1
create_weighted_1d_histogram("h1", "Amount of photon counts registered in the x direction (scintillating); Depth in x (ix); Photon count", ix3dSS, ph3dSS_array, bin_num, x_min1, x_max1)

x_min2 = iz3dSS.min() - 1
x_max2 = iz3dSS.max() + 1
create_weighted_1d_histogram("h2", "Amount of photon counts registered in the z direction (scintillating); Depth in z (iz); Photon count", iz3dSS, ph3dSS_array, bin_num, x_min2, x_max2)


x_min3 = ix3dCC.min() - 1
x_max3 = ix3dCC.max() + 1
create_weighted_1d_histogram("h3", "Amount of photon counts registered in the x direction (cherenkov); Depth in x (ix); Photon count", ix3dCC, ph3dCC_array, bin_num, x_min3, x_max3)

x_min4 = iz3dCC.min() - 1
x_max4 = iz3dCC.max() + 1
create_weighted_1d_histogram("h4", "Amount of photon counts registered in the z direction (cherenkov); Depth in z (iz); Photon count", iz3dCC, ph3dCC_array, bin_num, x_min4, x_max4)

x_min5 = iz3dSS.min() - 1
x_max5 = iz3dSS.max() + 1
y_min5 = ix3dSS.min() - 1
y_max5 = ix3dSS.max() + 1
create_weighted_2d_histogram("h5", "Depth in x as a function of depth in z (scintillating); Depth in z (iz); Depth in x (ix)", iz3dSS, ix3dSS, ph3dSS_array, 20, x_min5, x_max5, y_min5, y_max5)

x_min6 = iz3dCC.min() - 1
x_max6 = iz3dCC.max() + 1
y_min6 = ix3dCC.min() - 1
y_max6 = ix3dCC.max() + 1
create_weighted_2d_histogram("h6", "Depth in x as a function of depth in z (cherenkov); Depth in z (iz); Depth in x (ix)", iz3dCC, ix3dCC, ph3dCC_array, 20, x_min6, x_max6, y_min6, y_max6)

x_min7 = iy3dSS.min() - 1
x_max7 = iy3dSS.max() + 1
create_weighted_1d_histogram("h7", "Amount of photon counts registered in the y direction (scintillating); Depth in y (iy); Photon count", iy3dSS, ph3dSS_array, bin_num, x_min7, x_max7)

x_min8 = iy3dCC.min() - 1
x_max8 = iy3dCC.max() + 1
create_weighted_1d_histogram("h8", "Amount of photon counts registered in the y direction (cherenkov); Depth in y (iy); Photon count", iy3dCC, ph3dCC_array, bin_num, x_min8, x_max8)

x_min9 = ix3dSS.min() - 1
x_max9 = ix3dSS.max() + 1
y_min9 = iy3dSS.min() - 1
y_max9 = iy3dSS.max() + 1
create_weighted_2d_histogram("h9", "Depth in y as a function of depth in x (scintillating); Depth in x (ix); Depth in y (iy)", ix3dSS, iy3dSS, ph3dSS_array, 20, x_min9, x_max9, y_min9, y_max9)

x_min10 = ix3dCC.min() - 1
x_max10 = ix3dCC.max() + 1
y_min10 = iy3dCC.min() - 1
y_max10 = iy3dCC.max() + 1
create_weighted_2d_histogram("h10", "Depth in y as a function of depth in x (cherenkov); Depth in x (ix); Depth in y (iy)", ix3dCC, iy3dCC, ph3dCC_array, 20, x_min10, x_max10, y_min10, y_max10)

x_min11 = iy3dSS.min() - 1
x_max11 = iy3dSS.max() + 1
y_min11 = iz3dSS.min() - 1
y_max11 = iz3dSS.max() + 1
create_weighted_2d_histogram("h11", "Depth in y as a function of depth in z (scintillating); Depth in y (iy); Depth in z (iz)", iz3dSS, iy3dSS, ph3dSS_array, 20, x_min11, x_max11, y_min11, y_max11)

x_min12 = iy3dCC.min() - 1
x_max12 = iy3dCC.max() + 1
y_min12 = iz3dCC.min() - 1
y_max12 = iz3dCC.max() + 1
create_weighted_2d_histogram("h12", "Depth in y as a function of depth in z (cherenkov); Depth in y (iy); Depth in z (iz)", iz3dCC, iy3dCC, ph3dCC_array, 20, x_min12, x_max12, y_min12, y_max12)

#x_min13 = iyy3dSS.min() - 1
#x_max13 = iyy3dSS.max() + 1
#create_weighted_1d_histogram("h13", "Signal as a function of depth in yy direction (scintillating); Depth in yy (iyy); Photon count", iyy3dSS, ph3dSS_array, bin_num, x_min13, x_max13)

#x_min14 = iyy3dCC.min() - 1
#x_max14 = iyy3dCC.max() + 1
#create_weighted_1d_histogram("h14", "Signal as a function of depth in yy direction (cherenkov); Depth in yy (iyy); Photon count", iyy3dCC, ph3dCC_array, bin_num, x_min14, x_max14)

# Close the output ROOT file
output_file.Close()
# Close the ROOT file
file.Close()