/******************************************************************************
 *
 * Purpose:  Implementation of the JPEG compression/decompression based
 *           on libjpeg.  This implements functions suitable for use
 *           as jpeg interfaces in the PCIDSKInterfaces class.
 *
 ******************************************************************************
 * Copyright (c) 2009
 * PCI Geomatics, 90 Allstate Parkway, Markham, Ontario, Canada.
 *
 * SPDX-License-Identifier: MIT
 ****************************************************************************/

#include "pcidsk_config.h"
#include "pcidsk_types.h"
#include "core/pcidsk_utils.h"
#include "pcidsk_exception.h"
#include <cassert>
#include <cstdio>

using namespace PCIDSK;

#if defined(HAVE_LIBJPEG)

extern "C" {
#include "jpeglib.h"
}

static void _DummyMgrMethod( j_compress_ptr /*pUnused*/ ) {}
static void _DummySrcMgrMethod( j_decompress_ptr /*pUnused*/ ) {}
static boolean _DummyFillInputBuffer(j_decompress_ptr) { return 0; }
static void _DummySkipInputData(j_decompress_ptr, long) {}
static boolean _DummyEmptyOutputBuffer(j_compress_ptr) { return 0; }

/************************************************************************/
/*                             JpegError()                              */
/*                                                                      */
/*      Handle errors generated by the IJG library.  We treat all       */
/*      errors as fatal at this point.  Future handling may be          */
/*      improved by overriding other methods.                           */
/************************************************************************/

static void JpegError(j_common_ptr cinfo)
{
    char buf[256];

    cinfo->err->format_message(cinfo, buf);

    // Make sure we destroy the context before throwing an exception.
    if (cinfo->is_decompressor)
        jpeg_destroy_decompress((j_decompress_ptr) cinfo);
    else
        jpeg_destroy_compress((j_compress_ptr) cinfo);

    return ThrowPCIDSKException( "%s", buf );
}

/************************************************************************/
/*                      LibJPEG_DecompressBlock()                       */
/************************************************************************/

void PCIDSK::LibJPEG_DecompressBlock(
    uint8 *src_data, int src_bytes, uint8 *dst_data, CPL_UNUSED int dst_bytes,
    int xsize, int ysize, eChanType CPL_UNUSED pixel_type )
{
    struct jpeg_decompress_struct sJCompInfo;
    struct jpeg_source_mgr        sSrcMgr;
    struct jpeg_error_mgr         sErrMgr;

    int i;

/* -------------------------------------------------------------------- */
/*      Setup the buffer we will compress into.  We make it pretty      */
/*      big to ensure there is space.  The calling function will        */
/*      free it as soon as it is done so this should not hurt much.     */
/* -------------------------------------------------------------------- */
    sSrcMgr.init_source = _DummySrcMgrMethod;
    sSrcMgr.fill_input_buffer = _DummyFillInputBuffer;
    sSrcMgr.skip_input_data = _DummySkipInputData;
    sSrcMgr.resync_to_restart = jpeg_resync_to_restart;
    sSrcMgr.term_source = _DummySrcMgrMethod;

    sSrcMgr.next_input_byte = src_data;
    sSrcMgr.bytes_in_buffer = src_bytes;

/* -------------------------------------------------------------------- */
/*      Setup JPEG Decompression                                        */
/* -------------------------------------------------------------------- */
    jpeg_create_decompress(&sJCompInfo);

    sJCompInfo.src = &sSrcMgr;
    sJCompInfo.err = jpeg_std_error(&sErrMgr);
    sJCompInfo.err->output_message = JpegError;

/* -------------------------------------------------------------------- */
/*      Read the header.                                                */
/* -------------------------------------------------------------------- */
    jpeg_read_header( &sJCompInfo, TRUE );
    if (sJCompInfo.image_width != (unsigned int)xsize ||
        sJCompInfo.image_height != (unsigned int)ysize)
    {
        jpeg_destroy_decompress( &sJCompInfo );

        return ThrowPCIDSKException("Tile Size wrong in LibJPEG_DecompressTile(), got %dx%d, expected %dx%d.",
                             sJCompInfo.image_width,
                             sJCompInfo.image_height,
                             xsize, ysize );
    }

    sJCompInfo.out_color_space = JCS_GRAYSCALE;
    jpeg_start_decompress(&sJCompInfo);

/* -------------------------------------------------------------------- */
/*      Read each of the scanlines.                                     */
/* -------------------------------------------------------------------- */
    for( i = 0; i < ysize; i++ )
    {
        uint8   *line_data = dst_data + i*xsize;
        jpeg_read_scanlines( &sJCompInfo, (JSAMPARRAY) &line_data, 1 );
    }

/* -------------------------------------------------------------------- */
/*      Cleanup.                                                        */
/* -------------------------------------------------------------------- */
    jpeg_finish_decompress( &sJCompInfo );
    jpeg_destroy_decompress( &sJCompInfo );
}

/************************************************************************/
/*                      LibJPEG_CompressBlock()                         */
/************************************************************************/

void PCIDSK::LibJPEG_CompressBlock(
    uint8 *src_data, CPL_UNUSED int src_bytes, uint8 *dst_data, int &dst_bytes,
    int xsize, int ysize, CPL_UNUSED eChanType pixel_type, int quality )
{
    struct jpeg_compress_struct sJCompInfo;
    struct jpeg_destination_mgr sDstMgr;
    struct jpeg_error_mgr       sErrMgr;

    int     i;

/* -------------------------------------------------------------------- */
/*      Setup the buffer we will compress into.                         */
/* -------------------------------------------------------------------- */
    sDstMgr.next_output_byte = dst_data;
    sDstMgr.free_in_buffer = dst_bytes;
    sDstMgr.init_destination = _DummyMgrMethod;
    sDstMgr.empty_output_buffer = _DummyEmptyOutputBuffer;
    sDstMgr.term_destination = _DummyMgrMethod;

/* -------------------------------------------------------------------- */
/*      Setup JPEG Compression                                          */
/* -------------------------------------------------------------------- */
    jpeg_create_compress(&sJCompInfo);

    sJCompInfo.dest = &sDstMgr;
    sJCompInfo.err = jpeg_std_error(&sErrMgr);
    sJCompInfo.err->output_message = JpegError;

    sJCompInfo.image_width = xsize;
    sJCompInfo.image_height = ysize;
    sJCompInfo.input_components = 1;
    sJCompInfo.in_color_space = JCS_GRAYSCALE;

    jpeg_set_defaults(&sJCompInfo);
    jpeg_set_quality(&sJCompInfo, quality, TRUE );
    jpeg_start_compress(&sJCompInfo, TRUE );

/* -------------------------------------------------------------------- */
/*      Write all the scanlines at once.                                */
/* -------------------------------------------------------------------- */
    for( i = 0; i < ysize; i++ )
    {
        uint8   *pabyLine = src_data + i*xsize;

        jpeg_write_scanlines( &sJCompInfo, (JSAMPARRAY)&pabyLine, 1 );
    }

/* -------------------------------------------------------------------- */
/*      Cleanup.                                                        */
/* -------------------------------------------------------------------- */
    jpeg_finish_compress( &sJCompInfo );

    dst_bytes = static_cast<int>(dst_bytes - sDstMgr.free_in_buffer);

    jpeg_destroy_compress( &sJCompInfo );
}

#endif /* defined(HAVE_LIBJPEG) */
