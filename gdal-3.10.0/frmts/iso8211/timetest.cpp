/* ****************************************************************************
 *
 * Project:  SDTS Translator
 * Purpose:  Example program dumping data in 8211 data to stdout.
 * Author:   Frank Warmerdam, warmerda@home.com
 *
 ******************************************************************************
 * Copyright (c) 1999, Frank Warmerdam
 *
 * SPDX-License-Identifier: MIT
 ****************************************************************************/

#include <stdio.h>
#include "iso8211.h"

static void ViewRecordField(DDFField *poField);
static int ViewSubfield(DDFSubfieldDefn *poSFDefn, const char *pachFieldData,
                        int nBytesRemaining);

/* **********************************************************************/
/*                                main()                                */
/* **********************************************************************/

int main(int nArgc, char **papszArgv)

{
    if (nArgc < 2)
    {
        printf("Usage: 8211view filename\n");
        exit(1);
    }

    const char *pszFilename = papszArgv[1];
    DDFModule oModule;

    for (int i = 0; i < 40; i++)
    {
        /* --------------------------------------------------------------------
         */
        /*      Open the file.  Note that by default errors are reported to */
        /*      stderr, so we don't bother doing it ourselves. */
        /* --------------------------------------------------------------------
         */
        if (!oModule.Open(pszFilename))
        {
            exit(1);
        }

        /* --------------------------------------------------------------------
         */
        /*      Loop reading records till there are none left. */
        /* --------------------------------------------------------------------
         */
        DDFRecord *poRecord = nullptr;
        int nRecordCount = 0;
        int nFieldCount = 0;

        while ((poRecord = oModule.ReadRecord()) != nullptr)
        {
            /* ------------------------------------------------------------ */
            /*      Loop over each field in this particular record.         */
            /* ------------------------------------------------------------ */
            for (int iField = 0; iField < poRecord->GetFieldCount(); iField++)
            {
                DDFField *poField = poRecord->GetField(iField);

                ViewRecordField(poField);

                nFieldCount++;
            }

            nRecordCount++;
        }

        oModule.Close();

        printf("Read %d records, %d fields.\n", nRecordCount, nFieldCount);
    }
}

/* **********************************************************************/
/*                          ViewRecordField()                           */
/*                                                                      */
/*      Dump the contents of a field instance in a record.              */
/* **********************************************************************/

static void ViewRecordField(DDFField *poField)

{
    DDFFieldDefn *poFieldDefn = poField->GetFieldDefn();

    // Get pointer to this fields raw data.  We will move through
    // it consuming data as we report subfield values.

    const char *pachFieldData = poField->GetData();
    int nBytesRemaining = poField->GetDataSize();

    /* -------------------------------------------------------- */
    /*      Loop over the repeat count for this fields          */
    /*      subfields.  The repeat count will almost            */
    /*      always be one.                                      */
    /* -------------------------------------------------------- */

    int nRepeatCount = poField->GetRepeatCount();

    for (int iRepeat = 0; iRepeat < nRepeatCount; iRepeat++)
    {

        /* -------------------------------------------------------- */
        /*   Loop over all the subfields of this field, advancing   */
        /*   the data pointer as we consume data.                   */
        /* -------------------------------------------------------- */
        for (int iSF = 0; iSF < poFieldDefn->GetSubfieldCount(); iSF++)
        {
            DDFSubfieldDefn *poSFDefn = poFieldDefn->GetSubfield(iSF);
            int nBytesConsumed =
                ViewSubfield(poSFDefn, pachFieldData, nBytesRemaining);

            nBytesRemaining -= nBytesConsumed;
            pachFieldData += nBytesConsumed;
        }
    }
}

/* **********************************************************************/
/*                            ViewSubfield()                            */
/* **********************************************************************/

static int ViewSubfield(DDFSubfieldDefn *poSFDefn, const char *pachFieldData,
                        int nBytesRemaining)

{
    int nBytesConsumed = 0;

    switch (poSFDefn->GetType())
    {
        case DDFInt:
            poSFDefn->ExtractIntData(pachFieldData, nBytesRemaining,
                                     &nBytesConsumed);
            break;

        case DDFFloat:
            poSFDefn->ExtractFloatData(pachFieldData, nBytesRemaining,
                                       &nBytesConsumed);
            break;

        case DDFString:
            poSFDefn->ExtractStringData(pachFieldData, nBytesRemaining,
                                        &nBytesConsumed);
            break;

        default:
            break;
    }

    return nBytesConsumed;
}
