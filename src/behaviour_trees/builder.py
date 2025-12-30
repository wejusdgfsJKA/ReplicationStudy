import py_trees


def make_ppa(name, action, postcondition=None, preconditions=None):
    seq = py_trees.composites.Sequence("PPA_Seq", memory=False)

    # Add preconditions
    if preconditions:
        for prec in preconditions:
            seq.add_child(prec)

    # Add the action itself
    seq.add_child(action)

    # Selector: postcondition first, then sequence
    root = py_trees.composites.Selector(name, memory=False)
    if postcondition:
        root.add_child(postcondition)
    root.add_child(seq)

    return root
