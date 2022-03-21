
import opensees as ops


def run(stype):

    pid = ops.getPID()
    np = ops.getNP()
    ops.start()
    split = 1
    if np < 2 and split:
        split = 0

    ops.model('basic', '-ndm', 2, '-ndf', 2)
    ops.uniaxialMaterial('Elastic', 1, 3000.0)

    if pid == 0 and split:
        ops.node(1, 0.0, 0.0)
        ops.node(4, 72.0, 96.0)

        ops.fix(1, 1, 1)
        ops.mass(4, 100.0, 100.0)

        ops.element('Truss', 1, 1, 4, 10.0, 1)
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        ops.load(4, 100.0, -50.0)

    elif pid == 1 and split:
        ops.node(2, 144.0, 0.0)
        ops.node(3, 168.0, 0.0)
        ops.node(4, 72.0, 96.0)

        ops.fix(2, 1, 1)
        ops.fix(3, 1, 1)
        ops.mass(4, 100.0, 100.0)

        ops.element('Truss', 2, 2, 4, 5.0, 1)
        ops.element('Truss', 3, 3, 4, 5.0, 1)
    elif pid == 0 and not split:
        ops.node(1, 0.0, 0.0)
        ops.node(2, 144.0, 0.0)
        ops.node(3, 168.0, 0.0)
        ops.node(4, 72.0, 96.0)

        ops.fix(1, 1, 1)
        ops.fix(2, 1, 1)
        ops.fix(3, 1, 1)
        ops.mass(4, 100.0, 100.0)

        ops.element('Truss', 1, 1, 4, 10.0, 1)
        ops.element('Truss', 2, 2, 4, 5.0, 1)
        ops.element('Truss', 3, 3, 4, 5.0, 1)
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        ops.load(4, 100.0, -50.0)
    else:
        pass

    ops.constraints('Transformation')
    ops.numberer('ParallelPlain')
    ops.test('NormDispIncr', 1e-6, 6, 2)
    ops.algorithm('Linear')

    ops.system(stype)
    ops.integrator('ExplicitDifference')
    ops.analysis('Transient')
    for i in range(30):
        # print(f'######################################## run {i} ##')
        ops.analyze(1, 0.000001)
    print('PPP')
    ops.analyze(20, 0.000001)

    if pid == 0:
        print("COMPLETED")
        print('Node 4: ', [ops.nodeCoord(4), ops.nodeDisp(4)])
    ops.wipe()
    # ops.stop()
    # export TMPDIR=/tmp


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        raise ValueError('Need one extra arg')
    s_allowed = ['BandGeneral', 'SparseGeneral', 'SparseSYM', 'FullGeneral', 'UmfPack', 'SuperLU', 'SProfileSPD', 'ProfileSPD',
                 'ParallelProfileSPD', 'MPIDiagonal', 'Mumps']
    s_para = ['MPIDiagonal', 'Mumps', 'ParallelProfileSPD']
    s_val = sys.argv[1]
    if s_val not in s_allowed:
        raise ValueError(f'stype of {s_val} not in {s_allowed}')
    np = ops.getNP()
    if np > 1 and s_val not in s_para:
        raise ValueError(f'for np>1 - stype of {s_val} not in {s_para}')

    run(s_val)
