/******************************************************************************
 *
 * Project:  AmigoCloud Translator
 * Purpose:  Implements OGRAMIGOCLOUDDriver.
 * Author:   Victor Chernetsky, <victor at amigocloud dot com>
 *
 ******************************************************************************
 * Copyright (c) 2015, Victor Chernetsky, <victor at amigocloud dot com>
 *
 * SPDX-License-Identifier: MIT
 ****************************************************************************/

#include "ogr_amigocloud.h"

extern "C" void RegisterOGRAmigoCloud();

/************************************************************************/
/*                        OGRAmigoCloudDriverIdentify()                    */
/************************************************************************/

static int OGRAmigoCloudDriverIdentify(GDALOpenInfo *poOpenInfo)
{
    return EQUALN(poOpenInfo->pszFilename,
                  "AMIGOCLOUD:", strlen("AMIGOCLOUD:"));
}

/************************************************************************/
/*                           OGRAmigoCloudDriverOpen()                     */
/************************************************************************/

static GDALDataset *OGRAmigoCloudDriverOpen(GDALOpenInfo *poOpenInfo)

{
    if (!OGRAmigoCloudDriverIdentify(poOpenInfo))
        return nullptr;

    OGRAmigoCloudDataSource *poDS = new OGRAmigoCloudDataSource();

    if (!poDS->Open(poOpenInfo->pszFilename, poOpenInfo->papszOpenOptions,
                    poOpenInfo->eAccess == GA_Update))
    {
        delete poDS;
        poDS = nullptr;
    }

    return poDS;
}

/************************************************************************/
/*                      OGRAmigoCloudDriverCreate()                        */
/************************************************************************/

static GDALDataset *OGRAmigoCloudDriverCreate(const char *pszName,
                                              CPL_UNUSED int nBands,
                                              CPL_UNUSED int nXSize,
                                              CPL_UNUSED int nYSize,
                                              CPL_UNUSED GDALDataType eDT,
                                              CPL_UNUSED char **papszOptions)

{
    OGRAmigoCloudDataSource *poDS = new OGRAmigoCloudDataSource();

    if (!poDS->Open(pszName, nullptr, TRUE))
    {
        delete poDS;
        return nullptr;
    }

    return poDS;
}

/************************************************************************/
/*                         RegisterOGRAMIGOCLOUD()                         */
/************************************************************************/

void RegisterOGRAmigoCloud()
{
    if (GDALGetDriverByName("AmigoCloud") != nullptr)
        return;

    GDALDriver *poDriver = new GDALDriver();

    poDriver->SetDescription("AmigoCloud");
    poDriver->SetMetadataItem(GDAL_DMD_LONGNAME, "AmigoCloud");
    poDriver->SetMetadataItem(GDAL_DCAP_VECTOR, "YES");
    poDriver->SetMetadataItem(GDAL_DCAP_CREATE_LAYER, "YES");
    poDriver->SetMetadataItem(GDAL_DCAP_DELETE_LAYER, "YES");
    poDriver->SetMetadataItem(GDAL_DMD_HELPTOPIC,
                              "drivers/vector/amigocloud.html");
    poDriver->SetMetadataItem(GDAL_DMD_CONNECTION_PREFIX, "AMIGOCLOUD:");

    poDriver->SetMetadataItem(
        GDAL_DMD_OPENOPTIONLIST,
        "<OpenOptionList>"
        "  <Option name='AMIGOCLOUD_API_KEY' type='string' "
        "description='AmigoCLoud API token'/>"
        "  <Option name='OVERWRITE' type='boolean' description='Whether to "
        "overwrite an existing table without deleting it' default='NO'/>"
        "</OpenOptionList>");

    poDriver->SetMetadataItem(GDAL_DMD_CREATIONOPTIONLIST,
                              "<CreationOptionList/>");

    poDriver->SetMetadataItem(
        GDAL_DS_LAYER_CREATIONOPTIONLIST,
        "<LayerCreationOptionList>"
        "  <Option name='GEOMETRY_NULLABLE' type='boolean' "
        "description='Whether the values of the geometry column can be NULL' "
        "default='YES'/>"
        "</LayerCreationOptionList>");

    poDriver->SetMetadataItem(GDAL_DMD_CREATIONFIELDDATATYPES,
                              "String Integer Integer64 Real");
    poDriver->SetMetadataItem(GDAL_DCAP_NOTNULL_FIELDS, "YES");
    poDriver->SetMetadataItem(GDAL_DCAP_DEFAULT_FIELDS, "YES");
    poDriver->SetMetadataItem(GDAL_DCAP_NOTNULL_GEOMFIELDS, "YES");
    poDriver->SetMetadataItem(GDAL_DCAP_Z_GEOMETRIES, "YES");
    poDriver->SetMetadataItem(GDAL_DMD_SUPPORTED_SQL_DIALECTS,
                              "NATIVE OGRSQL SQLITE");

    poDriver->pfnOpen = OGRAmigoCloudDriverOpen;
    poDriver->pfnIdentify = OGRAmigoCloudDriverIdentify;
    poDriver->pfnCreate = OGRAmigoCloudDriverCreate;

    GetGDALDriverManager()->RegisterDriver(poDriver);
}