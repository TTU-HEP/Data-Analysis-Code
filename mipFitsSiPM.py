# Converted on 8/9/2024 - Michael O'Donnell

import ROOT
from ROOT import TCanvas, TChain, TH1D, TF1, TLatex


print(dir(ROOT))
# This function fits the SiPM MIP distribution
def fitSPEMIP(hfit, run):
    c1 = TCanvas("c1", "c1", 800, 800)
    c1.SetTopMargin(0.1)
    c1.SetBottomMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetLeftMargin(0.14)
    # c1.SetLogx()
    c1.SetLogy()
    # hfit.GetXaxis().SetRangeUser(10, 400)
    hfit.GetXaxis().SetRangeUser(1, 1000)
    hfit.SetMinimum(0.01)
    hfit.SetMaximum(1000)

    ffname = f"sff{hfit.GetName()}"
    nPeaks = 4

    background = ROOT.PPEFunc(nPeaks, False)
    background.h = hfit
    background_MIP = ROOT.PPEFunc(nPeaks, True)
    background_MIP.h = hfit
    hfit.Draw("hist")

    # Parameters for fitting
    fit_params = [
        (10, 500),   # p[0] : pedestal amplitude
        (10.0, 18.0),  # p[1] : pedestal width
        (0, 25),    # p[2] : Overall Shift
        (0, 1000),  # p[3] : background amplitude
        (0, 1000),  # p[4] : background width
        (40000, 50000), # p[5] : overall PE amplitude
        (0.01, 1.0),   # p[6] : Poisson mean number of PE
        (0, 100),   # p[7] : PE peak spacing (Gain)
        (0.1, 35),   # p[8] : PE peak width
        (0.01, 0.95),  # p[9] : pixel cross-talk probability
        (200, 200000),  # p[10] : Total MIP peak area
        (90, 2500),   # p[11] : Most probable value of Landau (MPV)
        (1, 150),   # p[12] : Landau width parameter
        (1, 200),   # p[13] : Gaussian width
    ]

    set_params = [450, 10, 20, 0, 1, 40000, 0.02, 45, 1.0, 0.4, 300, 1000, 50, 100]

    fit1 = TF1(ffname, background, 0.0, 1000.0, 10)
    for i, (min_val, max_val) in enumerate(fit_params[:10]):
        fit1.SetParLimits(i, min_val, max_val)
    for i, val in enumerate(set_params[:10]):
        if i in [3, 4, 5]:
            fit1.FixParameter(i, val)
        else:
            fit1.SetParameter(i, val)

    hfit.Fit(fit1, "RQML", "", 5, 100)
    fit1.SetLineColor(ROOT.kRed)
    fit1.SetLineWidth(2)

    # Fit PE Peaks
    fit2 = TF1(f"sff2{hfit.GetName()}", background, 0.0, 1000.0, 10)
    for i, (min_val, max_val) in enumerate(fit_params[:10]):
        fit2.SetParLimits(i, min_val, max_val)
    fit2.SetParameter(0, fit1.GetParameter(0))
    fit2.FixParameter(1, fit1.GetParameter(1))
    fit2.FixParameter(2, fit1.GetParameter(2))
    for i, val in enumerate(set_params[3:10], start=3):
        fit2.SetParameter(i, val)

    hfit.Fit(fit2, "RQML", "", fit1.GetParameter(2), 1000)
    fit2.SetLineColor(ROOT.kBlack)
    fit2.SetLineWidth(2)

    # Fine tune PE peaks
    fit3 = TF1(f"sff3{hfit.GetName()}", background, 0.0, 1000.0, 10)
    down1, up1 = 0.7, 1.3
    for i in range(10):
        fit3.SetParLimits(i, down1 * fit2.GetParameter(i), up1 * fit2.GetParameter(i))
    for i in range(10):
        fit3.SetParameter(i, fit2.GetParameter(i))

    hfit.Fit(fit3, "RQML", "", fit2.GetParameter(2), 1000)
    fit3.SetLineColor(ROOT.kBlue)
    fit3.SetLineWidth(2)

    # Fit MIP peak
    fit4 = TF1(f"sff4{hfit.GetName()}", background_MIP, 0.0, 1000.0, 14)
    for i, (min_val, max_val) in enumerate(fit_params):
        fit4.SetParLimits(i, min_val, max_val)
    for i in range(10):
        fit4.FixParameter(i, fit3.GetParameter(i))
    for i, val in enumerate(set_params[10:], start=10):
        fit4.SetParameter(i, val)

    hfit.Fit(fit4, "RQML", "", fit3.GetParameter(2), 1000)
    fit4.SetLineColor(ROOT.kOrange)
    fit4.SetLineWidth(2)

    # Fine-tuning All Fit
    fit5 = TF1(f"sff4{hfit.GetName()}", background_MIP, 0.0, 1000.0, 14)
    down, up = 0.7, 1.3
    for i in range(14):
        fit5.SetParLimits(i, down * fit4.GetParameter(i), up * fit4.GetParameter(i))
    for i in range(14):
        fit5.SetParameter(i, fit4.GetParameter(i))

    hfit.Fit(fit5, "RQML", "", fit4.GetParameter(2), 1000)
    fit5.SetLineColor(ROOT.kBlack)
    fit5.SetLineWidth(2)

    # Print and display results
    print(f"Chi^2:{fit5.GetChisquare():10.4f} Gain:{fit5.GetParameter(7):10.4f} MPV:{fit5.GetParameter(11):10.4f}")
    hfit.GetYaxis().SetTitle("Events")
    hfit.GetXaxis().SetTitle("ADC Counts")
    hfit.SetTitleOffset(1, "X")
    hfit.SetTitleOffset(1.2, "Y")
    hfit.SetTitleSize(0.05, "X")
    hfit.SetTitleSize(0.05, "Y")

    draw5PE = TF1("BackGround_MIP", background_MIP, 0.0, 1000.0, 14)
    for i in range(14):
        draw5PE.FixParameter(i, fit5.GetParameter(i))
    draw5PE.SetLineWidth(2)
    draw5PE.SetLineColor(ROOT.kBlue)
    draw5PE.Draw("same")

    draw5Mip = TF1("Lang", ROOT.langaufun, 0.0, 1000.0, 4)
    draw5Mip.FixParameter(0, fit5.GetParameter(12))
    draw5Mip.FixParameter(1, fit5.GetParameter(11) + fit5.GetParameter(2))
    draw5Mip.FixParameter(2, fit5.GetParameter(10))
    draw5Mip.FixParameter(3, fit5.GetParameter(13))
    draw5Mip.SetLineWidth(2)
    draw5Mip.SetLineColor(ROOT.kGreen + 2)
    draw5Mip.Draw("same")

    hfit.SetStats(False)
    hfit.SetTitle("")

    testbeam = TLatex(0.95, 0.91, "HG-DREAM 2024")
    testbeam.SetNDC()
    testbeam.SetTextFont(42)
    testbeam.SetTextAlign(31)
    testbeam.Draw()

    mpv_text = f"MPV: {fit5.GetParameter(11):0.3f}"
    MPV = TLatex(0.93, 0.8, mpv_text)
    MPV.SetNDC()
    MPV.SetTextFont(42)
    MPV.SetTextAlign(31)
    MPV.Draw()

    gain_text = f"SiPM Gain: {fit5.GetParameter(7):0.3f}"
    Gain = TLatex(0.93, 0.75, gain_text)
    Gain.SetNDC()
    Gain.SetTextFont(42)
    Gain.SetTextAlign(31)
    Gain.Draw()

    oname = f"adcHist_{hfit.GetName()}_{run}.pdf"
    c1.Print(oname)

def main():
    baseFile = "/home/michaelod/CaloXWork/datafiles/run742_V22000.root"
    treeName = "EventTree"
    chBase = ROOT.TChain(treeName)
    chBase.Add(baseFile)

    try:
        h = ROOT.TH1D("h", "h", 1000, 0, 2000)
        chan = 1

        # Read data from TChain
        for entry in chBase:
            # Assuming FERS_Board1_energyHG is a branch in the tree
            hg1 = getattr(chBase, "FERS_Board1_energyHG")
            if hg1[chan] < 1:
                h.Fill(hg1[chan])

        fitSPEMIP(h, 1)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
