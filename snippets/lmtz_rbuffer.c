#include "lmtz_rbuffer.h"

rbuffer_size_t _rbuffer_read(rbuffer_context_t* b, rbuffer_size_t capacity, rbuffer_elem_t* dst, const rbuffer_elem_t* src, rbuffer_size_t len)
{
	rbuffer_size_t transfer = 0;
    while (transfer < len)
    {
        if (b->rp == b->wp) break;
        dst[transfer++] = src[b->rp];
        b->rp = (b->rp + 1) % capacity;
	}
	return transfer;
}

rbuffer_size_t _rbuffer_write(rbuffer_context_t* b, rbuffer_size_t capacity, rbuffer_elem_t* dst, const rbuffer_elem_t* src, rbuffer_size_t len)
{
    rbuffer_size_t transfer = 0;
    while (transfer < len)
    {
        rbuffer_size_t next = (b->wp + 1) % capacity;
        if (next == b->rp) break;
        dst[b->wp] = src[transfer++];
        b->wp = next;
	}
	return transfer;
}
