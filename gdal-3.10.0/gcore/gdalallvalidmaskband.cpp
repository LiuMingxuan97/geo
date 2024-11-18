/******************************************************************************
 *
 * Project:  GDAL Core
 * Purpose:  Implementation of GDALAllValidMaskBand, a class implementing all
 *           a default 'all valid' band mask.
 * Author:   Frank Warmerdam, warmerdam@pobox.com
 *
 ******************************************************************************
 * Copyright (c) 2007, Frank Warmerdam
 *
 * SPDX-License-Identifier: MIT
 ****************************************************************************/

#include "cpl_port.h"
#include "gdal_priv.h"

#include <cstring>

#include "gdal.h"
#include "cpl_error.h"

//! @cond Doxygen_Suppress
/************************************************************************/
/*                        GDALAllValidMaskBand()                        */
/************************************************************************/

GDALAllValidMaskBand::GDALAllValidMaskBand(GDALRasterBand *poParent)
    : GDALRasterBand(FALSE)
{
    poDS = nullptr;
    nBand = 0;

    nRasterXSize = poParent->GetXSize();
    nRasterYSize = poParent->GetYSize();

    eDataType = GDT_Byte;
    poParent->GetBlockSize(&nBlockXSize, &nBlockYSize);
}

/************************************************************************/
/*                       ~GDALAllValidMaskBand()                        */
/************************************************************************/

GDALAllValidMaskBand::~GDALAllValidMaskBand() = default;

/************************************************************************/
/*                             IReadBlock()                             */
/************************************************************************/

CPLErr GDALAllValidMaskBand::IReadBlock(int /* nXBlockOff */,
                                        int /* nYBlockOff */, void *pImage)
{
    memset(pImage, 255, static_cast<size_t>(nBlockXSize) * nBlockYSize);

    return CE_None;
}

/************************************************************************/
/*                            GetMaskBand()                             */
/************************************************************************/

GDALRasterBand *GDALAllValidMaskBand::GetMaskBand()

{
    return this;
}

/************************************************************************/
/*                            GetMaskFlags()                            */
/************************************************************************/

int GDALAllValidMaskBand::GetMaskFlags()

{
    return GMF_ALL_VALID;
}

/************************************************************************/
/*                           ComputeStatistics()                        */
/************************************************************************/

CPLErr GDALAllValidMaskBand::ComputeStatistics(
    int /* bApproxOK */, double *pdfMin, double *pdfMax, double *pdfMean,
    double *pdfStdDev, GDALProgressFunc, void * /*pProgressData*/)
{
    if (pdfMin)
        *pdfMin = 255.0;
    if (pdfMax)
        *pdfMax = 255.0;
    if (pdfMean)
        *pdfMean = 255.0;
    if (pdfStdDev)
        *pdfStdDev = 0.0;
    return CE_None;
}

//! @endcond