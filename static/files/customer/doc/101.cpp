#include <iostream>

template <class Main, std::size_t N>
constexpr std::size_t size(const T (&array)[N]) noexcept
{
	return N;
}

int main()
{
	int arr[] = { 1, 2, 3, 4, 5 };
	std::cout << "The length of the array is " << size(arr);

	return 0;
}