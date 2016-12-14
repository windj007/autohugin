import exifread, re, dateutil.parser, datetime, os, logging

from .config import BatchPanoConfig


logger = logging.getLogger(__name__)


_MEANINGFUL_EXIF_RE = re.compile('^(Image|EXIF|MakerNote) ')
def _get_meaningful_exif(fname):
    with open(fname, 'rb') as f:
        return { k : v
                for k, v in exifread.process_file(f).viewitems()
                if _MEANINGFUL_EXIF_RE.search(k) }


class Rule(object):
    def __init__(self, key):
        self.key = key

    def __call__(self, first_exif, second_exif):
        logger.debug('apply %s to %s' % (self.__class__, self.key))
        return self._exec(first_exif[self.key], second_exif[self.key])


class Eq(Rule):
    def _exec(self, first_tag, second_tag):
        return str(first_tag) == str(first_tag)


class DiffSmaller(Rule):
    def __init__(self, key, max_diff, parser = str):
        super(DiffSmaller, self).__init__(key)
        self.max_diff = max_diff
        self.parser = parser

    def _exec(self, first_tag, second_tag):
        return (self.parser(second_tag) - self.parser(first_tag)) <= self.max_diff


_EXIF_EQ_RULES = map(Eq,
                     ['EXIF ExposureMode',
                      'EXIF FocalLength',
                      'Image Orientation',
                      'MakerNote LensModel'])


class ImagesGrouper(object):
    def __init__(self, max_timestamp_diff_seconds = 5):
        self.timestamp_diff_rule = DiffSmaller('Image DateTimeOriginal',
                                               datetime.timedelta(seconds = max_timestamp_diff_seconds),
                                               lambda t: dateutil.parser.parse(str(t)))
    
    def __call__(self, filenames):
        if len(filenames) == 0:
            return

        filenames = sorted(filenames)
        cur_chunk = [filenames[0]]
        prev_exif = _get_meaningful_exif(filenames[0])
        for fname in filenames[1:]:
            logger.info('considering %s' % fname)
            cur_exif = _get_meaningful_exif(fname)
            if not self._exifs_compatible(prev_exif, cur_exif):
                if len(cur_chunk) > 1:
                    logger.info('yield chunk of %d images' % len(cur_chunk))
                    yield cur_chunk
                else:
                    logger.info('skipping 1 image')
                cur_chunk = []
            cur_chunk.append(fname)
            prev_exif = cur_exif

        if len(cur_chunk) > 1:
            logger.info('yield chunk of %d images' % len(cur_chunk))
            yield cur_chunk

    def _exifs_compatible(self, prev_exif, cur_exif):
        if any(not eq(prev_exif, cur_exif) for eq in _EXIF_EQ_RULES):
            return False
        if not self.timestamp_diff_rule(prev_exif, cur_exif):
            return False
        return True


def get_default_project_filepath(filepaths):
    only_names = sorted(os.path.splitext(os.path.basename(fname))[0] for fname in filepaths)
    dirname = os.path.dirname(filepaths[0])
    return os.path.join(dirname, '%s-%s.pto' % (only_names[0], only_names[-1]))


_IMAGE_EXTENSION_RE = re.compile('(jpg|png)$', re.I)

def group_images_and_make_config(in_dir, out_file, config_kwargs = {}, grouper_kwargs = {}):
    config = BatchPanoConfig(**config_kwargs)

    src_files = [os.path.join(in_dir, fname)
                 for fname in os.listdir(in_dir)
                 if _IMAGE_EXTENSION_RE.search(fname)]
    logging.debug('Found %d images' % len(src_files))
    for group in ImagesGrouper(**grouper_kwargs)(src_files):
        config.add_pano(source_files = group,
                        project_filename = get_default_project_filepath(group))

    config.save(out_file)
    return config
