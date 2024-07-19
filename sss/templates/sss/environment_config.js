var env = {
    // authUrl:'/sso/profile',
    authUrl: "{{ settings.ACCOUNT_DETAILS_URL }}",
    appType: (window.location.protocol == "file:")?"cordova":"webapp",
    // cswService:"https://csw-uat.dbca.wa.gov.au/catalogue/api2/application/records",
    cswService: "{{ settings.CSW_SERVICE_URL }}",
    catalogueAdminService:"{{ settings.CATALOGUE_URL }}",

    //kmiService:"https://kmi.dbca.wa.gov.au/geoserver",
    kmiService:"{{ settings.KMI_SERVICE_URL }}",
    kmiApiService: "{{ settings.KMI_API_URL }}",
    legendSrc:"https://kmi.dbca.wa.gov.au/geoserver/gwc/service/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&legend_options=fontName:Times%20New%20Roman;fontAntiAliasing:true;fontSize:14;bgColor:0xFFFFEE;dpi:120;labelMargin:10&LAYER=",

	hotspotService:"{{ settings.HOTSPOT_SERVICE_URL }}",

    gokartService:"{{ settings.SSS_SERVICE_URL }}",
    resourceTrackingService:"{{ settings.RESOURCE_TRACKING_SERVICE_URL }}",
    bfrsService:"{{ settings.BFRS_SERVICE_URL }}",
    staticService:"{{ settings.DBCA_STATIC_URL }}",

    s3Service:"{{ settings.SSS_FILE_URL }}",

    appMapping:{
    },
    layerMapping:{
    },
    overviewLayer:"{{ settings.OVERVIEW_LAYER }}",

    kmiUrl:"{{ mapserver.kmi }}",
    hotspotsUrl:"{{mapserver.hotspots}}"
};

