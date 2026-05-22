let gokartProfile=  {
    "name": "sss",
    "version":"16.11.1",
    "distributionType":"release",
    "description":"Spatial Support System v3 (Django)",
    "repositoryBranch":"working",
    "lastCommit":"7f038bc",
    "commitDate":"Fri May 22 09:30:55 2026 +0800",
    "commitMessage":"Fix JSONDecodeError in spatial_calculation_progress\\ncalculation_object.output stores the Python repr() of a dict, which uses\\nsingle-quoted strings. The previous approach of .replace(\"'\", '\"') broke\\nwhenever a string value contained an apostrophe (e.g. layer names like\\n'cddp:legislated_lands_and_waters'). Its companion .replace(\"nan\", \"null\")\\nalso lacked word-boundary guards, so values containing \"nan\" as a substring\\n(e.g. \"banana\") would be corrupted.\\nReplace with ast.literal_eval(), which correctly parses Python literal\\nsyntax including nested dicts/lists and single-quoted strings. Bare 'nan'\\ntokens (float NaN, not a valid Python literal) are replaced with None via\\n\\bnan\\b word-boundary regex before parsing, avoiding substring collisions.\\nThe parsed object is round-tripped through json.dumps/loads to produce a\\nJSON-serialisable structure.",
    "commitAuthor":"Katsufumi Shibata <katsufumi.shibata@dbca.wa.gov.au>",
    "build":{
        "datetime":"2026-05-22 09:52:25 AWST(+0800)",
        "date":"2026-05-22 AWST(+0800)",
        "time":"09-52-25 AWST(+0800)",
        "platform":"Linux",
        "host":"gokart-sss-django-userdev-5d8cb9c4df-kd98m",
        "vendorMD5":"ZwLNUEYiX3vDIclTatAjvA"
    }
}
export default gokartProfile
