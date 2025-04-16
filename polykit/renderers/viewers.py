import numpy as np
import matplotlib.pyplot as plt

from matplotlib.cm import ScalarMappable
from matplotlib.ticker import AutoLocator
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import ListedColormap, Normalize, NoNorm

from scipy.ndimage import gaussian_filter


def chromosome_viewer(chrom_lengths,
                      colors=None,
                      height=0.5,
                      width=10.):
    """
    Simple matplotlib-based visualization of individual chromosomes
    
    Parameters
    ----------
        chrom_lengths : Cx1 int array
            List of the sizes of each chromosome
        colors : Nx4 float array or None
            Colors to be assigned to each monomer.
            If omitted, random colors will be attributed to each chromosome
        height : float
            Per-chromosome height of the output figure (in inches)
        width : float
            Total width of the output figure (in inches)
    """
    
    num_chrom = chrom_lengths.shape[0]
    chrom_bounds = np.insert(np.cumsum(chrom_lengths), 0, 0)
    
    fig = plt.figure(figsize=(width, height*num_chrom))
    
    heights = np.linspace(1, 0, num=num_chrom)
    lengths = chrom_lengths.astype(np.float32)/chrom_lengths.max()
    
    if not isinstance(colors, np.ndarray):
        colors = np.ones((num_chrom, 4))
        colors[:, :3] = np.random.random((num_chrom, 3))
        
        colors = np.repeat(colors, chrom_lengths, axis=0)

    for i in range(num_chrom):
        map_name = "chromosome %d" % (i+1)
        ax = fig.add_axes([(1-lengths[i])/2., heights[i], lengths[i], height/num_chrom])
        
        ax.set_title(map_name)
    
        chrom_colors = colors[chrom_bounds[i]:chrom_bounds[i+1], :]
        chrom_map = ListedColormap(chrom_colors, name=map_name)
        
        try:
            plt.register_cmap(name=map_name, cmap=chrom_map)
            
        except ValueError:
            pass
        
        plt.set_cmap(chrom_map)
        
        cb = ColorbarBase(ax, orientation='horizontal', norm=NoNorm())
    
        cb.locator = AutoLocator()
        cb.update_ticks()
        
    plt.show()


def rasterize(positions,
              box_size,
              resolution=100,
              length_unit=50,
              gaussian_width=250,
              normalize=False):
    """
    3D positions rasterizer for numerical microscopy analysis
    
    Parameters
    ----------
        positions : Nx3 float array
            List of X,Y,Z particle positions to be rasterized (in model units).
            Assumes particle coordinates are wrapped in PBCs within the range [-box_size/2,+box_size/2]
        box_size : float
            Linear dimension of periodic box (in model units)
        resolution : float
            Linear dimension of output voxels (in nm)
        length_unit : float
            Model unit of length (in nm)
        gaussian_width : float
            Width of Gaussian point-spread function to be used (in nm).
            If gaussian_width<=0, returns the raw (undiffracted) raster
		normalize : bool
            Set to True to scale maximum voxel intensity to 1
            
    Returns
    -------
        MxMxM raster array of 3D voxels
    """
    
    n_voxels = int(box_size / (resolution/length_unit))
    bins = np.linspace(-box_size/2., box_size/2., num=n_voxels+1)
																			
    digitized_x = np.digitize(positions[:,0], bins) - 1
    digitized_y = np.digitize(positions[:,1], bins) - 1
    digitized_z = np.digitize(positions[:,2], bins) - 1
					
    digitized = digitized_x + digitized_y*n_voxels + digitized_z*n_voxels**2
    bincounts = np.bincount(digitized, minlength=n_voxels**3)
					
    raster = bincounts.reshape((n_voxels,n_voxels,n_voxels))
	
    if gaussian_width > 0:
        raster = gaussian_filter(raster/raster.max(), sigma=gaussian_width/resolution, mode='wrap')
        
    if normalize:
        raster /= raster.max()
        
    return raster


def voxels_to_pixels_RGB(raster,
                         cmap,
                         vmin=None,
                         vmax=None,
                         mode='max',
                         axis=2):
    """
    Project voxels onto 2D pixels and map values to RGB
    
    Parameters
    ----------
        raster : MxMxM float array
            3D voxel array to visualize
        cmap : matplotlib colormap object or str
            Colormap to be used
        vmin, vmax : float or None
            RGB dynamic range.
            If set to None, use full data range
        mode : str
            Projection mode to be used.
            Set to either 'max' for maximum intensity or 'sum' for summed intensity projection
        axis : int
            Index of projection axis
            
    Returns
    -------
        MxMx3 image array of RGB pixels
    """

    if mode == 'max':
        raster_2D = raster.max(axis=axis)
    elif mode == 'sum':
        raster_2D = raster.sum(axis=axis)
    else:
        raise RuntimeError(f"Unsupported projection mode {mode}")
		
    vmin = raster_2D.min() if vmin is None else vmin
    vmax = raster_2D.max() if vmax is None else vmax

    norm = Normalize(vmin=vmin, vmax=vmax)
    cm = ScalarMappable(norm=norm, cmap=cmap)

    im = cm.to_rgba(raster_2D)
	
    return im[..., :3]
