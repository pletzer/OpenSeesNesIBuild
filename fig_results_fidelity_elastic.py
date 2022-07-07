import numpy as np
import matplotlib.pyplot as plt
import all_paths as ap
from bwplot import cbox, lsbox
import engformat as ef

def create(save=0, show=0):
    etypes = ['explicit_difference', 'central_difference', 'implicit']
    etypes = ['central_difference', 'explicit_difference']
    etypes = ['central_difference']
    vs = ['v5', 'v5a']

    nps = [2, 4, 8, 16, 32]

    bw = 8  # benchmark width
    # etypes = ['explicit_difference']
    for ee, etype in enumerate(etypes):
        bf, ax = plt.subplots(nrows=1)
        mw = 8
        nprocs = 8
        name = 'free_vib_fe3d_elastic'
        version = 'v5a'
        version = vs[ee]
        out_folder = f'{ap.OP_VDATA_PATH}fe3d/{name}/{version}/'
        for nn, nprocs in enumerate(nps):
            mw = nprocs

            for pp in range(nprocs):
                data = np.loadtxt(f'{out_folder}MW{mw}-np{nprocs}-{etype}-nfr-pid{pp}.txt')
                ydata = np.loadtxt(f'{out_folder}MW{mw}-np{nprocs}-y-rnodes-pid{pp}.txt')
                # ys = data + ydata[np.newaxis, :]
                ys = data
                plt.plot(ys, c=cbox(nn), ls=lsbox(nn), label=f"{etype} MW{mw}-np{nprocs}")
        # plt.plot(data[-1])
        # plt.plot(data[:, 0])

        ef.revamp_legend(ax)
        plt.show()

if __name__ == '__main__':
    create(save=1, show=1)