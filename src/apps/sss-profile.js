let gokartProfile=  {
    "name": "sss",
    "version":"16.11.1",
    "distributionType":"release",
    "description":"Spatial Support System v3 (Django)",
    "repositoryBranch":"working",
    "lastCommit":"6e571ce",
    "commitDate":"Tue Mar 24 14:40:53 2026 +0800",
    "commitMessage":"Fix: correct timediff variable name typo in _setTimeIndex\\ntimddiff was declared but never used due to a typo. The actual variable used inside the $.each callback was timediff, which lacked a var declaration and was therefore an implicit global (window.timediff).\\nFix the typo so that timediff is declared with var in the outer scope, making the $.each callback reference the correct local variable.",
    "commitAuthor":"Katsufumi Shibata <katsufumi.shibata@dbca.wa.gov.au>",
    "build":{
        "datetime":"2026-03-26 15:04:53 AWST(+0800)",
        "date":"2026-03-26 AWST(+0800)",
        "time":"15-04-53 AWST(+0800)",
        "platform":"Linux",
        "host":"gokart-sss-django-userdev-5d8cb9c4df-glhf4",
        "vendorMD5":"rvXZh5m046EuqC9h8dkyFA"
    }
}
export default gokartProfile
