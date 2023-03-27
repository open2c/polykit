# polykit

Generic toolkit for polymer simulation setup and analysis

## Usage

All functions within the `analysis` module should work as described in the [**Polychrom**](https://polychrom.readthedocs.io/en/latest/index.html) documentation, on condition that an appropriate [**`load_function`**](https://polychrom.readthedocs.io/en/latest/polychrom.hdf5_format.html#polychrom.hdf5_format.load_URI) is provided to parse the required trajectory files. For [**HOOMD-blue**](https://glotzerlab.engin.umich.edu/hoomd-blue/)'s native [**GSD**](https://gsd.readthedocs.io/en/stable/index.html) file format, the corresponding function takes the following form:

~~~python
def load_gsd(URI):
    filename, group = URI.split("::")

    with gsd.hoomd.open(name=filename, mode="rb") as traj:
        return traj[int(group)].particles.position
~~~
