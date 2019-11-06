#~/bin/sh
grep -a -r -i --include '*.out' "NORM. CHI" | awk '{print $1,$2,$9}' > normChiSquared.dat
