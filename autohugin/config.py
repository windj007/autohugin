import yaml


class BatchPanoConfig(object):
    def __init__(self, global_out_dir = None, **global_hugin_kwargs):
        self.global_settings = dict(out_dir = global_out_dir)
        self.global_settings.update(global_hugin_kwargs)
        self.panos = []
    
    def add_pano(self, source_files = [], project_filename = None, **hugin_kwargs):
        result = {'source_files' : source_files,
                  'project_filename' : project_filename}
        result.update(hugin_kwargs)
        self.panos.append(result)

    def save(self, out_file):
        with open(out_file, 'w') as f:
            yaml.dump(dict(global_settings = self.global_settings,
                           panos = self.panos),
                      f)

    @classmethod
    def load(cls, in_file):
        with open(in_file, 'r') as f:
            info = yaml.load(f)
            result = BatchPanoConfig()
            result.global_settings = info['global_settings']
            result.panos = info['panos']
            return result
