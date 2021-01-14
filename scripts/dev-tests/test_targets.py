from subprocess import Popen ,PIPE

args = ["cors2ascii", "swift://data-telescope-meta-dos/datasource=ucsd-nt/year=2020/month=5/day=8/ucsd-nt.1588953600.dos.cors.gz", " | egrep -o '^([0-9]{1,3}\.){3}[0-9]{1,3}\\b'" ]

process = Popen(args=args, stdout=PIPE, shell=True)

print([ip.strip() for ip in process.stdout])