#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#define MIN(a,b) ((a) <= (b) ? (a) : (b))
#define MAX(a,b) ((a) >= (b) ? (a) : (b))
#define CLAMP(b,min,max) MIN(MAX(b, min),max)

#define Z_OK 0
#define Z_ERR -1

#define Z_CHECK_ARG(x) do { if (!(x)) return -EINVAL; } while (0)
