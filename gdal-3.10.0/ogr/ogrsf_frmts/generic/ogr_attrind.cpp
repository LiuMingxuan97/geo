/******************************************************************************
 *
 * Project:  OpenGIS Simple Features Reference Implementation
 * Purpose:  Implementation of OGRLayerAttrIndex and OGRAttrIndex base classes.
 * Author:   Frank Warmerdam, warmerdam@pobox.com
 *
 ******************************************************************************
 * Copyright (c) 2003, Frank Warmerdam
 *
 * SPDX-License-Identifier: MIT
 ****************************************************************************/

#include "ogr_attrind.h"
#include "cpl_conv.h"

//! @cond Doxygen_Suppress

/************************************************************************/
/* ==================================================================== */
/*                           OGRLayerAttrIndex                          */
/* ==================================================================== */
/************************************************************************/

/************************************************************************/
/*                         OGRLayerAttrIndex()                          */
/************************************************************************/

OGRLayerAttrIndex::OGRLayerAttrIndex() : poLayer(nullptr), pszIndexPath(nullptr)
{
}

/************************************************************************/
/*                         ~OGRLayerAttrIndex()                         */
/************************************************************************/

OGRLayerAttrIndex::~OGRLayerAttrIndex()

{
    CPLFree(pszIndexPath);
    pszIndexPath = nullptr;
}

/************************************************************************/
/* ==================================================================== */
/*                             OGRAttrIndex                             */
/* ==================================================================== */
/************************************************************************/

/************************************************************************/
/*                            OGRAttrIndex()                            */
/************************************************************************/

OGRAttrIndex::OGRAttrIndex()
{
}

/************************************************************************/
/*                           ~OGRAttrIndex()                            */
/************************************************************************/

OGRAttrIndex::~OGRAttrIndex()
{
}

//! @endcond