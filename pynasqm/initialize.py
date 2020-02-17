from pynasqm.pynasqmin import pynasqmin
from pynasqm.initinputceon import initinputceon
from pynasqm.mdqmmmambin import mdqmmmambin

def initialize() -> None:
    open('input.ceon', 'w').write(initinputceon)
    open('pynasqm.in', 'w').write(pynasqmin)
    open('md_qmmm_amb.in', 'w').write(mdqmmmambin)
