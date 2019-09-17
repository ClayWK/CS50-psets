 // Copies a BMP file

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // Ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize f infile outfile\n");
        return 1;
    }

    // Parse float input
    float f;
    f = atof(argv[1]);

    // Ensure resize factor f within valid range
    if (f < 0 || f > 100)
    {
        printf("Usage: resize factor must be between 0.0 and 100.0\n");
        return 1;
    }

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    // Initialize a variable to remeber biHeight and biWidth of infile
    // These values will be used below when we write to outfile
    // infile_biHeight = abs(bi.biHeight);
    // infile_biWidth = bi.biWidth;

    // determine padding of infile for scanlines
    int infile_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // Update biWidth and biHeight of in BITMAPINFOHEADER
    bi.biWidth *= f;
    bi.biHeight *= f;

    // determine padding needed in oufile
    int outfile_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // Update bfSize in BITMAPFILEHEADER
    // This definition of no_of_pixels includes the padding, if any
    int no_of_pixels = -f*((bi.biWidth+outfile_padding)*bi.biHeight);
    bf.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + (no_of_pixels * sizeof(RGBTRIPLE));

    // Update biSizeImage in BITMAPINFOHEADER
    bi.biSizeImage = no_of_pixels * sizeof(RGBTRIPLE);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        // iterate over pixels in scanline
        for (int j = 0; j < bi.biWidth; j++)
        {
            // temporary storage
            RGBTRIPLE triple;

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

            // Print pixels f times
            for (int k = 0; k < f; k++)
            {
                // write RGB triple to outfile
                fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                fseek(inptr, -1 * sizeof(RGBTRIPLE), SEEK_CUR);
            }
            fseek(inptr, sizeof(RGBTRIPLE), SEEK_CUR);
        }


        // skip over padding, if any
        fseek(inptr, infile_padding, SEEK_CUR);

        // then add it back (to demonstrate how)
        for (int l = 0; l < outfile_padding; l++)
        {
            fputc(0x00, outptr);
        }
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}
