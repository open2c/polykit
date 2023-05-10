import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import AutoLocator
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import ListedColormap, NoNorm


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
