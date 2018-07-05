#!/usr/bin/env python
# Summary Plots For QIE Calibration
# Zach Shelton
#Located in Desktop/SummaryPlots
# Updated: 6/6/18 6:00PM CDT
# Imported Packages
import sqlite3
import pprint
import glob
import os
import sys
import argparse
from MergeDatabases import MergeDatabases


#For Adapter test
#Bin Definitions
bins = [0, 1, 2, 3]
backAdapter = [1,2,3,4,9,10,11,12]



shunts = [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11.5]
hslopes = {}
hoffsets = {}


plotBoundaries_slope = [0.28, 0.33]

plotBoundaries_offset = [1, 16, 100, 800]

#FINDING ERROR PERCENTAGE
thshunt= .30
THRESHOLD = .15


def SummaryPlot(options):

    from ROOT import *
    gROOT.SetBatch(True)
    # Get required arguments from options
    date = options.date[0]
    run = options.run[0]

    qieList = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

    #Canvases

    c = []
    c2 = []

    #Histogram Lists

    histoffset = []
    histshunt = []
    histslopes = []
    histSlopeNvSlope1 = []
    histShuntFactor = []

    #Total Histograms

    totalhist = []

    #Max - min Variables
    maximum = 0
    minimum = 0

    #Failure
    failure = False
    FailedCards = []


    #Set Axes Digits
    if(options.all or not options.uid is None):
        files = glob.glob("data/%s/Run_%s/qieCalibrationParameters*.db"%(date,run))
    elif(len(options.dbnames) != 0):
        files = []
        for f in options.dbnames:
            files.append(glob.glob("data/%s/Run_%s/%s"%(date,run,f))[0])
            print files
    MergeDatabases(files, "data/%s/Run_%s/"%(date, run),"MergedDatabaseRun%s.db"%run)
    xyz1234 = sqlite3.connect("data/%s/Run_%s/MergedDatabaseRun%s.db"%(date, run,run))
    cursor = xyz1234.cursor()
    TGaxis.SetMaxDigits(3)
    #files = cursor.excute("Select distinct runDirectory from qieshuntparams").Fetchall()
    idlist = cursor.execute("Select distinct id from qieshuntparams").fetchall()
    #if (options.all):
    for nameList in idlist:
        name = nameList[0]

        if not options.uid is None:
            if name not in options.uid:
                continue
        if not os.path.exists("data/%s/Run_%s/SummaryPlots"%(date, run)):
            os.makedirs("data/%s/Run_%s/SummaryPlots"%(date,run))
        if not os.path.exists("data/%s/Run_%s/SummaryPlots/%s/ImagesOutput"%(date,run,name)):
            os.makedirs("data/%s/Run_%s/SummaryPlots/%s/ImagesOutput"%(date,run,name))
        if not os.path.exists("data/%s/Run_%s/SummaryPlots/Log/"%(date,run)):
            os.makedirs("data/%s/Run_%s/SummaryPlots/Log"%(date,run))
        #if not os.path.exists("data/%s/Run_%s/SummaryPlots/TotalPlots"%(date, run)):
            #os.makedirs("data/%s/Run_%s/SummaryPlots/TotalPlots"%(date, run))
            # Modify rootout change title of output ROOT file
        rootout = TFile("data/%s/Run_%s/SummaryPlots/%s/summary_plot_%s.root" %(date, run, name, name), "recreate")
        for r in bins:
            for sh in shunts:
                if (r == 2 or r == 3) and (sh != 1):
                    continue
                # Fetch the values of slope and offset for the corresponding shunt and range
                #values = cursor.execute("select slope,offset from qieshuntparams where range=%i and shunt=%.1f and id = '%s';" % (r, sh,name)).fetchall()
                values = cursor.execute("select slope,offset,qie,capid, (SELECT slope from qieshuntparams where id=p.id and qie=p.qie and capID=p.capID and range=p.range and shunt=1) from qieshuntparams as p where range = %i and shunt = %.1f and id = '%s';"%(r,sh,name)).fetchall()

                # Fetch Max and minimum values for slope of shunt
                maxmin = cursor.execute("select max(slope),min(slope) from qieshuntparams where range=%i and shunt = %.1f and id = '%s';" % (r, sh,name)).fetchall()
                maximum, minimum = maxmin[0]
                maximums = max(plotBoundaries_slope[1]/sh, maximum+0.01)
                minimums = min(plotBoundaries_slope[0]/sh, minimum-0.01)
                if sh == 1:
                    maximum1 = maximums
                    minimum1 = minimums
                #Creates Canvases for each Shunt and Range(TH1D)
                c.append(TCanvas("Card %s Shunt %.1f  -  Range %i" % (name, sh, r), "histo"))
                c[-1].Divide(2,1)

                c[-1].cd(1)
                #Create Histograms for the shunt slopes
                histshunt.append(TH1D("SLOPE Sh: %.1f - R: %i" %(sh, r),"%s Shunt %.1f - Range %i" % (name, sh, r), 100, minimums, maximums))
                histshunt[-1].SetTitle("SLOPE SH: %.1f R: %d"%(sh,r))
                histshunt[-1].GetXaxis().SetTitle("Slope")
                histshunt[-1].GetYaxis().SetTitle("Frequency")
                gPad.SetLogy(1)

                #Create 2D histogram of slope of shunt N vs slope of shunt 1
                if(options.hist2D):
                    histSlopeNvSlope1.append(TH2D("Slope_Shunt_%s_vs_Shunt_1_R_%i"%(str(sh).replace(".",""),r),"%s Slope of Shunt %.1f vs Shunt 1 - Range %i"%(name,sh,r),100,minimum1,maximum1,100,minimums,maximums))
                    histSlopeNvSlope1[-1].GetXaxis().SetTitle("Shunt 1 Slope")
                    histSlopeNvSlope1[-1].GetYaxis().SetTitle("Shunt %.1f Slope"%sh)
                #Create 2D histogram of slope vs qie
                if(options.slVqie):
                    histSlvQie.append(TH2D("SlopeVsQIE_Shunt_%s_Range_%d"%(str(sh).replace(".",""),r),"%s Slope Vs QIE Shunt %.1f Range %d"%(name,sh,r),16,0.5,16.5,40,minimums,maximums))
                    histSlvQie[-1].GetXaxis().SetTitle("QIE")
                    histSlvQie[-1].GetYaxis().SetTitle("Slope")
                #Create histogram of shunt factor
                if(options.shFac):
                    histShuntFactor.append(TH1D("ShuntFactor_Sh_%s_R_%.i"%(str(sh).replace(".",""),r),"Shunt Factor Shunt %.1f Range %i"%(sh,r),100,sh-1,sh+1))
                    histShuntFactor[-1].GetXaxis().SetTitle("Shunt Factor")
                    histShuntFactor[-1].GetYaxis().SetTitle("Frequency")

                #Create Histograms for the Offsets
                maxmin = cursor.execute("select max(offset),min(offset) from qieshuntparams where range=%i and shunt = %.1f and id = '%s';" % (r, sh,name)).fetchall()
                maximum, minimum = maxmin[0]
                maximumo  = max(plotBoundaries_offset[r], maximum)
                minimumo  = min(-1*plotBoundaries_offset[r], minimum)
                test = []
                c[-1].cd(2)
                histoffset.append(TH1D("OFFSET Sh: %.1f - R: %i" %(sh, r),"%s Shunt %.1f - Range %d" %(name, sh, r), 40, minimumo, maximumo))
                histoffset[-1].SetTitle("OFFSET SH: %.1f R: %d"%(sh,r))
                histoffset[-1].GetXaxis().SetTitle("Offset")
                histoffset[-1].GetYaxis().SetTitle("Frequency")
                gPad.SetLogy(1)
                if sh not in hslopes.keys():
                    hslopes[sh] = {}
                if r not in hslopes[sh].keys():
                    hslopes[sh][r] = {"total":{}, "front":{}, "back":{}}
                    for ty in ['total','front','back']:
                        hslopes[sh][r][ty] = TH1D("Slopes_shunt_%s_range_%d" % (str(sh).replace(".","_"), r), "Slopes  Shunt %.1f Range %d" % (sh,r), 100, minimums, maximums)
                        hslopes[sh][r][ty].SetDirectory(0)
                        hslopes[sh][r][ty].GetXaxis().SetTitle("Slope (LinADC / fC)")
                        hslopes[sh][r][ty].GetYaxis().SetTitle("QIE Channels")
                    hslopes[sh][r]['front'].SetTitle("Slopes  Front Adapter  Shunt %.1f Range %d" % (sh,r))
                    hslopes[sh][r]['back'].SetTitle("Slopes  Back Adapter  Shunt %.1f Range %d" % (sh,r))
                if sh not in hoffsets.keys():
                    hoffsets[sh] = {}
                if r not in hoffsets[sh].keys():
                    hoffsets[sh][r] = {"total":{}, "front":{}, "back":{}}
                    for ty in ['total','front','back']:
                        hoffsets[sh][r][ty] = TH1D("Offsets_shunt_%s_range_%d" % (str(sh).replace(".","_"), r), "Offsets  Shunt %.1f Range %d" % (sh,r), 100, minimumo, maximumo)
                        hoffsets[sh][r][ty].SetDirectory(0)
                        hoffsets[sh][r][ty].GetXaxis().SetTitle("Offset (LinADC)")
                        hoffsets[sh][r][ty].GetYaxis().SetTitle("QIE Channels")
                    hoffsets[sh][r]['front'].SetTitle("Slopes  Front Adapter  Shunt %.1f Range %d" % (sh,r))
                    hoffsets[sh][r]['back'].SetTitle("Slopes  Back Adapter  Shunt %.1f Range %d" % (sh,r))
                # Fills the histograms with the values fetched above
                for val in values:
                    #slope, offset = val
                    slope, offset,qie,capid ,slSh1 = val
                    if slopeFail(sh,r,name,slope,thshunt,THRESHOLD) or offsetFail(sh,r,offset,name):
                        if slopeFail(sh,r,name,slope) and offsetFail(sh,r,offset,name):
                            test.append({'slope':slope,'shunt':sh, 'range':r,'offset':offset,'Qie':qie,'CapID':capid,'BadSlope':1,'BadOffset':1})
                        elif slopeFail(sh,r,name,slope):
                            test.append({'slope':slope,'shunt':sh, 'range':r,'offset':offset,'Qie':qie,'CapID':capid,'BadSlope':1,'BadOffset':0})
                        elif offsetFail(sh,r,offset,name):
                            test.append({'slope':slope,'shunt':sh, 'range':r,'offset':offset,'Qie':qie,'CapID':capid,'BadSlope':0,'BadOffset':1})
                    c[-1].cd(1)
                    histshunt[-1].Fill(slope)
                    histshunt[-1].Draw()
                    c[-1].cd(2)
                    histoffset[-1].Fill(offset)
                    histoffset[-1].Draw()
                    hslopes[sh][r]['total'].Fill(slope)
                    hoffsets[sh][r]['total'].Fill(offset)
                    if qie in backAdapter:
                        hslopes[sh][r]['back'].Fill(slope)
                        hoffsets[sh][r]['back'].Fill(offset)
                    else:
                        hslopes[sh][r]['front'].Fill(slope)
                        hoffsets[sh][r]['front'].Fill(offset)
                    #c[-1].cd(3)
                    if(options.hist2D):
                        histSlopeNvSlope1[-1].Fill(slSh1,slope)
                    if(options.shFac):
                        try:
                            histShuntFactor[-1].Fill(slSh1/slope)
                        except ZeroDivisionError:
                            print "Divide by Zero Error: %s Shunt %.1f Range %d"%(name,sh,r)
                    #histSlopeNvSlope1[-1].Draw()
                # Write the histograms to the file, saving them for later
                # histshunt[-1].Draw()
                # histoffset[-1].Draw()
                # c2[-1].Write()
                c[-1].Update()
                #c[-1].SaveAs("data/%s/Run_%s/SummaryPlots/ImagesOutput/CARD_%s_SHUNT_%s_RANGE_%i.png"%(date, run, name, str(sh).replace(".",""), r))
                if(options.images):
                    c[-1].Print("data/%s/Run_%s/SummaryPlots/%s/ImagesOutput/%s_SHUNT_%s_RANGE_%i.png"%(date, run, name,name, str(sh).replace(".",""), r))
                c[-1].Write()
                if(options.hist2D):
                    histSlopeNvSlope1[-1].Write()
                if(options.shFac):
                    histShuntFactor[-1].Write()
                
                if(options.verbose):
                    print "Card %s Shunt %.1f Range %d Finished"%(name,sh,r)
                # if True:
                #     maxmin = cursor.execute("select max(slope),min(slope),max(offset),min(offset) from qieshuntparams where range=%i and shunt = %.1f and id= '%s';" % (r, sh,name)).fetchall()
                #     maximum , minimum,maxo,mino = maxmin[0]
                #     maxt=(thshunt/sh)+(thshunt/sh)*THRESHOLD
                #     mint=(thshunt/sh)-(thshunt/sh)*THRESHOLD
                #     if sh == 1:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 1.5:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 2:
                #         if ((mint > minimum or maximum > maxt)):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 3:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 4:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 5:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 6:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 7:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 8:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 9:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 10:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 11:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if sh == 11.5:
                #         if (mint > minimum or maximum > maxt):
                #             print "Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
                #             failure = True
                #     if r == 0:
                #         if maxo > -.25 or mino < -.75:
                #             print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
                #             failure=True
                #     if r == 1:
                #         if maxo > 12 or mino < -12:
                #             print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
                #             failure=True
                #     if r == 2:
                #         if maxo > 80 or mino < -80:
                #             print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
                #             failure=True
                #     if r == 3:
                #         if maxo > 600 or mino < -600:
                #             print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
                #             failure=True
                #     if failure:
                        # fail = cursor.execute("Select shunt,range, offset, qie,capid from qieshuntparams where slope= and shunt = %.1f and range  = %i and id = '%s'; "%(maxt,mint,sh,r,name))
                        # tshun, tranges, toffset, tcapid, tfailedcards = fault
                        # FailedCards['Shunts'].append(tshun)
                        # FailedCards['Ranges'].append(tranges)
                        # FailedCards['Offset'].append(toffset)
                        # FailedCards['capID'].append(tcapid)
                        # FailedCards['Qie'].append(tfailedcards)
                        # FailedCards['Card'].append(name)

                # maxmin = cursor.execute("select max(offset),min(offset) from qieshuntparams where range=%i and shunt = %.1f and id= '%s';" % (r, sh,name)).fetchall()
                # maxo,mino = maxmin[0]
                # if ofail:
                #     fail = cursor.execute("Select shunt,range, offset, qie,capid from qieshuntparams where slope > %.1f or range<%.1f and shunt = %.1f and range  = %i and id = '%s'; "%(maxo,mino,sh,r,name))
                #     for fault in fail:
                #         tshun, tranges, toffset, tcapid, tfailedcards = fault
                #         FailedCards['Shunts'].append(tshun)
                #         FailedCards['Ranges'].append(tranges)
                #         FailedCards['Offset'].append(toffset)
                #         FailedCards['capID'].append(tcapid)
                #         FailedCards['Qie'].append(tfailedcards)
                #         FailedCards['Card'].append(name)
                #         FailedCards['label'].append("Bad Offset")
                FailedCards.append(test)
    if(options.all):
        rundir = "data/%s/Run_%s/SummaryPlots" % (date, run)
        outdir = "adapterTests"
        os.system("mkdir -p %s/%s" % (rundir, outdir))
        c = TCanvas("c","c",1600,1200)
        shunts = [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11.5]
        ranges = xrange(4)
        gStyle.SetOptStat(0)
        for r in bins:
            for sh in shunts:
                if (r == 2 or r == 3) and (sh != 1):
                    continue
                l = TLegend(0.75, 0.75, 0.9, 0.9)
                l.AddEntry(hslopes[sh][r]['front'], "Front adapter")
                l.AddEntry(hslopes[sh][r]['back'], "Back adapter")
                hslopes[sh][r]['front'].SetLineColor(2)
                hslopes[sh][r]['front'].SetLineWidth(2)
                hslopes[sh][r]['back'].SetLineColor(4)
                hslopes[sh][r]['back'].SetLineWidth(2)

                hslopes[sh][r]['back'].SetTitle("Slopes  Shunt %.1f Range %d" % (sh,r))
                hslopes[sh][r]['back'].Draw("HIST")
                hslopes[sh][r]['front'].Draw("HIST SAME")
                l.Draw("SAME")
                c.SaveAs("%s/%s/slopes_shunt_%s_range_%d.png" % (rundir,outdir,str(sh).replace(".","_"),r))

                lo = TLegend(0.75, 0.75, 0.9, 0.9)
                lo.AddEntry(hslopes[sh][r]['front'], "Front adapter")
                lo.AddEntry(hslopes[sh][r]['back'], "Back adapter")

                hoffsets[sh][r]['front'].SetLineColor(2)
                hoffsets[sh][r]['front'].SetLineWidth(2)
                hoffsets[sh][r]['back'].SetLineColor(4)
                hoffsets[sh][r]['back'].SetLineWidth(2)

                hoffsets[sh][r]['back'].SetTitle("Offsets  Shunt %.1f Range %d" %(sh,r))
                hoffsets[sh][r]['back'].Draw("HIST")
                hoffsets[sh][r]['front'].Draw("HIST SAME")
                lo.Draw("SAME")
                c.SaveAs("%s/%s/offsets_shunt_%s_range_%d.png" % (rundir,outdir,str(sh).replace(".","_"),r))
    if (options.total):
        name = nameList[0]
        if not os.path.exists("data/%s/Run_%s/SummaryPlots"%(date, run)):
            os.makedirs("data/%s/Run_%s/SummaryPlots"%(date,run))
        if not os.path.exists("data/%s/Run_%s/SummaryPlots/TotalOutput"%(date, run)):
            os.makedirs("data/%s/Run_%s/SummaryPlots/TotalOutput"%(date,run))
            # Modify rootout change title of output ROOT file
        rootout = TFile("data/%s/Run_%s/SummaryPlots/summary_plot_total.root" %(date, run), "recreate")
        for ra in bins:
            r =ra[0]
            for shu in shunts:
                sh = shu[0]
                if (r == 2 or r == 3) and (sh != 1):
                    continue
                # Fetch the values of slope and offset for the corresponding shunt and range
                #values = cursor.execute("select slope,offset from qieshuntparams where range=%i and shunt=%.1f ;" % (r, sh)).fetchall()
                values = cursor.execute("select slope,offset,capid, (SELECT slope from qieshuntparams where id=p.id and qie=p.qie and capID=p.capID and range=p.range and shunt=1) from qieshuntparams as p where range = %i and shunt = %.1f;"%(r,sh)).fetchall()
                # Fetch Max and minimum values for slope of shunt
                maxmin = cursor.execute("select max(slope),min(slope) from qieshuntparams where range=%i and shunt = %.1f;" % (r,sh)).fetchall()
                maximum, minimum = maxmin[0]
                maximums = max(plotBoundaries_slope[1]/sh, maximum+0.01)
                minimums = min(plotBoundaries_slope[0]/sh, minimum-0.01)
                if sh == 1:
                    maximum1 = maximums
                    minimum1 = minimums
                #Creates Canvases for each Shunt and Range(TH1D)
                c.append(TCanvas("Shunt %.1f  -  Range %i" % (sh, r), "histo"))
                c[-1].Divide(2,1)

                #Create Histograms for the shunt slopes
                histshunt.append(TH1D("SLOPE_Sh:_%.1f_RANGE_r:_%d" %(sh,r),"SLOPE Sh: %.1f RANGE r: %d" %(sh,r), 100, minimums, maximums))
                #histshunt[-1].SetTitle("SLOPE SH: %.1f "%(sh))
                histshunt[-1].GetXaxis().SetTitle("Slope")
                histshunt[-1].GetYaxis().SetTitle("Frequency")
                gPad.SetLogy(1)

                #Create 2D histogram of slope of shunt N vs slope of shunt 1
                if(options.hist2D):
                    histSlopeNvSlope1.append(TH2D("Slope_Shunt_%s_vs_Shunt_1_R_%i"%(str(sh).replace(".",""),r),"Slope of Shunt %.1f vs Shunt 1 - Range %i"%(sh,r),100,minimum1,maximum1,100,minimums,maximums))
                    histSlopeNvSlope1[-1].GetXaxis().SetTitle("Shunt 1 Slope")
                    histSlopeNvSlope1[-1].GetYaxis().SetTitle("Shunt %.1f Slope"%sh)

                #Create histogram of shunt factor
                if(options.shFac):
                    histShuntFactor.append(TH1D("ShuntFactor_Sh_%s_R_%.i"%(str(sh).replace(".",""),r),"Shunt Factor Shunt %.1f Range %i"%(sh,r),100,sh-1,sh+1))
                    histShuntFactor[-1].GetXaxis().SetTitle("Shunt Factor")
                    histShuntFactor[-1].GetYaxis().SetTitle("Frequency")
                #Create Histograms for the Offsets
                maxmin = cursor.execute("select max(offset),min(offset) from qieshuntparams where range=%i and shunt = %.1f;" % (r, sh)).fetchall()
                maximum, minimum = maxmin[0]
                maximumo  = max(plotBoundaries_offset[r], maximum)
                minimumo  = min(-1*plotBoundaries_offset[r], minimum)

                c[-1].cd(2)
                histoffset.append(TH1D("OFFSET Sh: %.1f - R: %i" %(sh, r),"Shunt %.1f - Range %d" %(sh, r), 40, minimumo, maximumo))
                histoffset[-1].SetTitle("OFFSET SH: %.1f R: %d"%(sh,r))
                histoffset[-1].GetXaxis().SetTitle("Offset")
                histoffset[-1].GetYaxis().SetTitle("Frequency")
                gPad.SetLogy(1)

                if(options.slVqie):
                    histSlvQie.append(TH2D("SlopeVsQIE_Shunt_%s_Range_%d"%(str(sh).replace(".",""),r),"Slope Vs QIE Shunt %.1f Range %d"%(sh,r),16,0.5,16.5,40,minimums,maximums))
                    histSlvQie[-1].GetXaxis().SetTitle("QIE")
                    histSlvQie[-1].GetYaxis().SetTitle("Slope")
                # Fills the histograms with the values fetched above
                for val in values:
                    #slope, offset = val
                    slope, offset,qie,capid ,slSh1 = val
                    if slopeFail(sh,r,name,slope,thshunt,THRESHOLD) or offsetFail(sh,r,offset,name):
                        if slopeFail(sh,r,name,slope) and offsetFail(sh,r,offset,name):
                            test.append({'slope':slope,'shunt':sh, 'range':r,'offset':offset,'Qie':qie,'CapID':capid,'BadSlope':1,'BadOffset':1})
                        elif slopeFail(sh,r,name,slope):
                            test.append({'slope':slope,'shunt':sh, 'range':r,'offset':offset,'Qie':qie,'CapID':capid,'BadSlope':1,'BadOffset':0})
                        elif offsetFail(sh,r,offset,name):
                            test.append({'slope':slope,'shunt':sh, 'range':r,'offset':offset,'Qie':qie,'CapID':capid,'BadSlope':0,'BadOffset':1})
                    c[-1].cd(1)
                    histshunt[-1].Fill(slope)
                    histshunt[-1].Draw()
                    c[-1].cd(2)
                    histoffset[-1].Fill(offset)
                    histoffset[-1].Draw()
                    if(options.slVqie):
                        histSlvQie[-1].Fill(qie,slope)
                    if(options.hist2D):
                        histSlopeNvSlope1[-1].Fill(slSh1,slope)
                    if(options.shFac):
                        try:
                            histShuntFactor[-1].Fill(slSh1/slope)
                        except ZeroDivisionError:
                            pass
                # Write the histograms to the file, saving them for later
                # histshunt[-1].Draw()
                # histoffset[-1].Draw()
                # c2[-1].Write()
                c[-1].Update()
                #c[-1].SaveAs("data/%s/Run_%s/SummaryPlots/ImagesOutput/CARD_%s_SHUNT_%s_RANGE_%i.png"%(date, run, name, str(sh).replace(".",""), r))
                if(options.images):
                    c[-1].Print("data/%s/Run_%s/SummaryPlots/TotalOutput/Total_SHUNT_%s_RANGE_%i.png"%(date, run, str(sh).replace(".",""), r))
                c[-1].Write()
                if(options.hist2D):
                    histSlopeNvSlope1[-1].Write()
                if(options.slVqie):
                    histSlvQie[-1].Write()
                if(options.shFac):
                    histShuntFactor[-1].Write()
                if(options.verbose):
                    print "Total Plots Shunt %.1f Range %d Finished"%(sh,r)
        FailedCards.append({'%s'%name:test})
    if len(FailedCards)>1:
        outputText = open("data/%s/Run_%s/SummaryPlots/Failed_Shunts_and_Ranges.txt"%(date,run),"w+")
        # if os.path.exists("data/%s/Run_%s/SummaryPlots/FailedCards.db"%(date,run)):
        #     os.remove("data/%s/Run_%s/SummaryPlots/FailedCards.db"%(date,run))
        # connection = sqlite3.connect("data/%s/Run_%s/SummaryPlots/FailedCards.db"%(date,run))
        # cursor1 = connection.cursor()
        # cursor1.execute("""CREATE TABLE failInfo (
        #     Card Char[30],
        #     Shunts FLOAT,
        #     Range INT,
        #     Offset FLOAT,
        #     CapID INT,
        #     QIE INT,
        #     Bad Offset Char[30],
        #     Bad Slope Char[30]);""")
        # for index in range(len(FailedCards['Card'])):
        #     cursor.execute("""INSERT INTO failInfo (Card,Shunts,Range,Offset,CapID,QIE,Label) VALUES (%s , %.1f,%i,%.1f,%i,%i,%s);"""%(FailedCards['Card'][index],FailedCards['Shunts'][index],FailedCards['Range'][index],FailedCards['Offset'][index],FailedCards['capID'][index],FailedCards['Qie'][index],FailedCards['label'][index]))
        outputText.write(str(FailedCards))
        outputText.close()
    rootout.Close()

def shuntboundaries(tuple1,sh):
    maxi , mini = tuple1
    maxis=0
    minis =0
    if sh == 0:
        if 0.28 > mini or maxi > 0.32:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .32
            minis = .28
    if sh == 1.5:
        if 0.185 > mini or maxi > 0.22:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .22
            minis = .185
    if sh == 2:
        if 0.143 > mini or maxi > 0.168:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .143
            minis = .168
    if sh == 3:
        if 0.095 > mini or maxi > 0.115:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .095
            minis = .115
    if sh == 4:
        if 0.072 > mini or maxi > 0.085:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .072
            minis = .085
    if sh == 5:
        if 0.0575 > mini or maxi > 0.068:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .05
            minis = .07
    if sh == 6:
        if 0.048 > mini or maxi > 0.064:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .048
            minis = .064
    if sh == 7:
        if 0.041 > mini or maxi > 0.05:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .041
            minis = .05
    if sh == 8:
        if 0.036 > mini or maxi > 0.044:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .036
            minis = .044
    if sh == 9:
        if 0.032 > mini or maxi > 0.039:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .032
            minis = .039
    if sh == 10:
        if 0.029 > mini or maxi > 0.035:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .029
            minis = .035
    if sh == 11:
        if 0.026 > mini or maxi > 0.032:
            maxis = maxi+(.1)
            minis = mini - (.1)
        else:
            maxis = .026
            minis = .032
    if sh == 11.5:
        if 0.025 > mini or maxi > 0.031:
            maxis = maxi+(.1)
            minis = mini-(.1)
        else:
            maxis = .025
            minis = .031
    return maxis,minis
def slopeFail(sh, r, name,slope,thshunt = .3,pct = .1):
    maxt=(thshunt/sh)+(thshunt/sh)*THRESHOLD
    mint=(thshunt/sh)-(thshunt/sh)*THRESHOLD
    failure = False
    if sh == 1:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 1.5:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 2:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 3:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 4:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 5:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 6:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 7:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 8:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 9:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 10:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 11:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    if sh == 11.5:
        if (mint > slope or slope > maxt):
            print "Slope Value in Card %s in Shunt %.1f in Range %i failed" % (name, sh, r)
            failure = True
    return failure
def offsetFail(sh,r,offset,name):
    failure= True
    if r == 0:
        if offset > -.25 or offset < -.75:
            print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
            failure=True
    if r == 1:
        if offset > 12 or offset < -12:
            print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
            failure=True
    if r == 2:
        if offset > 80 or offset < -80:
            print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
            failure=True
    if r == 3:
        if offset > 600 or offset < -600:
            print "Bad Offset in Shunt %.1f and Range %i of Card %s" %(sh,r,name)
            failure=True
    return failure

###################################################################################
uid = []
dbnames = []
arg = ''
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This produces Summary Plots for runs')
    parser.add_argument('-a','--all', action="store_true", dest='all', default=False, help = "Creates plots for all files and a combined database")
    parser.add_argument('-f','--files', action="append", dest = 'dbnames', help  = "Creates Summary Plots for a  file(s) list with -f [FILENAME] -f [FILENAME]")
    parser.add_argument('-u','--uniqueID', action="append", dest = 'uid', help  = "Creates Summary Plots for a  file(s) based on Unique IDs list with -u [UniqueID] -u [UniqueID] -u [UniqueID] (format uniqueID as '0xXXXXXXXX_0xXXXXXXXX')")
    parser.add_argument('-t','--total', action="store_true", dest="total", default = False, help = "Creates total histograms for each shunt WARNING Adapter Test Will not be done with this arg")
    parser.add_argument('-d','--date', required=True, action="append", dest="date", help = "Enter date in format XX-XX-XXXX(Required)")
    parser.add_argument('-r','--run', required=True, action="append", dest="run", type = int,help = "Enter the number run(Required)")
    parser.add_argument('-2','--hist2D',action="store_true",dest="hist2D",default=False,help="Creates 2D histogram of slope of shunt N vs. slope of shunt 1")
    parser.add_argument('-s','--shuntFactor',action="store_true",dest="shFac",default=False,help="Creates histogram of shunt factors")
    parser.add_argument('--noImages',action="store_false",dest="images",default=True,help="Do not save images")
    parser.add_argument('--verbose',action="store_true",dest="verbose",default=False,help="Print progress messages")
    options = parser.parse_args()
    SummaryPlot(options)
