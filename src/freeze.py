from py2exe import freeze

freeze(
    console=['BExpts.py', 'CData.py', 'DKeywords.py', 'FFiles.py', 'Gimages.py'],
    windows=[],
    data_files=['settings.py'],
    zipfile='library.zip',
    options={},
    version_info={}
)