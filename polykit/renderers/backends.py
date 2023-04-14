import IPython

import numpy as np
import fresnel as fl


def fresnel(positions,
            bonds,
            colors,
            cmap='viridis',
            pathtrace=True,
            show_compartments=False,
            light_samples=22,
            roughness=0.3,
            metal=0.4,
            specular=0.8,
            spec_trans=0.,
            outline=0.05,
            h=600,
            w=600):
    """
    Render individual simulation snapshots within IPython notebooks using the Fresnel backend
    """
    
    scene = fl.Scene()
    geometry = fl.geometry.Cylinder(scene, N=bonds.shape[0], outline_width=outline)

    geometry.points[:] = positions[bonds]
    geometry.radius[:] = np.ones(bonds.shape[0])*0.5
    
    geometry.color[:] = colors[bonds]
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

    scene.camera = fl.camera.fit(scene, view='isometric', margin=0)
    
    if pathtrace:
        canvas = fl.pathtrace(scene, light_samples=light_samples, w=w, h=h)
    else:
        canvas = fl.preview(scene, h=h, w=w)
        
    return IPython.display.Image(canvas._repr_png_())
