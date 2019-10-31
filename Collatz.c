/Collatz Conjecture


int maint(void);

int collatz(int n);
{
	int i = 0;
	
	while (n >= 1)
	{
		if (n == 1)
		{
			break;
		}
		else if (is_even(n) == true)
		{
			n /= 2;
			i++; 
			continue;
		}
		else
		{
			n = (3 * n) + 1;
			i++;
			continue;
		}	
	}
	return i; 
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


bool is_odd(int n);
{
	// bool is_odd = false;  
	if (n % 2 !== 0)
	{
		// bool is_odd = true;
		return true;
	}
}


