let gokartProfile=  {
    "name": "sss",
    "version":"16.11.1",
    "distributionType":"release",
    "description":"Spatial Support System v3 (Django)",
    "repositoryBranch":"working",
    "lastCommit":"6c54d09",
    "commitDate":"Fri Mar 27 11:43:26 2026 +0800",
    "commitMessage":"Block invalid center/scale from being persisted in saveState\\nGuard saveState() so center is only stored when it is a finite [x, y] pair and scale is only stored when finite and > 0, preventing corrupted offline state from being written.",
    "commitAuthor":"Katsufumi Shibata <katsufumi.shibata@dbca.wa.gov.au>",
    "build":{
        "datetime":"2026-03-27 11:47:22 AWST(+0800)",
        "date":"2026-03-27 AWST(+0800)",
        "time":"11-47-22 AWST(+0800)",
        "platform":"Linux",
        "host":"gokart-sss-django-userdev-5d8cb9c4df-glhf4",
        "vendorMD5":"rvXZh5m046EuqC9h8dkyFA"
    }
}
export default gokartProfile
