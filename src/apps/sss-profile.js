let gokartProfile=  {
    "name": "sss",
    "version":"16.11.1",
    "distributionType":"dev",
    "description":"Spatial Support System v3 (Django)",
    "repositoryBranch":"working",
    "lastCommit":"4a2d22d",
    "commitDate":"Thu May 28 14:20:02 2026 +0800",
    "commitMessage":"fix: upgrade Python dependencies to resolve security vulnerabilities\\n- django==5.2.13 \u2192 ==5.2.14 (PYSEC-2026-50, PYSEC-2026-54, PYSEC-2026-55)\\n- requests==2.32.4 \u2192 >=2.33.0 (CVE-2026-25645)\\n- urllib3~=2.6.0 \u2192 >=2.7.0 (PYSEC-2026-141, PYSEC-2026-142)\\n- idna>=3.15 added explicitly (CVE-2026-45409; transitive via requests)\\nGDAL vulnerabilities (CVE-2026-8087, CVE-2026-8088) are excluded\\ndue to upgrade risk; requires system-level GDAL update.",
    "commitAuthor":"Katsufumi Shibata <katsufumi.shibata@dbca.wa.gov.au>",
    "build":{
        "datetime":"2026-05-29 09:11:43 AWST(+0800)",
        "date":"2026-05-29 AWST(+0800)",
        "time":"09-11-43 AWST(+0800)",
        "platform":"Linux",
        "host":"gokart-sss-django-userdev-5d8cb9c4df-vm6w4",
        "vendorMD5":"GAZpW8wJbRC1eg72WOKCRA"
    }
}
export default gokartProfile
