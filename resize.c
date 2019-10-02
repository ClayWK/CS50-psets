// Copies and resizes a BMP file

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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
    if (f <= 0 || f > 100)
    {
        printf("Usage: resize factor must be > 0.0 and <= 100.0\n");
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

    // Initialize a variable to remember biHeight and biWidth of infile
    // These values will be used below when we write to outfile
    int infile_biHeight = abs(bi.biHeight);
    int infile_biWidth = bi.biWidth;

    // determine padding of infile for scanlines
    int infile_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // Update biWidth and biHeight in our copy of BITMAPINFOHEADER
    bi.biWidth = roundf(bi.biWidth * f);
    bi.biHeight = roundf(bi.biHeight * f);

    // determine padding needed in oufile
    int outfile_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // Update biSizeImage in BITMAPINFOHEADER
    // This definition of no_of_pixels does not include the padding, if any
    // Padding pixels are only one byte so the number
    // of padding pixels is not multipled by the size of an RGBTRIPLE
    int no_of_pixels = abs(bi.biWidth * bi.biHeight);
    bi.biSizeImage = (no_of_pixels * sizeof(RGBTRIPLE)) + abs(bi.biHeight * outfile_padding);

    // Update bfSize in BITMAPFILEHEADER
    bf.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + bi.biSizeImage;

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // Separate process for enlarging vs shrinking
    // Test value of f to determine which to follow
    if (f >= 1)
    {
        // iterate over infile's scanlines
        for (int i = 0; i < infile_biHeight; i++)
        {
            // print each row f times
            // f is rounded since we must print whole rows
            for (int j = 0, round_f = roundf(f); j < round_f; j++)
            {
                // iterate over pixels in scanline
                for (int k = 0; k < infile_biWidth; k++)
                {

                    // Print pixels f times
                    // f is rounded since we must print whole pixels
                    for (int m = 0; m < round_f; m++)
                    {
                        // temporary storage
                        RGBTRIPLE triple;

                        // read RGB triple from infile
                        fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                        // write RGB triple to outfile
                        fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);

                        // move back one pixel
                        fseek(inptr, -1 * sizeof(RGBTRIPLE), SEEK_CUR);

                        // break if we are at the end of the adjusted width
                        if (((k * round_f) + m) >= (bi.biWidth - 1))
                        {
                            break;
                        }
                    }
                    // Move forward one pixel
                    fseek(inptr, sizeof(RGBTRIPLE), SEEK_CUR);
                }

                // skip over padding, if any
                fseek(inptr, infile_padding, SEEK_CUR);

                // then add padding needed in outfile
                for (int n = 0; n < outfile_padding; n++)
                {
                    fputc(0x00, outptr);
                }

                // move back to beginning of row in infile if needed
                if (j < (round_f - 1))
                {
                    fseek(inptr, -1 * ((sizeof(RGBTRIPLE) * infile_biWidth) + infile_padding), SEEK_CUR);
                }

                // break if we're out of rows
                if (((i * round_f) + j) >= (abs(bi.biHeight) - 1))
                {
                    break;
                }
            }
        }
    }

    // if f is less than 1 and image needs to shrink, run below
    else
    {
        // iterate over infile's scanlines
        for (int i = 0; i < abs(bi.biHeight); i++)
        {
            // iterate over pixels in scanline
            for (int k = 0; k < bi.biWidth; k++)
            {
                // temporary storage
                RGBTRIPLE triple;

                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                // write RGB triple to outfile
                fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);

                // skip over a pixel
                fseek(inptr, sizeof(RGBTRIPLE), SEEK_CUR);
            }

            // skip over padding, if any
            fseek(inptr, infile_padding, SEEK_CUR);

            // then add padding needed in outfile
            for (int n = 0; n < outfile_padding; n++)
            {
                fputc(0x00, outptr);
            }
            // skip over the next row
            fseek(inptr, (sizeof(RGBTRIPLE) * infile_biWidth) + infile_padding, SEEK_CUR);
        }
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}