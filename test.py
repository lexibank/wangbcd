def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 5583
    assert any(f["Form"] == "全部" for f in cldf_dataset["FormTable"])


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset["ParameterTable"])) == 200


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset["LanguageTable"])) == 24
