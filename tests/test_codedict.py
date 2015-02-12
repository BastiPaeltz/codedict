
from codedict.processor import split_arguments


def test_split_arguments():
	assert split_arguments({'-i': 'True', 'use_case' : 'power'}) == ({'use_case' : 'power'}, {'-i' : 'True'}) 