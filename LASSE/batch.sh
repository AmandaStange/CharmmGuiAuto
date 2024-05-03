#Assumes yamls are named 1..4

outfile='log'
> "$outfile"

path=LASSE

sleep 1

for i in {1..4}; do
    python -u  CharmmGuiAuto.py -i ${path}/${i}.yaml  >>$outfile 2>&1 &
done

obids_outfile='jobids.txt'
> "$jobids_outfile"


while [ $(cat $jobids_outfile | wc -l) -lt 4 ]; do
    grep JOBID $outfile | awk '{print $NF}' > $jobids_outfile
done

for i in $(cat $jobids_outfile); do
    sed "s/JOBID/$i/g"  ${path}/Retrieve.yaml > ${path}/${i}_retrieve.yaml
    python -u  CharmmGuiAuto.py -i ${path}/${i}_retrieve.yaml  >>log_retrieve 2>&1 &
done



