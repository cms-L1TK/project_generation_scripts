// -------------------------------------------------------------------
// Draw diagram of modules used in tracklet track finding
// By A. Ryd, Jan 2015  
// -------------------------------------------------------------------

#include "TROOT.h"
#include "TStyle.h"
#include "TLatex.h"
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TBranch.h"
#include "TLeaf.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TH1.h"
#include "TH2.h"
#include "TF1.h"
#include "TProfile.h"
#include "TProfile2D.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "TGraphErrors.h"
#include "TPaveText.h"

#include <fstream>
#include <string>
#include <vector>

double textsize=1.0;

class DrawBase{

  friend class Box;
  friend class Hex;


public:

  DrawBase(){
    x1_=0.0;
    x2_=0.0;
    y1_=0.0;
    y2_=0.0;
    name_="";
  }

  virtual ~DrawBase() {}

  DrawBase(double x1, double y1, double x2, double y2, TString name) {
    x1_=x1;
    x2_=x2;
    y1_=y1;
    y2_=y2;
    name_=name;
  }

  void virtual Draw()=0;

  TString getName() {
    return name_;
  }

  void DrawConnection(const DrawBase& otherDrawBase) {
    TLine* l=new TLine(x2_,0.5*(y1_+y2_),
		      otherDrawBase.x1_,
		       0.5*(otherDrawBase.y1_+otherDrawBase.y2_));
    l->SetLineWidth(1);
    l->Draw();
  }




private:

  double x1_;
  double x2_;
  double y1_;
  double y2_;
  TString name_;

};

class Box:public DrawBase{

public:

  Box() {}

  Box(double x1, double y1, double x2, double y2, 
      TString name,unsigned int theMultiplicity=1):DrawBase(x1,y1,x2,y2,name){
    multiplicity_=theMultiplicity;
    seq_=0;
  }

  unsigned int multiplicity() const { return multiplicity_; } 

  TString getName(unsigned int i=0) const { 
    TString tmp=name_;
    if (i!=0) {
      tmp+="n";
      tmp+=i;
    }
    return tmp;
  } 

  TString getNameSeq() { 
    TString tmp=name_;
    seq_++;
    tmp+="n";
    tmp+=seq_;
    
    return tmp;
  } 

  void Draw() {
    TLine* l1=new TLine(x1_,y1_,x2_,y1_);
    l1->SetLineColor(kBlue);
    l1->Draw();
    TLine* l2=new TLine(x1_,y1_,x1_,y2_);
    l2->SetLineColor(kBlue);
    l2->Draw();
    TLine* l3=new TLine(x2_,y2_,x2_,y1_);
    l3->SetLineColor(kBlue);
    l3->Draw();
    TLine* l4=new TLine(x2_,y2_,x1_,y2_);
    l4->SetLineColor(kBlue);
    l4->Draw();    
    //TPaveText* t1=new TPaveText(x1_,y1_,x2_,y2_,"NB"); 
    //t1->AddText(name_);
    //t1->Draw();
    double dytmp=fabs(y1_-y2_);
    TString name=name_;
    if (multiplicity_>1){
      name+="n";
      name+=1;
      name+="..";
      name+=multiplicity_;
    }
    TText *t1 = new TText(x1_+0.1*dytmp,y1_+0.2*dytmp,name);
    t1->SetTextAlign(11); t1->SetTextSize(textsize);
    t1->Draw();

  }

private:

  unsigned int multiplicity_;

  unsigned int seq_;

};


class Hex:public DrawBase{

public:

  Hex(){
    x1_=0.0;
    x2_=0.0;
    y1_=0.0;
    y2_=0.0;
    name_="";
  }

  Hex(double x1, double y1, double x2, double y2, TString name) {
    x1_=x1;
    x2_=x2;
    y1_=y1;
    y2_=y2;
    name_=name;
  }

  void Draw() {
    double dytmp=fabs(y1_-y2_);
    double y=0.5*(y1_+y2_);
    TLine* l1=new TLine(x1_,y,x1_+0.25*dytmp,y1_);
    l1->SetLineColor(kRed);
    l1->Draw();
    TLine* l2=new TLine(x1_,y,x1_+0.25*dytmp,y2_);
    l2->SetLineColor(kRed);
    l2->Draw();
    TLine* l3=new TLine(x1_+0.25*dytmp,y1_,x2_-0.25*dytmp,y1_);
    l3->SetLineColor(kRed);
    l3->Draw();
    TLine* l4=new TLine(x1_+0.25*dytmp,y2_,x2_-0.25*dytmp,y2_);
    l4->SetLineColor(kRed);
    l4->Draw();
    TLine* l5=new TLine(x2_,y,x2_-0.25*dytmp,y1_);
    l5->SetLineColor(kRed);
    l5->Draw();
    TLine* l6=new TLine(x2_,y,x2_-0.25*dytmp,y2_);
    l6->SetLineColor(kRed);
    l6->Draw();
    //TPaveText* t1=new TPaveText(x1_,y1_,x2_,y2_,"NDCARCNB"); 
    //t1->AddText(name_);
    //t1->Draw();
    TText *t1 = new TText(x1_+0.25*dytmp,y1_+0.2*dytmp,name_);
    t1->SetTextAlign(11); t1->SetTextSize(textsize);
    t1->Draw();

  }

private:

};



using namespace std;

void SetPlotStyle();

// Main script
void DrawSubProject() {

  ifstream diagram("smallgraph.dat");

  TString procname;

  diagram >> procname;

  cout << procname <<endl;

  std::vector<TString> inmem;
  std::vector<TString> outmem;

  TString type, mem;


  do {

    diagram >> type >> mem;

    if (!diagram.good()) continue;

    if (type=="in") inmem.push_back(mem);
    if (type=="out") outmem.push_back(mem);
    
  } while (diagram.good());


  cout << "inmem.size() = "<<inmem.size()<<endl;
  cout << "outmem.size() = "<<outmem.size()<<endl;


  unsigned int nbox=inmem.size();
  if (nbox<outmem.size()) {
    nbox=outmem.size(); 
  }


  TCanvas* c1=new TCanvas("c1","c1",20,20,800,50*(nbox+1));

  textsize=0.35/(nbox+1);
  double dy=0.5/(nbox+1);

  double dy1=0.70*dy;  

  Hex *proc= new Hex(0.38,0.5-0.5*dy,0.62,0.5+0.5*dy,procname);
  proc->Draw();
  
  for(unsigned int i=0;i<inmem.size();i++) {
    double y=0.5+1.5*dy1*(inmem.size()-1)-3*dy1*i;
    Box *membox= new Box(0.05,y-0.5*dy,0.32,y+0.5*dy,inmem[i]);
    membox->Draw();
    TLine *line= new TLine(0.32,y,0.38,0.5);
    line->Draw();
  }


  for(unsigned int i=0;i<outmem.size();i++) {
    double y=0.5+1.5*dy1*(outmem.size()-1)-3*dy1*i;
    Box *membox= new Box(0.68,y-0.5*dy,0.98,y+0.5*dy,outmem[i]);
    membox->Draw();
    TLine *line= new TLine(0.62,0.5,0.68,y);
    line->Draw();
  }

  



    

  c1->Print("TrackletSubProject_"+procname+".pdf");
  
}



void SetPlotStyle() {

  // from ATLAS plot style macro

  // use plain black on white colors
  gStyle->SetFrameBorderMode(0);
  gStyle->SetFrameFillColor(0);
  gStyle->SetCanvasBorderMode(0);
  gStyle->SetCanvasColor(0);
  gStyle->SetPadBorderMode(0);
  gStyle->SetPadColor(0);
  gStyle->SetStatColor(0);
  gStyle->SetHistLineColor(1);

  gStyle->SetPalette(1);

  // set the paper & margin sizes
  gStyle->SetPaperSize(20,26);
  gStyle->SetPadTopMargin(0.05);
  gStyle->SetPadRightMargin(0.05);
  gStyle->SetPadBottomMargin(0.16);
  gStyle->SetPadLeftMargin(0.16);

  // set title offsets (for axis label)
  gStyle->SetTitleXOffset(1.4);
  gStyle->SetTitleYOffset(1.4);

  // use large fonts
  gStyle->SetTextFont(42);
  gStyle->SetTextSize(0.05);
  gStyle->SetLabelFont(42,"x");
  gStyle->SetTitleFont(42,"x");
  gStyle->SetLabelFont(42,"y");
  gStyle->SetTitleFont(42,"y");
  gStyle->SetLabelFont(42,"z");
  gStyle->SetTitleFont(42,"z");
  gStyle->SetLabelSize(0.05,"x");
  gStyle->SetTitleSize(0.05,"x");
  gStyle->SetLabelSize(0.05,"y");
  gStyle->SetTitleSize(0.05,"y");
  gStyle->SetLabelSize(0.05,"z");
  gStyle->SetTitleSize(0.05,"z");

  // use bold lines and markers
  gStyle->SetMarkerStyle(20);
  gStyle->SetMarkerSize(1.2);
  gStyle->SetHistLineWidth(2.);
  gStyle->SetLineStyleString(2,"[12 12]");

  // get rid of error bar caps
  gStyle->SetEndErrorSize(0.);

  // do not display any of the standard histogram decorations
  gStyle->SetOptTitle(0);
  gStyle->SetOptStat(0);
  gStyle->SetOptFit(0);

  // put tick marks on top and RHS of plots
  gStyle->SetPadTickX(1);
  gStyle->SetPadTickY(1);

}


void mySmallText(Double_t x,Double_t y,Color_t color,char *text) {
  Double_t tsize=0.044;
  TLatex l;
  l.SetTextSize(tsize); 
  l.SetNDC();
  l.SetTextColor(color);
  l.DrawLatex(x,y,text);
}


