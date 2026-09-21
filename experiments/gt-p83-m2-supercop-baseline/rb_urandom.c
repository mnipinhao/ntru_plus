/* control: the /dev/urandom randombytes the trees ship with */
#include "randombytes.h"
#include <fcntl.h>
#include <unistd.h>
static int fd = -1;
void randombytes(uint8_t *out, size_t length)
{
    if (fd < 0) fd = open("/dev/urandom", O_RDONLY);
    while (length) { ssize_t n = read(fd, out, length);
        if (n <= 0) continue; out += n; length -= (size_t)n; }
}
