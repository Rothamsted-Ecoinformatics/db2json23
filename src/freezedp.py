from py2exe import freeze

freeze(
    console=['data_packager.py'],
    windows=[],
    data_files=['settings.py'],
    zipfile='library.zip',
    options={},
    version_info={}
)