import PIL
import IPython

import numpy as np
import fresnel as fl

try:
    import fresnel.interact as interact
    
except ImportError:
    pass


class Fresnel():
    """
    Fresnel API for interactive/notebook-embedded visualization.
        
    See the _fresnel backend method for a full list of arguments and parameters
    """
        
    def __init__(self, *args, **kwargs):
        self.scene = self._fresnel(*args, **kwargs)
            
            
    def interactive(self, standalone=True):
        """
        Conjure up interactive rendering window
        
        Parameters
        ----------
        standalone : bool
            Set to True if called within standalone script
        """
        
        view = interact.SceneView(self.scene)

        if standalone:
            view.show()
            interact.app.exec_()
            
        else:
            return view
            
            
    def static(self,
               pathtrace=True,
               png_output_file=None,
               light_samples=22,
               height=600,
               width=600):
        """
        Render static image for notebook-embedded visualization or saving to disk
        
        Parameters
        ----------
        pathtrace : bool
            Set to False to enable quick rendering with approximate lighting effects, or True for full path tracing.
        png_output_file : string
            Path of PNG output image to be created
        light_samples : int
            Number of light samples per primary camera ray (only relevant if pathtrace == True).
            Higher numbers reduce sampling noise, but result in slower rendering speeds
        height : int
            Height of the output image (in pixels)
        width : int
            Width of the output image (in pixels)
        """
            
        if pathtrace:
            canvas = fl.pathtrace(self.scene, light_samples=light_samples, h=height, w=width)
            
        else:
            canvas = fl.preview(self.scene, h=height, w=width)
        
        if png_output_file:
            image = PIL.Image.fromarray(canvas, mode='RGBA')
            image.save(png_output_file)
            
        else:
            return IPython.display.Image(canvas._repr_png_())
            

    def _fresnel(self,
                 positions,
                 bonds,
                 colors,
                 radii,
                 roughness=0.3,
                 metal=0.4,
                 specular=0.8,
                 spec_trans=0.,
                 outline=0.05):
        """
        Render individual polymer conformations within IPython notebooks using the Fresnel backend
            
        Parameters
        ----------
        positions : Nx3 float array
            List of 3D positions of the monomers to be displayed
        bonds : Mx2 int array
            List of pairwise inter-monomer bonds to be displayed
        colors : Nx3 float array
            List of RGB colors to be assigned to each monomer
        radii : Mx1 float array
            List of bond/particle radii
        roughness : float
            Roughness of the rendering material. Nominally in the range [0.1,1]
        metal : float
            Set to 0 for dielectric materials, or 1 for metals. Intermediate values interpolate between the 2
        specular : float
            Controls the strength of specular highlights. Nominally in the range [0.1,1]
        spec_trans : float
            Controls the amount of specular light transmission. In the range [0,1]
        outline : float
            Width of the outline material
        
        Returns
        -------
            IPython image object suitable for embedding in Jupyter notebooks
        """
            
        scene = fl.Scene()
            
        geometry = fl.geometry.Cylinder(scene, N=bonds.shape[0], outline_width=outline)
        
        geometry.color[:] = colors[bonds]
        geometry.points[:] = positions[bonds]
        geometry.radius[:] = radii[bonds].min(axis=1)
            
        geometry.material = fl.material.Material(color=fl.color.linear([0.25,0.25,0.25]),
                                                 roughness=roughness,
                                                 metal=metal,
                                                 specular=specular,
                                                 spec_trans=spec_trans,
                                                 primitive_color_mix=1.)
                                                     
        geometry.outline_material = fl.material.Material(color=fl.color.linear([0.25,0.25,0.25]),
                                                         roughness=2*roughness,
                                                         metal=metal,
                                                         specular=specular,
                                                         spec_trans=spec_trans,
                                                         primitive_color_mix=0., solid=0.)
            
        polymer_mask = np.ones(positions.shape[0], dtype=bool)
        polymer_mask[bonds] = False
            
        num_unbound_atoms = np.count_nonzero(polymer_mask)
            
        if num_unbound_atoms > 0:
            geometry2 = fl.geometry.Sphere(scene, N=num_unbound_atoms, outline_width=outline)
                
            geometry2.color[:] = colors[polymer_mask]
            geometry2.radius[:] = radii[polymer_mask]
            geometry2.position[:] = positions[polymer_mask]
        
            geometry2.material = fl.material.Material(color=fl.color.linear([0.25,0.25,0.25]),
                                                      roughness=roughness,
                                                      metal=metal,
                                                      specular=specular,
                                                      spec_trans=spec_trans,
                                                      primitive_color_mix=1., solid=0.)
        
        scene.camera = fl.camera.Orthographic.fit(scene, view='isometric', margin=0)
            
        return scene
