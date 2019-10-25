#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover image\n");
        return 1;
    }

    // remember file's name
    char *raw_file = argv[1];

    // open raw file
    FILE *rawptr = fopen(raw_file, "r");
    if (rawptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", raw_file);
        return 2;
    }
    // initialize an int to hold the value returned by fread in the while loop
    int test;

    // initialize boolean to test if the first jpeg has been found
    bool found_first_jpeg = false;

    // create a counter to be used in naming jpegs
    int i = -1;

    BYTE *buffer;

    do
    {
        // create temporary storage
        // read the raw file
        buffer = (BYTE *) malloc(512 * sizeof(BYTE));
        test = fread(buffer, 1, 512, rawptr);
        // end of file found when fread doesn't read 512 bytes
        if (test != 512)
        {
            break;
        }

        // check if beginning of jpeg found
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            // if beginning of jpeg found, open new jpeg,
            // name it, and write 512 bytes to it
            found_first_jpeg = true;
            i += 1;
            char filename[8];
            sprintf(filename, "%03i.jpg", i);
            FILE *img = fopen(filename, "w");
            if (img == NULL)
            {
                fprintf(stderr, "Could not open %s.\n", filename);
                return 3;
            }
            fwrite(buffer, 1, 512, img);
            fclose(img);
            free(buffer);
            continue;
        }

        else if (found_first_jpeg == false)
        {
            free(buffer);
            continue;
        }

        else
        {
            char filename[8];
            sprintf(filename, "%03i.jpg", i);
            FILE *img = fopen(filename, "a");
            fwrite(buffer, 1, 512, img);
            fclose(img);
            free(buffer);
            continue;
        }
    }
    while (test == 512);
    // close raw file
    fclose(rawptr);
    return 0;
}
