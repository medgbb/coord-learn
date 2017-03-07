from ccdc import io
import pandas as pd
import time
import numpy as np

np.random.seed(901)
csd_reader = io.EntryReader('CSD')

def mol_reader(n):
    """Calls the nth entry in the CSD as a molecule object."""
    entry = csd_reader[n]
    return csd_reader.molecule(entry.identifier)

class Mol():
    """
    A wrapper class for csd molecule objects. 
    """
    def __init__(self, index):
        self._molecule = self.get_mol(index)
    
    def __getattr__(self, attr):
        """Wraps this class object around a CSD molecule object."""
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._molecule, attr)
    
    def get_mol(self, index):
        """Acquires a molecule object from the CSD, using either the string 
        label for the structure, or its numerical index."""
        try: 
            return csd_reader.molecule(index)
        except NotImplementedError:
            return mol_reader(index)
    
    def remove_unlocated(self):
        """Removes all atoms in a molecule that are missing coordinates."""
        for atom in self.atoms:
            if atom.coordinates is None:
                self.remove_atom(atom)
    
    def center(self):
        """Centers the molecule, eliminating unlocated atoms."""
        try:
            self.remove_unlocated()
            self.translate([round(-1 * a, 4)
                            for a in self.centre_of_geometry()])
        except ValueError:
            pass
    
    def xyz(self):
        """Returns a dataframe of the molecule's atomic coordinates in
        a format similar to .xyz files.
        """
        atoms = self.atoms
        size = len(atoms)
        coords = [[atom.atomic_symbol] + 
                    self.coord_format(atom.coordinates)
                        for atom in atoms]
            #use atom.label to get the symbol and index number together
        return pd.DataFrame(coords, columns=['Element', 'x', 'y', 'z'])
    
    def coord_format(self, coord):
        """Rounds coordinates or deals with missing data."""
        try:
            return [round(a, 4) for a in coord]
        except TypeError:
            return [None, None, None]
    
    def center_elements(self, elem):
        """Takes an element type and returns a list of dataframes, representing
        the same molecule centered on each instance of that element.
        The molecule is represented entirely in terms of radii from the central
        atom, and the atoms are ordered by these distances, smallest to largest.
        """
        

A = Mol('AABHTZ')
print(A)
print(A.xyz())

B = Mol(1)
print(B)
print(B.xyz())
print(A.all_atoms_have_sites)
print(B.all_atoms_have_sites)
B.center()
print(B.xyz())
print(B.all_atoms_have_sites)


                
class Molset():
    """
    __init__:
    Takes either a list of structure identifier symbols, or an integer value n 
    representing the first n entries in the CSD, and generates a dictionary
    containing a subset of the molecule objects in the CSD. 
    
    """
    def __init__(self, ids=[]):
        self.mols = self.populate_mols(ids)
        #self.center_all()
        #self.xyzset = self.populate_xyz()
        self.xyzset = self.centered_xyz()
    
    def populate_mols(self, ids):
        """Populates self.mols using a list of string identifiers, or a list of
        numerical indices. If instead a number n is given directly, n fully-3D
        entries are chosen from the CSD to populate self.mols."""
        try:
            mols = {}
            for id in ids:
                amol = Mol(id)
                mols[amol.identifier] = amol
        except TypeError:
            mols = self.random_populate(ids)
        return mols
    
    def random_populate(self, count):
        mols = {}
        while len(mols) < count:
            id = np.random.randint(0, len(csd_reader))
            amol = Mol(id)
            if amol.all_atoms_have_sites:
                mols[amol.identifier] = amol
        return mols
    
    def center_all(self):
        """Use to re-center all Mols."""
        for id in self.mols:
            self.mols[id].center()
    
    def populate_xyz(self):
        return {id: self.mols[id].xyz() for id in self.mols}
    
    def centered_xyz(self):
        molxyz = {}
        for id in self.mols:
            self.mols[id].center()
            molxyz[id] = self.mols[id].xyz()
        return molxyz
    
        
# examples = [csd_reader[i].identifier for i in range(11)]
# print(examples)
                        
# trainset = Molset(['AABHTZ', 'ABEBUF'])
# print(trainset.mols)
# print(trainset.xyzset)
# trainset2 = Molset([10])
# print(trainset2.xyzset)
# trainset3 = Molset(10)
# print(trainset3.xyzset)
# print(len(trainset3.xyzset))


# #Timing Tests
# start = time.time()
# trainset10 = Molset(10)
# end = time.time()
# time10 = end - start

# start = time.time()
# trainset100 = Molset(100)
# end = time.time()
# time100 = end - start

# start = time.time()
# trainset1000 = Molset(1000)
# end = time.time()
# time1000 = end - start

# print(time10)
# print(time100)
# print(time1000)
