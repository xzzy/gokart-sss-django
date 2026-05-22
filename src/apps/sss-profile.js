let gokartProfile=  {
    "name": "sss",
    "version":"16.11.1",
    "distributionType":"release",
    "description":"Spatial Support System v3 (Django)",
    "repositoryBranch":"working",
    "lastCommit":"466dac1",
    "commitDate":"Thu May 14 10:08:37 2026 +0800",
    "commitMessage":"Fix prepareDatasource not recovering from notexist state for .grb and .nc files\\nWhen a datasource file is missing at server startup, prepareDatasource sets\\ndatasource[\"datasource\"] = None and loadstatus[\"status\"] = \"notexist\".\\nAfter the file becomes available (e.g. after an FTP sync delivers the file),\\nsubsequent calls to prepareDatasource failed to recover due to two bugs:\\n1. The check `if \"datasource\" not in datasource` only tests for key existence,\\nnot the value. Since the key was already present (with value None), the\\nblock that sets the datasource path was skipped, leaving the path as None\\nindefinitely. Fixed by changing to `if not datasource.get(\"datasource\")`\\nso that a None value is correctly treated as \"not yet set\".\\n2. \"notexist\" was included in the exclusion list of the final status-reset\\nguard at the end of the function:\\n`if datasource[\"loadstatus\"][\"status\"] not in (\"loaded\",\"notexist\",\"notsupport\")`\\nThis prevented the status from being reset to \"inited\" when the file\\nbecame available, so syncDatasource would never attempt to reload it.\\nFixed by removing \"notexist\" from the exclusion list. \"notsupport\" is\\nintentionally kept excluded because an unsupported file format will never\\nfix itself and should not be retried. Note that all code paths that set\\nthe status to \"notexist\" end with an explicit return, so there is no risk\\nof this change incorrectly resetting a currently-missing file.\\nThese two bugs combined meant that any datasource whose file was absent at\\nstartup would remain permanently unavailable even after the file was later\\ndelivered, causing it to be excluded from the outlookmetadata API response\\nand not appear in the Available Columns list on the weather outlook UI.",
    "commitAuthor":"Katsufumi Shibata <katsufumi.shibata@dbca.wa.gov.au>",
    "build":{
        "datetime":"2026-05-22 08:26:56 AWST(+0800)",
        "date":"2026-05-22 AWST(+0800)",
        "time":"08-26-56 AWST(+0800)",
        "platform":"Linux",
        "host":"gokart-sss-django-userdev-5d8cb9c4df-kd98m",
        "vendorMD5":"pblY_g4-s1TttbI8u0a9vA"
    }
}
export default gokartProfile
