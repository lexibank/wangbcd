# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.misc import slug
from clldutils.path import Path
import lingpy

from clldutils.path import Path
from clldutils.misc import slug
from pylexibank.dataset import Metadata
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import getEvoBibAsBibtex


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = 'wangbcd'

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
        return BaseDataset.split_forms(self, row, value)[:1]

    def cmd_install(self, **kw):
        wl = lingpy.Wordlist(self.raw.posix('chinese.tsv'))
        maxcogid = 0

        with self.cldf as ds:
            ds.add_sources()
            ds.add_languages(id_factory=lambda l: l['Name'])
            ds.add_concepts(id_factory=lambda c: slug(c.label, lowercase=False))

            # store list of proto-form to cognate set
            p2c = {}

            for k in wl:
                for row in ds.add_lexemes(
                    Language_ID=wl[k, 'doculect'],
                    Parameter_ID=slug(wl[k, 'concept'], lowercase=False),
                    Value=wl[k, 'ipa'],
                    Source='Hamed2006',
                    Cognacy=wl[k, 'COGID']
                ):
                    ds.add_cognate(
                        lexeme=row,
                        Cognateset_ID=wl[k, 'cogid'],
                        Source=['Hamed2006'])
                maxcogid = max([maxcogid, int(wl[k, 'cogid'])])
                p2c[wl[k, 'proto']] = wl[k, 'cogid']
            idx = max([k for k in wl]) + 1
            for line in lingpy.csv2list(self.raw.posix('old_chinese.csv')):
                for val in line[1].split(', '):
                    cogid = p2c.get(val)
                    if not cogid:
                        maxcogid += 1
                        cogid = p2c[val] = maxcogid
                    for row in ds.add_lexemes(
                        Language_ID='OldChinese',
                        Parameter_ID=slug(line[0], lowercase=False),
                        Value=val,
                        Source='Hamed2006',
                        Cognacy=p2c.get(val, val)
                    ):
                        ds.add_cognate(
                            lexeme=row,
                            Cognateset_ID=cogid,
                            Source=['Hamed2006'])
                    idx += 1
