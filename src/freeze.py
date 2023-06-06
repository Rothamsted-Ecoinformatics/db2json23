from py2exe import freeze

freeze(
    console=['CData.py', 'DKeywords.py', 'BExpts.py', 'FFiles.py', 'Gimages.py'],
    windows=[],
    data_files=['settings.py'],
    zipfile='library.zip',
    options={},
    version_info={}
)