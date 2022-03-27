import os
import numpy as np
#import pymetis
#from pymetis._internal import part_graph  # always do this before importing openseespy

import sfsimodels as sm
import o3seespy as o3
import time

import sys

if len(sys.argv) < 3:
    if len(sys.argv) < 2:
        raise ValueError('Need two extra args')
    raise ValueError('Need one extra arg')

etype = sys.argv[1]
allowed_etypes = ['implicit', 'newmark_explicit', 'central_difference', 'explicit_difference']
if etype not in allowed_etypes:
    raise ValueError(f'etype={etype}, must be one of: ' + ','.join(allowed_etypes))
sys_w = int(sys.argv[2])

nprocs = o3.mp.get_np()
pid = o3.mp.get_pid()
o3.wipe()

name = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
name = name.replace('flat_', '')
if name == '<input>':
    name = 'free_vib_fe3d_elastic'
version = 'v4_intel'
out_folder = f'{version}/'
print('out_folder: ', out_folder)
if pid == 0:
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

# Define system
loop = 4.0  # length out of plane
sys_h = 16.0

f1 = 0.8
f2 = 20.0
xi = 0.03

prefix_w_e = f'MW{sys_w}-np{nprocs}-{etype}'
prefix = f'MW{sys_w}-np{nprocs}'

if pid == 0:
    start_time = time.time()
    with open(f'{out_folder}{prefix_w_e}-time.txt', 'w') as tfile:
        tfile.write(f'start: {time.time()}\n')


tds = sm.TwoDSystem(width=sys_w, height=sys_h)
tds.id = 1
tds.x_surf = [0, sys_w]
tds.y_surf = np.zeros_like(tds.x_surf)
tds.loop = loop  # m (length out of plane)
f_order = 1.0e3  # scales the numerical model
dy = 0.5  # Target mesh element height
tds.f_order = f_order
tds.dy = dy
tds.inputs += ['f_order', 'dy']


# Define a soil profile
sp = sm.SoilProfile()
sp.x_angles = [0.0, 0.0]
tds.add_sp(sp, 0)
sp.height = sys_h

# Define a soil
sl = sm.Soil()
vs = 150.
unit_mass = 1700.0
sl.g_mod = vs ** 2 * unit_mass
sl.poissons_ratio = 0.3
sl.unit_dry_weight = unit_mass * 9.8
sp.add_layer(0.0, sl)
e_mod = 2 * sl.g_mod * (1 + sl.poissons_ratio) / f_order
# Create o3 soil instance
soil_mat = o3.nd_material.ElasticIsotropic(None, e_mod, nu=sl.poissons_ratio, rho=sl.unit_dry_mass / f_order)

# Define a finite element mesh
fem = sm.num.mesh.construct_femesh_orth(tds, dy_target=dy)

# Export engineering consistency parameters file
if pid == 0:
    eo = sm.Output()
    eo.add_to_dict(tds)
    eo.to_file(out_folder + f'{prefix}-ecp.json')

# Determine crtical time step
sp.gen_split(props=['unit_mass', 'shear_vel', 'poissons_ratio', 'g_mod'])
g_mod = sp.split['g_mod']
poi = sp.split['poissons_ratio']
rho = sp.split['unit_mass']
e_mod = 2 * g_mod * (1 + poi)
lam = (e_mod * poi) / ((1 + poi) * (1 - 2 * poi))
mu = g_mod  # note this is different to abaqus doc.
v_dil = np.sqrt((lam + 2 * mu) / rho)
y_split = sp.split['depth']
y_eles = (fem.y_nodes[1:] + fem.y_nodes[:-1]) / 2
v_dil_ele = np.interp(-y_eles, y_split, v_dil)
ele_h = -np.diff(fem.y_nodes)
dts = ele_h / v_dil_ele
min_dh = min(ele_h)
min_dt = min(dts)

w1 = 2 * np.pi * f1
w2 = 2 * np.pi * f2
a0 = 2 * xi * w1 * w2 / (w1 + w2)  # mu (mass term)
a1 = 2 * xi / (w1 + w2)  # Lambda (stiffness term)

fmax = 1. / min_dt
omega_max = 2 * np.pi * fmax
xi_at_fmax = 0.5 * (a0 / omega_max + a1 * omega_max)

lam = 0.4 * a1 / min_dt
cf = (np.sqrt(1 + lam ** 2) - lam)
min_dt_adj = min_dt * (np.sqrt(1 + lam ** 2) - lam)


min_dt_w_xi = (np.sqrt(xi_at_fmax ** 2 + 1) - xi_at_fmax) * min_dt
print('fmax: ', fmax)
print('xi_at_fmax: ', xi_at_fmax)
print('min_dt_w_xi: ', min_dt_w_xi, min_dt)

if pid == 0:
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
if nprocs > 1:
    if pid == 0:
        try:
            partitions = np.loadtxt(f'partitions/{prefix}-partitions.txt')
        except IOError:
            partitions = None
            pass
        if partitions is None:
            erows = len(fem.soil_grid)
            ecols = len(fem.soil_grid[0])

            es = np.arange(0, erows * ecols, 1)
            eles = np.reshape(es, [erows, ecols])
            eles = np.where(fem.soil_grid != fem.inactive_value, eles, -1)
            g_adjs, mlist = o3.mptools.build_graph_links(eles)

            n_cuts, parts = pymetis.part_graph(nprocs, adjacency=g_adjs)
            partitions = np.reshape(parts, [erows, ecols])
            partitions = np.where(fem.soil_grid == fem.inactive_value, nprocs + 100, partitions)
            try:
                os.makedirs('partitions')
            except FileExistsError:
                pass
            np.savetxt(f'partitions/{prefix}-partitions.txt', partitions, fmt='%.0f')
    o3.mp.barrier()
#mass prop damp - cen diff uses mpidiagonal
femesh = fem
close_on_write = False

if nprocs == 1:
    mp = False
else:
    mp = True
state = 0

ind_zslice = 0
# Establish nodes
femesh_z_nodes = np.linspace(0, loop, int(loop / dy))

anodes = femesh.get_active_nodes()
nx = len(anodes)
ny = len(anodes[1])
nz = len(femesh_z_nodes)
femesh_nnz = nz
print('n_nodes: ', nx * ny * nz)
print('nprocs: ', nprocs)

if pid == 0:
    import os
    if not os.path.exists(out_folder):
        print(f'Making directory: {out_folder}')
        try:
            os.makedirs(out_folder)
        except FileExistsError:
            pass
if nprocs == 1:
    pass
else:
    partitions = np.loadtxt(f'partitions/{prefix}-partitions.txt')
    partitions = partitions.astype(int)
    nodes_in_partition = o3.mptools.build_nodes_in_partition_2dmatrix(ele_partitions=partitions, pid=pid)
    anodes = np.where(nodes_in_partition, anodes, 0)
active = anodes[:, :, np.newaxis] * np.ones((femesh.nnx, femesh.nny, nz))
ntags = np.reshape(np.arange(1, nx * ny * nz + 1, dtype=np.int32), [nx, ny, nz])
tot_tags = int(nx * ny * nz + 1)

if pid == 0:
    with open(f'{out_folder}{prefix_w_e}-time.txt', 'a') as tfile:
        tfile.write(f'init-delta: {time.time()-start_time}\n')

osi = o3.OpenSeesInstance(ndm=3, ndf=3, state=state, mp=mp)
osi.n_node = tot_tags
print('build nodes')
sn = o3.node.build_regular_node_mesh(osi, femesh.x_nodes, femesh.y_nodes, femesh_z_nodes,
                                     active=active, tags=ntags)
print('fixing nodes')
# Fix base nodes
o3.Fix3DOFMulti(osi, sn[:, -1, :].flatten(), o3.cc.FIXED, o3.cc.FIXED, o3.cc.FIXED, is_none=False)
# Fix vertical edges
o3.Fix3DOFMulti(osi, sn[0, :-1, 0], o3.cc.FIXED, o3.cc.FREE, o3.cc.FIXED, is_none=False)
o3.Fix3DOFMulti(osi, sn[0, :-1, -1], o3.cc.FIXED, o3.cc.FREE, o3.cc.FIXED, is_none=False)
o3.Fix3DOFMulti(osi, sn[-1, :-1, 0], o3.cc.FIXED, o3.cc.FREE, o3.cc.FIXED, is_none=False)
o3.Fix3DOFMulti(osi, sn[-1, :-1, -1], o3.cc.FIXED, o3.cc.FREE, o3.cc.FIXED, is_none=False)
# Fix Left and Right face (except front, back and bottom edges)
o3.Fix3DOFMulti(osi, sn[0, 1:-1, 1:-1].flatten(), o3.cc.FIXED, o3.cc.FREE, o3.cc.FREE, is_none=False)
o3.Fix3DOFMulti(osi, sn[-1, 1:-1, 1:-1].flatten(), o3.cc.FIXED, o3.cc.FREE, o3.cc.FREE, is_none=False)
# Fix reflected face (except left, right and bottom edges)
o3.add_fixity_to_dof(osi, o3.cc.DOF3D_Z, sn[1:-1, :-1, 0].flatten())
# Fix back face (except left, right and bottom edges)
o3.add_fixity_to_dof(osi, o3.cc.DOF3D_Z, sn[1:-1, :-1, -1].flatten())

grav = 9.8
soil_mat.build(osi)
eles = []
for zz in range(femesh_nnz - 1):
    for yy in range(femesh.nny - 1):
        for xx in range(femesh.nnx - 1):
            # def element
            nodes = [sn[xx][yy + 1][zz + 1], sn[xx + 1][yy + 1][zz + 1],  # left-bot-front -> right-bot-front
                     sn[xx + 1][yy + 1][zz], sn[xx][yy + 1][zz],  # right-bot-back -> left-bot-back
                     sn[xx][yy][zz + 1], sn[xx + 1][yy][zz + 1],  # left-top-front -> right-top-front
                     sn[xx + 1][yy][zz], sn[xx][yy][zz]  # right-top-back -> left-top-back
                     ]
            if None not in nodes:
                eles.append(o3.element.SSPbrick(osi, nodes, soil_mat, 0.0, -grav, 0.0))


#%%
print('wiping analysis settings')
o3.wipe_analysis(osi)
# # Analysis settings
o3.constraints.Transformation(osi)
o3.test.NormDispIncr(osi, tol=1.0e-5, max_iter=20, p_flag=0, n_type=0)
print('apply numberer')
o3.numberer.apply_rcm(osi)
o3.rayleigh.Rayleigh(osi, alpha_m=a0, beta_k=0.0, beta_k_init=a1, beta_k_comm=0.0)
o3.algorithm.Linear(osi, factor_once=True)
if etype == 'implicit':
    o3.system.apply_mumps_or(osi, o3.system.SparseSYM, icntl14=200)
    o3.integrator.Newmark(osi, 0.5, 0.25)
else:
    if etype == 'newmark_explicit':
        o3.system.apply_mumps_or(osi, o3.system.SparseSYM, icntl14=200)
        o3.integrator.NewmarkExplicit(osi, gamma=0.5)
    elif etype == 'central_difference':
        o3.system.apply_mumps_or(osi, o3.system.SparseSYM, icntl14=200)
        o3.integrator.CentralDifference(osi)
    elif etype == 'explicit_difference':
        o3.system.MPIDiagonal(osi)
        o3.integrator.ExplicitDifference(osi)
    else:
        raise ValueError(etype)
explicit_dt = 0.9 * min_dt
ndp = np.ceil(np.log10(explicit_dt))
if 0.5 * 10 ** ndp < explicit_dt:
    dt = 0.5 * 10 ** ndp
elif 0.2 * 10 ** ndp < explicit_dt:
    dt = 0.2 * 10 ** ndp
elif 0.1 * 10 ** ndp < explicit_dt:
    dt = 0.1 * 10 ** ndp
else:
    raise ValueError(explicit_dt, 0.1 * 10 ** ndp)
o3.analysis.Transient(osi)
rnodes = sn[int(femesh.nnx / 2), :, int(femesh_nnz / 2)]

rnodes = [node for node in rnodes if node is not None]
with open(f'{out_folder}{prefix}-y-rnodes-pid{pid}.txt', 'w') as rfile:
    rfile.write('\n'.join([str(node.y) for node in rnodes]))
o3.recorder.NodesToFile(osi, f'{out_folder}{prefix_w_e}-nfr-pid{pid}.txt', rnodes, [o3.cc.DOF2D_Y], 'disp')
print('Start analysis')
if pid == 0:
    with open(f'{out_folder}{prefix_w_e}-time.txt', 'a') as tfile:
        tfile.write(f'init-os-delta: {time.time()-start_time}\n')
#%%
if o3.analyze(osi, 10, dt):
    if pid == 0:
        with open(f'{out_folder}{prefix_w_e}-time.txt', 'a') as tfile:
            tfile.write('MODEL FAILED\n')
    print('MODEL FAILED')

if pid == 0:
    with open(f'{out_folder}{prefix_w_e}-time.txt', 'a') as tfile:
        tfile.write(f'complete-delta: {time.time()-start_time}\n')
