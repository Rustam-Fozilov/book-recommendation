def transform_data(nested_dict):
    index_key = list(nested_dict["isbn"].keys())[0]

    flat_dict = {
        key.replace("-", "_"): value[index_key]
        for key, value in nested_dict.items()
    }

    return flat_dict
