from py2exe import freeze

freeze(
    console=['BExpts.py', 'CData.py', 'DKeywords.py', 'FFiles.py', 'Gimages.py','settings.py'],
    windows=[],
    data_files=[],
    zipfile='library.zip',
    options={},
    version_info={}
)