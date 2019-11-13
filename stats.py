import argparse
import os

parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--log_file', type=str, default='', help='path to log file')
parser.add_argument('--n', type=int, default=4800, help='how many in one iteration')

args=parser.parse_args()
log_file=args.log_file
N=args.n


log_file2='/tmp/nn_log.txt'
cmd_str='sed -n /neural/p '+log_file+' >'+log_file2

print(cmd_str)
os.system(cmd_str)
#print('stats from', log_file2)
res_dict={}
with open(log_file2, 'r') as f:
    ite=0
    cnt=0
    s=0.0
    sum_step=0
    #print('#iteration average_winrate average_num_steps')
    for line in f:
        arr=line.split()
        res=float(arr[6])
        res=max(0,res)
        sum_step +=int(arr[-1])
        s +=res
        cnt +=1
        if cnt == N:
            #print('%d %f %f'%(ite, s/cnt, sum_step/cnt))
            res_dict[ite]=[s/cnt,sum_step/cnt]
            cnt=0
            ite +=1
            s = 0.0
            sum_step=0

os.system('rm '+log_file2)

log_file3='/tmp/nn_log_loss.txt'
cmd_str3='sed -n /Average/p '+log_file+' >'+log_file3
print(cmd_str3)
os.system(cmd_str3)
#print('stats from ', log_file3)
print('#iteration average_winrate average_num_steps average_loss')
with open(log_file3, 'r') as f:
    #print('#iteration average_loss')
    ite=0
    for line in f:
        arr=line.split()
        res=float(arr[-1])
        print('%d %f %f %f'%(ite, res_dict[ite][0], res_dict[ite][1], res))
        ite +=1

os.system('rm '+log_file3)

