/Collatz Conjecture


int maint(void);

int collatz(int n);
{
	// int i = 0;
	if (n == 1)
		return 1;
	else if (is_even(n) == true)
		return n = collatz(n/2);
	else
		return n = collatz((3 * n) + 1);
}

bool is_even(int n);
{
	// bool is_even = false;
	if (n % 2 == 0)
	{
		// bool is_even = true;
		return true;
	}
}


/*bool is_odd(int n);
{
	// bool is_odd = false;  
	if (n % 2 !== 0)
	{
		// bool is_odd = true;
		return true;
	}
}
*/

