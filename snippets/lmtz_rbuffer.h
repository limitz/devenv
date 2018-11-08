#ifndef LMTZ_RBUFFER_H_
#define LMTZ_RBUFFER_H_

#include <stdint.h>

typedef uint16_t rbuffer_size_t;
typedef uint8_t rbuffer_elem_t;

typedef struct {
    volatile rbuffer_size_t rp;
    volatile rbuffer_size_t wp;
} rbuffer_context_t;

#define rbuffer_t(capacity) struct { rbuffer_context_t context; rbuffer_elem_t data[capacity]; }

#define rbuffer_read(b, dst, len) _rbuffer_read (&(b)->context, sizeof((b)->data) / sizeof(rbuffer_elem_t), (dst), (b)->data, (len))
#define rbuffer_write(b, src, len) _rbuffer_write(&(b)->context, sizeof((b)->data) / sizeof(rbuffer_elem_t), (b)->data, (src), (len))

rbuffer_size_t _rbuffer_read(rbuffer_context_t* b, rbuffer_size_t capacity, rbuffer_elem_t* dst, const rbuffer_elem_t* src, rbuffer_size_t len);
rbuffer_size_t _rbuffer_write(rbuffer_context_t* b, rbuffer_size_t capacity, rbuffer_elem_t* dst, const rbuffer_elem_t* src, rbuffer_size_t len);

#endif /* LMTZ_RBUFFER_H_ */
