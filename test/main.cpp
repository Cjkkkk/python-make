#include <stdio.h>

extern int f(int, int);
int main() {
    printf("result for 1 + 2 is %d\n", f(1, 2));
    return 0;
}