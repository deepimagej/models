from ruamel import yaml
from ruamel.yaml import YAML
import urllib.request
import math

# Dominik's magic:
def enforce_min_shape(min_shape, step, axes):
    """Hack: pick a bigger shape than min shape
    Some models come with super tiny minimal shapes, that make the processing
    too slow. While dryrun is not implemented, we'll "guess" a sensible shape
    and hope it will fit into memory.
    """
    MIN_SIZE_2D = 256
    MIN_SIZE_3D = 64

    assert len(min_shape) == len(step) == len(axes)

    spacial_increments = sum(i != 0 for i, a in zip(step, axes) if a in "xyz")
    if spacial_increments > 2:
        target_size = MIN_SIZE_3D
    else:
        target_size = MIN_SIZE_2D

    factors = [math.ceil((target_size - s) / i) for s, i, a in zip(min_shape, step, axes) if a in "xyz"]
    if sum(f > 0 for f in factors) == 0:
        return min_shape

    m = max(factors)
    return [s + i * m for s, i in zip(min_shape, step)]

def parse_prediction(prediction_dict):
    if prediction_dict[0]['spec'].__contains__('MacroFile'):
        processing_txt = [prediction_dict[0]['kwargs']]
    else:
        processing_txt = prediction_dict[0]['spec'].split(' ')
        processing_txt = [processing_txt[0]]
    if len(prediction_dict) > 1:
        for i in range(1, len(prediction_dict)):
            if prediction_dict[i]['spec'].__contains__('MacroFile'):
                aux_txt = prediction_dict[i]['kwargs']
            else:
                aux_txt = prediction_dict[i]['spec'].split(' ')
                aux_txt = aux_txt[0]

            processing_txt.append(aux_txt)
    processing_txt = ' '.join(processing_txt)
    return processing_txt

def create_dij_macro(yaml_url):
    urllib.request.urlretrieve(yaml_url, "model.yaml")
    try:
        yaml = YAML()
        with open('model.yaml') as f:
            YAML_dict = yaml.load(f)
    except:
        print("model.yaml not found.")
        exit(0)

    model_name = YAML_dict['name']
    # Add brackets when there are blanck spaces in the name
    if model_name.__contains__(' '):
        macro_model_name = '[' + model_name + ']'
    else:
        macro_model_name = model_name
        
    # Detect python package of the model
    if 'tensorflow_saved_model_bundle' in YAML_dict['weights']:
        py_format = "Tensorflow"
    elif 'pytorch_script' in YAML_dict['weights']:
        py_format = "Pytorch"
    else:
        print("This models does not have any deepImageJ compatible weight format.")
        exit(0)

    # if YAML_dict['framework'] == 'tensorflow' or YAML_dict['framework'] == 'Tensorflow':
    #     py_format = 'Tensorflow'
    # elif YAML_dict['framework'] == 'tensorflow' or YAML_dict['framework'] == 'Tensorflow' ::
    #     py_format = 'Pytorch'
    # else:
    #     print("The format of the model is not compatible with deepImageJ (format: {})".format(py_format))
    #     exit(0)
    
    preprocessing = YAML_dict['config']['deepimagej']['prediction']['preprocess']
    if preprocessing[0]['spec'] is None:
        # No preprocessing
        preprocessing_txt = "no preprocessing"
    else:
        preprocessing_txt = parse_prediction(preprocessing)

    postprocessing = YAML_dict['config']['deepimagej']['prediction']['postprocess']
    if postprocessing[0]['spec'] is None:
        # No postprocessing
        postprocessing_txt = "no postprocessing"
    else:
        postprocessing_txt = parse_prediction(postprocessing)

    axes = YAML_dict['inputs'][0]['axes']
    if axes.__contains__('b'):
        axes = axes[1:]
    input_shape = YAML_dict['inputs'][0]['shape']

    if 'min' in input_shape:
        m = input_shape['min']
        step = input_shape['step']
        if YAML_dict['inputs'][0]['axes'].__contains__('b'):
            # avoid the batch dimension
            m = m[1:]
            step = step[1:]
        shape = enforce_min_shape(m, step, axes)  # ensure that the tile shape won't be too large
    else:
        if YAML_dict['inputs'][0]['axes'].__contains__('b'):
            input_shape = input_shape[1:]
        shape = input_shape

    # convert into string:
    axes = ','.join(axes)
    shape = ','.join([str(i) for i in shape])
    
    ijmacro = f"""
    rename("image");
    run("DeepImageJ Run", "model={macro_model_name} format={py_format} preprocessing=[{preprocessing_txt}] postprocessing=[{postprocessing_txt}] axes={axes} tile={shape} logging=normal");
    selectWindow("{model_name}" + "_output_image");
    """
    return ijmacro
## Test it with:
#yaml_url = "https://sandbox.zenodo.org/record/885236/files/model.yaml"
#print(create_dij_macro(yaml_url))
