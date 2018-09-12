# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.misc import slug
from clldutils.path import Path
import lingpy

from clldutils.path import Path
from pylexibank.dataset import Metadata
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.lingpy_util import getEvoBibAsBibtex


class Dataset(BaseDataset):
    dir = Path(__file__).parent

    def cmd_download(self, **kw):
        d = Path(
            'LinguList-Network-perspectives-on-Chinese-dialect-history-933bf29/'
            'Supplementary_Material_I/data/')
        self.raw.download_and_unpack(
            "https://zenodo.org/record/16760/files/"
            "Network-perspectives-on-Chinese-dialect-history-1.zip",
            d.joinpath('chinese.tsv'),
            d.joinpath('old_chinese.csv'),
            log=self.log)
        self.raw.write('sources.bib', getEvoBibAsBibtex('Hamed2006', 'List2015d', **kw))

    def split_forms(self, row, value):
        """
        We make sure to always only yield one form per raw lexeme.
        """
        return Dataset.split_forms(self, row, value)[:1]

    def cmd_install(self, **kw):
        wl = lingpy.Wordlist(self.raw.posix('chinese.tsv'))
        gcode = {x['NAME']: x['GLOTTOCODE'] for x in self.languages}
        ccode = {x.english: x.concepticon_id for x in
                 self.conceptlist.concepts.values()}

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())

            # store list of proto-form to cognate set
            p2c = {}

            for k in wl:
                ds.add_concept(
                    ID=wl[k, 'concept'],
                    gloss=wl[k, 'concept'],
                    conceptset=ccode[wl[k, 'concept']])
                ds.add_language(
                    ID=wl[k, 'doculect'],
                    name=wl[k, 'doculect'],
                    glottocode=gcode[wl[k, 'doculect']])
                for row in ds.add_lexemes(
                    Language_ID=wl[k, 'doculect'],
                    Parameter_ID=wl[k, 'concept'],
                    Value=wl[k, 'ipa'],
                    Source='Hamed2006',
                    Cognacy=wl[k, 'COGID']
                ):
                    ds.add_cognate(
                        lexeme=row,
                        Cognateset_ID='{0}-{1}'.format(
                            slug(wl[k, 'concept']), wl[k, 'cogid']),
                        Cognate_source='Hamed2006')
                p2c[wl[k, 'proto']] = wl[k, 'cogid']
            idx = max([k for k in wl]) + 1
            ds.add_language(
                    ID='OldChinese',
                    name='Old Chinese',
                    glottocode='sini1245')
            for line in lingpy.csv2list(self.raw.posix('old_chinese.csv')):
                ds.add_concept(
                    ID=line[0],
                    gloss=line[0],
                    conceptset=ccode[line[0]])
                for val in line[1].split(', '):
                    for row in ds.add_lexemes(
                        Language_ID='OldChinese',
                        Parameter_ID=line[0],
                        Value=val,
                        Source='Hamed2006',
                        Cognacy=p2c.get(val, val)
                    ):
                        ds.add_cognate(
                            lexeme=row,
                            Cognateset_ID='{0}-{1}'.format(
                                slug(line[0]), p2c.get(val, val)),
                            Cognate_source='Hamed2006')
                    idx += 1
