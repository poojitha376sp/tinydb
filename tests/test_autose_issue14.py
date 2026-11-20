from tinydb import Query

def test_ac_fr001_a():
    q = Query().age.between(18, 30)
    assert q({'age': 18}) is True

def test_ac_fr001_b():
    q = Query().age.between(18, 30)
    assert q({'age': 30}) is True

def test_ac_fr001_c():
    q = Query().age.between(18, 30)
    assert q({'age': 25}) is True

def test_ac_nfr001_a():
    q = Query().age.between(18, 30)
    assert q({}) is False

def test_ac_nfr001_b():
    q = Query().age.between(18, 30)
    assert q({'age': 'not-a-number'}) is False
