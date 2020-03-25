// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#include "dictionary.h"

// Represents number of children for each node in a trie
#define N 27

// Used to adjust ASCII values
#define Magic_Number 97

// Represents a node in a trie
typedef struct node
{
    bool is_word;
    struct node *children[N];
}
node;

// Prototypes
void insert(node *first_node, FILE *file, const char *word, int wordlen, int i);
int count_size(node *first_node, int count);
void free_nodes(node *first_node);

// Represents a trie
node *root;

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize trie
    root = malloc(sizeof(node));
    if (root == NULL)
    {
        return false;
    }
    root->is_word = false;
    for (int i = 0; i < N; i++)
    {
        root->children[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];
    // [NTD: Ensure each element is /0 - write for loop]

    // Insert words into trie
    // fscanf extracts from file until it encounters non-char white space (or EOF)
    while (fscanf(file, "%s", word) != EOF)
    {
        // TODO
        int wordlen = strlen(word);
        int i = 0;
        insert (root, file, word, wordlen, i);
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    int count = 0;
    node *trav;
    count = count_size(root, count);
    return count;
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    // TODO
    node *trav;
    trav = root;
    int wordlen = strlen(word);
    for (int i = 0; i < wordlen; i++)
    {
        char ltr = word[i];
        int n = 0;
        if (isalpha(word[i]) && islower(word[i]))
        {
            n = ltr - Magic_Number;
         }
        else if (isalpha(word[i]) && isupper(word[i]))
        {
            n = ltr - 65;
         }
        // An apostrophe has an ASCII value of 47
        // To give the apostophe a vaue of 26 (26 letters in the alphabet + 1)
        // We subtract 20 from 47 (47 - 21 = 26)
        else if (word[i] == '\'')
        {
            n = ltr - 21;
        }
        if (trav->children[n] == NULL)
        {
            return false;

        }
        else if (trav->children[n] != NULL && i != (wordlen - 1))
        {
            trav = trav->children[n];
        }
        else if (trav->children[n] != NULL && i == (wordlen - 1))
        {
            trav = trav->children[n];
            if (trav->is_word == true)
            {
                return true;
            }
        }
    }
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    // TODO
    // node *trav;
    // trav = root;
    free_nodes(root);
    // free(root);
    return true;
}

// Takes as input the first node we want to look at, the dictionary, and the wordlen
void insert(node *first_node, FILE *file, const char *word, int wordlen, int i)
{
    char ltr = word[i];
    int n = 0;
    if (isalpha(word[i]))
    {
        n = ltr - Magic_Number;
    }
    // An apostrophe has an ASCII value of 47
    // To give the apostophe a vaue of 26 (26 letters in the alphabet + 1)
    // We subtract 20 from 47 (47 - 21 = 26)
    else if (word[i] == '\'')
    {
        n = ltr - 21;
    }
    // check value at children[n]
    // If NULL, malloc a new node, have children[n] point to it
    else if (word[i] == '\0')
    {
        return;
    }
    if (first_node->children[n] == NULL)
    {
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            return;
        }
        new_node->is_word = false;
        for (int j = 0; j < N; j++)
        {
            new_node->children[j] = NULL;
        }
        first_node->children[n] = new_node;
        // If at end of word, set is_word to true
        if (i == (wordlen - 1))
        {
            new_node->is_word = true;
        }
        else
        {
            i++;
            insert(first_node->children[n], file, word, wordlen, i);
        }
    }

    // If not NULL, move to new node and continue
    else if (first_node->children[n] != NULL)
    {
        i++;
        insert(first_node->children[n], file, word, wordlen, i);
    }
    return;
}

int count_size(node *first_node, int count)
{
    node *next_node;
    for (int i = 0; i < N; i++)
    {
        if (first_node->children[i] != NULL)
        {
            next_node = first_node->children[i];
            if (next_node->is_word == true)
            {
                count++;
            }
            count = count_size(next_node, count);
        }
    }
    return count;
}

void free_nodes(node *first_node)
{
    for (int i = 0; i < N; i++)
    {
        if (first_node->children[i] != NULL)
        {
            node *trav;
            trav = first_node->children[i];
            // for (int j = 0; j < N; j++)
            // {
            //    trav->children[j] = NULL;
            // }
            free_nodes(trav);
        }
    }
    free(first_node);
}