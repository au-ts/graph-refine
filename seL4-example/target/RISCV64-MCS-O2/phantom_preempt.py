# Loop heads whose back edge is dominated by a preemptionPoint() call.
# Unpreemptible loops go in assumed_loop_bounds.py.
# Always list heads, never True.

functions = {
    # preemption point at 0x8400ce08, below the head
    'cteRevoke':            [0x8400ce28],

    # preemption point at 0x8400caa0
    'finaliseSlot':         [0x8400c980],

    # preemption point at 0x84010678
    'invokeUntyped_Retype': [0x8401064c],
}
