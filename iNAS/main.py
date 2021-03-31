
from settings import Settings, arg_parser, load_settings
from NASBase.top import nas_top
import argparse
import json

if __name__ == "__main__":

	Testset = Settings() # default settings
	Testset = arg_parser(Testset)
	nas_top(Testset)
	