from subprocess import Popen ,PIPE

args = "swift list data-telescope-meta-dos -p datasource=ucsd-nt/year=2020/month=5/day=8/"

process = Popen(args=args, stdout=PIPE, shell=True)

print([file.strip() for file in process.stdout])