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

def create_dij_macro(url):
    urllib.request.urlretrieve(yaml_url, "model.yaml")
    try:
        yaml = YAML()
        with open('model.yaml') as f:
            YAML_dict = yaml.load(f)
    except:
        print("model.yaml not found.")
        exit(0)

    model_name = YAML_dict['name']

    preprocessing = YAML_dict['config']['deepimagej']['prediction']['preprocess']
    preprocessing_txt = parse_prediction(preprocessing)

    postprocessing = YAML_dict['config']['deepimagej']['prediction']['postprocess']
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
        # shape = [] # variable to store the shape of the tile
        # test_image = np.load( YAML_dict['test_inputs'][0])
        # dims = [test_image.shape[d] for d in range(len(test_image.shape))]
        # for i in range(len(dims)):
        # if YAML_dict['inputs'][0]['axes'].__contains__('b'):
        #     # avoid the batch dimension
        #     j = i+1
        # else:
        #     j = 1
        # if step[j] > 0:
        #     #if the step is 0, then the shape is like min
        #     n = np.floor((d[i]-m[j])/step[j]) # multiple for the shape calculator
        #     shape.append(int(m[j] + n*step[j]))
        # else:
        #     shape.append(int(m[j]))

    else:
        if YAML_dict['inputs'][0]['axes'].__contains__('b'):
            input_shape = input_shape[1:]
        shape = input_shape

    # convert into string:
    axes = ','.join(axes)
    shape = ','.join([str(i) for i in shape])
    if 'tensorflow_saved_model_bundle' in YAML_dict['weights']:
        format = "Tensorflow"
    elif 'pytorch_script' in YAML_dict['weights']:
        format = "Pytorch"
    else:
        print("This models does not have any deepImageJ compatible weight format.")
        exit(0)

    ijmacro = f"""
    run("DeepImageJ Run",
        "model=[{model_name}] format={format} preprocessing=[{preprocessing_txt}] postprocessing=[{postprocessing_txt}] axes={axes} tile={shape} logging=normal");
    """
    return ijmacro
## Test it with:
#yaml_url = "https://sandbox.zenodo.org/record/885236/files/model.yaml"
#print(create_dij_macro(yaml_url))
