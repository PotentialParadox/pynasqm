import re
import tempfile
import shutil


def sed_inplace(filename, pattern, replacement):
    # Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    # `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    pattern_compiled = re.compile(pattern)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(replacement, line))
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


def sed_global(filename, pattern, replacement):
    #  Like sed, but places the entire file into the buffer
    pattern_compiled = re.compile(pattern)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            tmp_file.write(pattern_compiled.sub(replacement, src_file.read()))
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)
