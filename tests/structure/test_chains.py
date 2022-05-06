# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

import biotite.structure as struc
import biotite.structure.io as strucio
import numpy as np
from os.path import join
from ..util import data_dir
import pytest


@pytest.fixture
def array():
    return strucio.load_structure(join(data_dir("structure"), "1igy.mmtf"))

def test_get_chain_starts(array):
    """
    Compare :func:`test_get_chain_starts()` with :func:`np.unique` in a
    case where chain ID unambiguously identify chains.
    """
    _, ref_starts = np.unique(array.chain_id, return_index=True)
    test_starts = struc.get_chain_starts(array)
    # All first occurences of a chain id are automatically chain starts
    assert set(ref_starts).issubset(set(test_starts))

def test_get_chain_starts_same_id(array):
    """
    Expect correct number of chains in a case where two successive
    chains have the same chain ID (as possible in an assembly).
    """
    # Concatenate two chains with same ID
    array = array[array.chain_id == "A"]
    merged = array + array
    assert struc.get_chain_starts(merged).tolist() == [0, array.array_length()]

def test_get_chains(array):
    assert struc.get_chains(array).tolist() == ["A", "B", "C", "D", "E", "F"]

def test_get_chain_count(array):
    assert struc.get_chain_count(array) == 6

def test_chain_iter(array):
    n = 0
    for chain in struc.get_chains(array):
        n += 1
        assert isinstance(array, struc.AtomArray)
    assert n == 6