#include <cs50.h>
#include <stdio.h>

void print_space(int n);
void print_hash(int n);
void draw_pyramid(int n);

int main(void)
{
    // Ask the user for height between 1 - 8
    int height;
    do
    {
        height = get_int("Height: ");
    }
    
    // Loop if the input is not within range of 1-8, inclusive
    while (height < 1 || height > 8);
    draw_pyramid(height);   
}

// Print n number of spaces
void print_space(int n)
{
    for (int i = 0; i < n; i++)
    {
        printf(" ");
    }
}

// Print n number of hashes
void print_hash(int n)
{
    for (int i = 0; i < n; i++)
    {
        printf("#");        
    }
}

// Draw the rows of the pyramid
void draw_pyramid(int n)
{
    // Where n is the height, will print number of rows equal to the height
    for (int i = 1; i <= n; i++)
    {
        print_space(n - i);
        print_hash(i);
        print_space(2);
        print_hash(i);
        printf("\n");
    }   
}