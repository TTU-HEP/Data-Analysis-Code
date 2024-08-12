# Converted on 8/12/2024 - MO

import ROOT
from ROOT import TCanvas, TChain, TH1D, TF1, TLatex

def ppe_func(x, params):
    # Custom function based on parameters
    p0, p1, p2, p3, p4 = params
    return p0 / (p2 * ROOT.TMath.Sqrt(2 * ROOT.TMath.Pi())) * ROOT.TMath.Exp(-((x[0] - p1) * (x[0] - p1)) / (2 * p2 * p2)) + p3 * ROOT.TMath.Exp(-((x[0] - p4) * (x[0] - p4)) / (2 * p2 * p2))

def fitSPEMIP(hfit, run):
    c1 = TCanvas("c1", "c1", 800, 800)
    c1.SetTopMargin(0.1)
    c1.SetBottomMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetLeftMargin(0.14)
    c1.SetLogy()
    hfit.GetXaxis().SetRangeUser(1, 1000)
    hfit.SetMinimum(0.01)
    hfit.SetMaximum(1000)

    ffname = f"sff{hfit.GetName()}"
    nPeaks = 4

    # Define the fitting function
    def fit_func(x, p):
        return ppe_func(x, p)

    fit1 = TF1(ffname, fit_func, 0.0, 1000.0, 5)
    fit1.SetParameters(450, 10, 20, 0, 1)
    fit1.SetParLimits(0, 10, 500)
    fit1.SetParLimits(1, 10.0, 18.0)
    fit1.SetParLimits(2, 0, 25)
    fit1.SetParLimits(3, 0, 1000)
    fit1.SetParLimits(4, 0, 1000)

    hfit.Fit(fit1, "RQML", "", 5, 100)
    fit1.SetLineColor(ROOT.kRed)
    fit1.SetLineWidth(2)

    # Additional fits with different parameters
    fit2 = TF1(f"sff2{hfit.GetName()}", fit_func, 0.0, 1000.0, 5)
    fit2.SetParameters(*fit1.GetParameters())
    hfit.Fit(fit2, "RQML", "", fit1.GetParameter(2), 1000)
    fit2.SetLineColor(ROOT.kBlack)
    fit2.SetLineWidth(2)

    fit3 = TF1(f"sff3{hfit.GetName()}", fit_func, 0.0, 1000.0, 5)
    fit3.SetParameters(*fit2.GetParameters())
    hfit.Fit(fit3, "RQML", "", fit2.GetParameter(2), 1000)
    fit3.SetLineColor(ROOT.kBlue)
    fit3.SetLineWidth(2)

    # Define MIP function with additional parameters
    fit4 = TF1(f"sff4{hfit.GetName()}", fit_func, 0.0, 1000.0, 14)
    fit4.SetParameters(*fit3.GetParameters(), 300, 1000, 50, 100)
    hfit.Fit(fit4, "RQML", "", fit3.GetParameter(2), 1000)
    fit4.SetLineColor(ROOT.kOrange)
    fit4.SetLineWidth(2)

    fit5 = TF1(f"sff5{hfit.GetName()}", fit_func, 0.0, 1000.0, 14)
    fit5.SetParameters(*fit4.GetParameters())
    hfit.Fit(fit5, "RQML", "", fit4.GetParameter(2), 1000)
    fit5.SetLineColor(ROOT.kBlack)
    fit5.SetLineWidth(2)

    print(f"Chi^2:{fit5.GetChisquare():10.4f} Gain:{fit5.GetParameter(7):10.4f} MPV:{fit5.GetParameter(11):10.4f}")
    hfit.GetYaxis().SetTitle("Events")
    hfit.GetXaxis().SetTitle("ADC Counts")
    hfit.SetTitleOffset(1, "X")
    hfit.SetTitleOffset(1.2, "Y")
    hfit.SetTitleSize(0.05, "X")
    hfit.SetTitleSize(0.05, "Y")

    draw5PE = TF1("BackGround_MIP", fit_func, 0.0, 1000.0, 14)
    draw5PE.SetParameters(*fit5.GetParameters())
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
        max_entries = 10
        entry_count = 0

        for entry in chBase:
            hg1 = getattr(chBase, "FERS_Board1_energyHG")
            if hg1[chan] < 1000:
                h.Fill(hg1[chan])
                
            entry_count += 1
            if entry_count >= max_entries:
                break

        fitSPEMIP(h, 1)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()

#end