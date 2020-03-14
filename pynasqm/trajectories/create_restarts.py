from functools import singledispatch

@singledispatch
def create_restarts_from_parent(traj_data, restart, override):
    raise NotImplementedError("Create Restart Not Support for This Traj Type")

