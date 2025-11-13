*****熵权法合成指标
	global positiveVar  degital RDSpendSumRatio PPE patent
	global negativeVar 
	global allVar $positiveVar 
*----------以下不用修改----------*

bysort degital: gen N = _N
*step 1:数据标准化
*标准化正向指标
foreach v in $positiveVar {
	qui sum `v'
	gen z_`v' = (`v'-r(min))/(r(max)-r(min))
	replace z_`v' = 0.0001 if z_`v' == 0
}
*标准化负向指标
foreach v in $negativeVar {
	qui sum `v'
	gen z_`v' = (r(max)-`v')/(r(max)-r(min))
	replace z_`v' = 0.0001 if z_`v' == 0
}
*step2：计算各指标比重p
foreach v  {
	egen sum_`v' = sum(z_`v')
	gen p_`v' = z_`v' / sum_`v'
}	
*step3：计算熵值e，这里的N为实际使用的样本数量
foreach v  {
	egen sump_`v' = sum(p_`v'*ln(p_`v'))
	gen e_`v' = -1 / ln(N) * sump_`v'
}	
*step4：计算信息效用值d
foreach v in $allVar {
	gen d_`v' = 1 - e_`v'
}
*step4： 计算各指标权重w
egen sumd = rowtotal(d_*)
foreach v in $allVar {
	gen w_`v' = d_`v' / sumd
}

*step5：计算各样本的综合得分
foreach v in $allVar {
    gen score_`v' = w_`v' * z_`v'
}
egen score = rowtotal(score*)

drop z_* p_* e_* d_* sum*
