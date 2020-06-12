import os
from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption

@singledispatch
def check_trajins(traj_data, trajins):
    raise NotImplementedError(f"traj_data type not supported by check_trajins\n"\
                              f"{traj_data}")

@check_trajins.register(Fluorescence)
@check_trajins.register(Absorption)
def _(traj_data, trajins):
    f_trajins = [trajin for trajin in trajins if os.path.isfile(trajin[1])]
    if not f_trajins:
        raise RuntimeError(f"{trajin} was not found, make sure you ran the previous step: \n"\
                           f"mm_ground_state ->  qm_ground_state ->  absorption -> excited_state -> fluorescence\n"\
                           f"                                    -> pulse_pump \n")
    return f_trajins

# @check_trajins.register(QmGround)
# @check_trajins.register(QmExcited)
# @check_trajins.register(PPump)
# def _(traj_data, trajins):
#     for trajin in trajins:
#         if not os.path.isfile(trajin):
#             raise RuntimeError(f"{trajin} was not found, make sure you ran the previous step: \n"\
#                                 f"mm_ground_state ->  qm_ground_state ->  absorption -> excited_state -> fluorescence\n"\
#                                 f"                                    -> pulse_pump \n")
