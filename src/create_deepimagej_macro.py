from ruamel import yaml
from ruamel.yaml import YAML
import numpy as np
import urllib.request

yaml_url = "https://sandbox.zenodo.org/record/885236/files/model.yaml"
urllib.request.urlretrieve(yaml_url,"model.yaml")
def create_dij_macro(url):
    try:
        yaml = YAML()
    with open('model.yaml') as f:
        YAML_dict = yaml.load(f)
    except:
    print("model.yaml not found.")

    model_name = YAML_dict['name']
    preprocessing = YAML_dict['config']['deepimagej']['prediction']['preprocess']
    preprocessing_txt = preprocessing[0]['kwargs']
    if len(preprocessing)>1:
        for i in range(1,len(preprocessing)):
            preprocessing_txt = preprocessing_txt + ' ' + preprocessing[i]['kwargs']

    postprocessing = YAML_dict['config']['deepimagej']['prediction']['postprocess']
    postprocessing_txt = postprocessing[0]['kwargs']
    if len(postprocessing) > 1:
        for i in range(1, len(postprocessing)):
            postprocessing_txt = postprocessing_txt + ' ' + postprocessing[i]['kwargs']

    axes = YAML_dict['inputs'][0]['axes']
    if axes.__contains__('b'):
        axes = axes[1:]
    axes = ','.join(axes)
    input_shape = YAML_dict['inputs'][0]['shape']


    test_image = np.load( YAML_dict['test_inputs'][0])
    dims = [test_image.shape[d] for d in range(len(test_image.shape))]
    # shape = min + (n)*step
    if 'min' in input_shape:
        shape = [] # variable to store the shape of the tile
        m = input_shape['min']
        step = input_shape['step']
        for i in range(len(d)):
            if YAML_dict['inputs'][0]['axes'].__contains__('b'):
                # avoid the batch dimension
                j = i+1
            else:
                j = 1
            if step[j] > 0:
                #if the step is 0, then the shape is like min
                n = np.floor((d[i]-m[j])/step[j]) # multiple for the shape calculator
                shape.append(int(m[j] + n*step[j]))
            else:
                shape.append(int(m[j]))
        shape = ','.join([str(i) for i in shape])

    ijmacro = f"""
    run("DeepImageJ Run",
        "model=[{model_name}] format=Tensorflow preprocessing=[{preprocessing_txt}] postprocessing=[{postprocessing_txt}] axes={axes} tile={shape} logging=normal");
    """
    return ijmacro



