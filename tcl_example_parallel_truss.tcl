
set pid [getPID]
set np [getNP]
start

if (np < 2):
    exit

model basic -ndm 2 -ndf 2
uniaxialMaterial Elastic 1 3000.0

if {pid == 0}{
    node 1 0.0 0.0
    node 4 72.0 96.0

    fix 1 1 1
    mass 4 100.0 100.0

    element Truss 1 1 4 10.0 1
    timeSeries Linear 1
    pattern Plain 1 1 {
    load 4 100.0 -50.0
    }

}else if {pid == 1}{
    node 2 144.0 0.0
    node 3 168.0 0.0
    node 4 72.0 96.0

    fix 2 1 1
    fix 3 1 1
    mass 4 100.0 100.0

    element Truss 2 2 4 5.0 1
    element Truss 3 3 4 5.0 1
}

constraints Transformation
numberer ParallelPlain
test NormDispIncr 1e-6 6 2
algorithm Linear
system Diagonal
integrator ExplicitDifference
analysis Transient
for {set k 0} {$k <= 30} {incr k 1} {
    analyze 1 0.000001

analyze 21 0.000001

if pid == 0:
    print COMPLETED
    set nc nodeCoord 4
    set nd nodeDisp 4
    puts "Node 4:  $nc $nd"
wipe

