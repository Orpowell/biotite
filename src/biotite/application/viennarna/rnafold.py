# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__name__ = "biotite.application.viennarna"
__author__ = "Tom David Müller"
__all__ = ["RNAfoldApp"]

import warnings
from .basefold import BaseFoldApp
from ..application import AppState, requires_state
from ...sequence.io.fasta import FastaFile, set_sequence
from ...sequence import NucleotideSequence
from ...structure.dotbracket import base_pairs_from_dot_bracket


class RNAfoldApp(BaseFoldApp):
    """
    Compute the minimum free energy secondary structure of a ribonucleic
    acid sequence using *ViennaRNA's* *RNAfold* software.

    Internally this creates a :class:`Popen` instance, which handles
    the execution.

    Parameters
    ----------
    sequence : NucleotideSequence
        The RNA sequence.
    temperature : int, optional
        The temperature (°C) to be assumed for the energy parameters.
    bin_path : str, optional
        Path of the *RNAfold* binary.

    Examples
    --------

    >>> sequence = NucleotideSequence("CGACGTAGATGCTAGCTGACTCGATGC")
    >>> app = RNAfoldApp(sequence)
    >>> app.start()
    >>> app.join()
    >>> print(app.get_mfe())
    -1.3
    >>> print(app.get_dot_bracket())
    (((.((((.......)).)))))....
    """

    def __init__(self, sequence, temperature=37, bin_path="RNAfold"):
        fasta_file = FastaFile()
        set_sequence(fasta_file, sequence)
        super().__init__(fasta_file, temperature, bin_path)
        self._temperature = str(temperature)
    
    @staticmethod
    def accepts_stdin():
        return True

    def run(self):
        self.set_arguments(["--noPS"])
        super().run()

    def evaluate(self):
        super().evaluate()
        lines = self.get_stdout().splitlines()
        content = lines[2]
        dotbracket, free_energy = content.split(" ", maxsplit=1)
        free_energy = float(free_energy[1:-1])

        self._free_energy = free_energy
        self._dotbracket = dotbracket
    
    @requires_state(AppState.JOINED)
    def get_free_energy(self):
        """
        Get the free energy (kcal/mol) of the suggested
        secondary structure.

        Returns
        -------
        free_energy : float
            The free energy.

        Examples
        --------

        >>> sequence = NucleotideSequence("CGACGTAGATGCTAGCTGACTCGATGC")
        >>> app = RNAfoldApp(sequence)
        >>> app.start()
        >>> app.join()
        >>> print(app.get_free_energy())
        -1.3
        """
        return self._free_energy

    @requires_state(AppState.JOINED)
    def get_mfe(self):
        """
        Get the free energy (kcal/mol) of the suggested
        secondary structure.

        DEPRECATED: Use :meth:`get_free_energy()` instead.

        Returns
        -------
        mfe : float
            The minimum free energy.

        Examples
        --------

        >>> sequence = NucleotideSequence("CGACGTAGATGCTAGCTGACTCGATGC")
        >>> app = RNAfoldApp(sequence)
        >>> app.start()
        >>> app.join()
        >>> print(app.get_mfe())
        -1.3
        """
        warnings.warn(
            "'get_mfe()' is deprecated, use 'get_free_energy()' instead",
            DeprecationWarning
        )
        return self._mfe

    @requires_state(AppState.JOINED)
    def get_dot_bracket(self):
        """
        Get the minimum free energy secondary structure of the input
        sequence in dot bracket notation.

        Returns
        -------
        dotbracket : str
            The secondary structure in dot bracket notation.

        Examples
        --------

        >>> sequence = NucleotideSequence("CGACGTAGATGCTAGCTGACTCGATGC")
        >>> app = RNAfoldApp(sequence)
        >>> app.start()
        >>> app.join()
        >>> print(app.get_dot_bracket())
        (((.((((.......)).)))))....
        """
        return self._dotbracket

    @requires_state(AppState.JOINED)
    def get_base_pairs(self):
        """
        Get the base pairs from the minimum free energy secondary
        structure of the input sequence.

        Returns
        -------
        base_pairs : ndarray, shape=(n,2)
            Each row corresponds to the positions of the bases in the
            sequence.

        Examples
        --------

        >>> sequence = NucleotideSequence("CGACGTAGATGCTAGCTGACTCGATGC")
        >>> app = RNAfoldApp(sequence)
        >>> app.start()
        >>> app.join()
        >>> print(app.get_base_pairs())
            [[ 0 22]
             [ 1 21]
             [ 2 20]
             [ 4 19]
             [ 5 18]
             [ 6 16]
             [ 7 15]]

        For reference, the corresponding dot bracket notation can be
        displayed as below.

        >>> print(app.get_dot_bracket())
        (((.((((.......)).)))))....
        """
        return base_pairs_from_dot_bracket(self._dotbracket)

    @staticmethod
    def compute_secondary_structure(sequence, bin_path="RNAfold"):
        """
        Compute the minimum free energy secondary structure of a 
        ribonucleic acid sequence using *ViennaRNA's* *RNAfold* software.

        This is a convenience function, that wraps the
        :class:`RNAfoldApp` execution.

        Parameters
        ----------
        sequence : NucleotideSequence
            The RNA sequence.
        bin_path : str, optional
            Path of the *RNAfold* binary.

        Returns
        -------
        dotbracket : str
            The secondary structure in dot bracket notation.
        free_energy : float
            The free energy.
        """
        app = RNAfoldApp(sequence, bin_path=bin_path)
        app.start()
        app.join()
        return app.get_dot_bracket(), app.get_free_energy()
