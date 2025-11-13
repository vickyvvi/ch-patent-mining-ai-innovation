use 1129,clear
save 1129,replace
  

replace age=ln(age+1)
drop if AI==.
gen size=ln(firmsize+1)


rename ai AI
rename RDI RDI
rename Lev Lev
rename ROA ROA
replace AI=AI*100

****Descriptive Statistics
sum score AI RDI Lev ROA size age
logout,save(Descriptive Statistics)word replace: tabstat score AI RDI Lev ROA size age,s(N mean sd min p50 max) f(%12.3f) c(s)

****Correlation Analysis
spearman score AI RDI Lev ROA size age,star(0.1)
corr2docx score AI RDI Lev ROA size age using corresult.docx, replace star pearson(ignore)  //If the command is not installed, execute: ssc install corr2docx before this command

reg score AI RDI Lev ROA size age
vif
****Baseline Regression
reghdfe score AI ,noabsorb vce(r)
est store a1
reghdfe score AI ,absorb(year ind) vce(r)
est store a2
reghdfe score AI RDI Lev ROA size age,noabsorb vce(r)
est store a3
reghdfe score AI RDI Lev ROA size age,absorb(ind year) vce(r)
est store a4
esttab a1 a2 a3 a4 using Baseline Regression.rtf,replace ar2 compress nogap star(* 0.10 ** 0.05 *** 0.01) b(%9.4f) t(%9.4f) ar2(%9.4f) 

***Robustness Check
***Shortening Sample Period
reghdfe score AI RDI Lev ROA size age if year>=2017,absorb(ind year) vce(r)
est store a1
esttab a1 using Shortening Sample Period.rtf,replace ar2 compress nogap star(* 0.10 ** 0.05 *** 0.01) b(%9.4f) t(%9.4f) ar2(%9.4f) 

***Winsorization
winsor2 score AI RDI Lev ROA firmsizeNumberofemployeesa age,cuts(5 95) replace
reghdfe score AI RDI Lev ROA size age,absorb(ind year) vce(r)
est store a2
winsor2 score AI RDI Lev ROA firmsizeNumberofemployeesa age,cuts(10 90) replace
reghdfe score AI RDI Lev ROA size age,absorb(ind year) vce(r)
est store a3
esttab a2 a3 using Robustness Check.rtf,replace ar2 compress nogap star(* 0.10 ** 0.05 *** 0.01) b(%9.4f) t(%9.4f) ar2(%9.4f) 

****Heterogeneity
use 1129,clear
reghdfe score AI RDI Lev ROA size age if size>=8.85462,absorb(ind year) vce(r)
est store a1
reghdfe score AI RDI Lev ROA size age if size<=8.85462,absorb(ind year) vce(r)
est store a2
esttab a1 a2 using Heterogeneity.rtf,replace ar2 compress nogap star(* 0.10 ** 0.05 *** 0.01) b(%9.4f) t(%9.4f) ar2(%9.4f) 
