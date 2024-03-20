from py2exe import freeze

freeze(
    console=['AFolder.py', 'BExpts.py', 'CData.py', 'DKeywords.py', 'FFiles.py', 'Gimages.py'],
    windows=[],
    data_files=[],
    zipfile='library.zip',
    options={},
    version_info={}
)