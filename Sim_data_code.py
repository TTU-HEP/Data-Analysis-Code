import ROOT
import numpy as np

# Open the ROOT file
#file = ROOT.TFile("/home/gvetters/CaloX_Work/sim_data/GV_files/mc_xsim10Cu_run004_00_Test_10000evt_pi+_1.0_150.0.root", "READ")
file = ROOT.TFile("/home/gvetters/CaloX_Work/sim_data/GV_files/mc_xsim10Cu_run007_10_Test_10000evt_pi+_1.0_150.0.root", "READ")
#file = ROOT.TFile("/home/gvetters/CaloX_Work/sim_data/GV_files/mc_testjob_run001_003_Test_4500evt_mu+_5.0_150.0.root")
output_file = ROOT.TFile("sim_data_uw1_pi+.root", "RECREATE")

# Get the tree from the file
tree = file.Get("tree;4")

def create_histograms():
    histograms = {
        "h1": ROOT.TH1D("h1", "Signal registered in the x direction (scintillating); Depth in x (ix); # of entries", 50, 0, 50),
        "h2": ROOT.TH1D("h2", "Signal registered in the z direction (scintillating); Depth in z (iz); # of entries", 250, 0, 250),
        "h3": ROOT.TH1D("h3", "Signal registered in the x direction (cherenkov); Depth in x (ix); # of entries", 50, 0, 50),
        "h4": ROOT.TH1D("h4", "Signal registered in the z direction (cherenkov); Depth in z (iz); # of entries", 250, 0, 250),
        "h5": ROOT.TH2D("h5", "Depth in x as a function of depth in z (scintillating); Depth in z (iz); Depth in x (ix)", 250, 0, 250, 20, 4, 24),
        "h6": ROOT.TH2D("h6", "Depth in x as a function of depth in z (cherenkov); Depth in z (iz); Depth in x (ix)", 250, 0, 250, 20, 4, 24),
        "h7": ROOT.TH1D("h7", "Signal registered in the y direction (scintillating); Depth in y (iy); # of entries", 50, 0, 50),
        "h8": ROOT.TH1D("h8", "Signal registered in the y direction (cherenkov); Depth in y (iy); # of entries", 50, 0, 50),
        "h9": ROOT.TH2D("h9", "Depth in y as a function of depth in x (scintillating); Depth in x (ix); Depth in y (iy)", 20, 5, 25, 20, 0, 20),
        "h10": ROOT.TH2D("h10", "Depth in y as a function of depth in x (cherenkov); Depth in x (ix); Depth in y (iy)", 20, 5, 25, 20, 0, 20),
        "h11": ROOT.TH2D("h11", "Depth in y as a function of depth in z (scintillating); Depth in z (iz); Depth in y (iy)", 250, 0, 250, 20, 0, 20),
        "h12": ROOT.TH2D("h12", "Depth in y as a function of depth in z (cherenkov); Depth in z (iz); Depth in y (iy)", 250, 0, 250, 20, 0, 20)
    }
    return histograms

# Define the histograms once
histograms = create_histograms()

# Loop over the entries in the tree
cnt = 0
for entry in tree:
    if cnt > 10000:
        break
    else:
        cnt += 1

        id3dSS_array = np.array(entry.id3dSS)
        id3dCC_array = np.array(entry.id3dCC)

        ph3dSS_array = np.array(entry.ph3dSS)
        ph3dCC_array = np.array(entry.ph3dCC)

        ix3dSS = np.rint(id3dSS_array / 10**7)
        iy3dSS = np.rint((id3dSS_array / 10000) % 1000)
        iz3dSS = id3dSS_array % 1000

        ix3dCC = np.rint(id3dCC_array / 10**7)
        iy3dCC = np.rint((id3dCC_array / 10000) % 1000)
        iz3dCC = id3dCC_array % 1000

        nhitsSS = len(ix3dSS)
        nhitsCC = len(ix3dCC)
         # Check if arrays are non-empty before filling histograms
        if len(ix3dSS) > 0:
            for i in range(len(ix3dSS)):
                histograms["h1"].Fill(ix3dSS[i]) #, ph3dSS_array[i])
                histograms["h2"].Fill(iz3dSS[i]) #, ph3dSS_array[i])
                histograms["h5"].Fill(iz3dSS[i], ix3dSS[i], ph3dSS_array[i])
                histograms["h7"].Fill(iy3dSS[i]) #, ph3dSS_array[i])
                histograms["h9"].Fill(ix3dSS[i], iy3dSS[i], ph3dSS_array[i])
                histograms["h11"].Fill(iz3dSS[i], iy3dSS[i], ph3dSS_array[i])

        if len(ix3dCC) > 0:
            for i in range(len(ix3dCC)):
                histograms["h3"].Fill(ix3dCC[i]) #, ph3dCC_array[i])
                histograms["h4"].Fill(iz3dCC[i]) #, ph3dCC_array[i])
                histograms["h6"].Fill(iz3dCC[i], ix3dCC[i], ph3dCC_array[i])
                histograms["h8"].Fill(iy3dCC[i]) #, ph3dCC_array[i])
                histograms["h10"].Fill(ix3dCC[i], iy3dCC[i], ph3dCC_array[i])
                histograms["h12"].Fill(iz3dCC[i], iy3dCC[i], ph3dCC_array[i])

# Save all histograms
output_file.cd()
for hist in histograms.values():
    hist.Write()

# Close the output ROOT file
output_file.Close()
file.Close()

print('Code is done! :D')