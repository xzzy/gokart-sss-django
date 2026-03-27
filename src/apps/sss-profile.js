let gokartProfile=  {
    "name": "sss",
    "version":"16.11.1",
    "distributionType":"release",
    "description":"Spatial Support System v3 (Django)",
    "repositoryBranch":"working",
    "lastCommit":"b48cb71",
    "commitDate":"Thu Mar 26 15:08:35 2026 +0800",
    "commitMessage":"Fix: wait for whoami before broadcasting gk-init to resolve intermittent IWF icon\\nThe IWF (Incident Weather Forecast) icon in the toolbox was intermittently missing on page load due to a race condition in the initialisation sequence.\\nTwo async operations were fired concurrently at startup:\\n1. $.ajax(\"/sso/auth\") \u2014 populates whoami.is_internal_dbca\\n2. loadRemoteCatalogue() \u2014 triggers the gk-init broadcast\\nThe toolbox reads each component's `tools` computed property exactly once during gk-init. In weatherforecast.vue, `tools` returns the IWF entry only when whoami.is_internal_dbca is truthy. If the catalogue finished before the auth response arrived, is_internal_dbca was still undefined at gk-init time and the IWF icon was never added to the toolbox for that session.\\nFix: store the whoami AJAX deferred (self._whoamiDeferred) and wrap the gk-init broadcast \u2014 along with the subsequent gk-postinit and post_init phases \u2014 inside $.when(self._whoamiDeferred).always(...), ensuring whoami is fully populated before any component reads it. .always() is used instead of .done() so that initialisation continues even if the auth request fails.",
    "commitAuthor":"Katsufumi Shibata <katsufumi.shibata@dbca.wa.gov.au>",
    "build":{
        "datetime":"2026-03-27 11:24:36 AWST(+0800)",
        "date":"2026-03-27 AWST(+0800)",
        "time":"11-24-36 AWST(+0800)",
        "platform":"Linux",
        "host":"gokart-sss-django-userdev-5d8cb9c4df-glhf4",
        "vendorMD5":"rvXZh5m046EuqC9h8dkyFA"
    }
}
export default gokartProfile
