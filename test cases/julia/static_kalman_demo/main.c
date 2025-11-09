# Start of file
#include <stdio.h>

/* The externally linked symbol name and signature depends on how juliac
   exports cfunctions. You may need to adjust the symbol name to match
   the produced library. */

extern int hello_from_julia(void);

int main(void) {
    int v = hello_from_julia();
    printf("Hello from Julia returned: %d\n", v);
    return 0;
}
# End of file
