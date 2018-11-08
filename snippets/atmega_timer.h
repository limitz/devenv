#ifndef ATMEGA_TIMER_H_
#define ATMEGA_TIMER_H_

// FOR ATMEGA 48/88/168/328
// FOR SETTING UP COMPARE MATCH A INTERRUPT

// ISR(TIMER0_COMPA_vect)
// ISR(TIMER1_COMPA_vect)
// ISR(TIMER2_COMPA_vect)

#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>

typedef enum {
	TIMER0_CLOCK_NONE,
	TIMER0_CLOCK_DIV1,
	TIMER0_CLOCK_DIV8,
	TIMER0_CLOCK_DIV64,
	TIMER0_CLOCK_DIV256,
	TIMER0_CLOCK_DIV1024,
	TIMER0_CLOCK_EXT_FALLING,
	TIMER0_CLOCK_EXT_RISING
} timer0_clock_t;

typedef enum {
	TIMER1_CLOCK_NONE,
	TIMER1_CLOCK_DIV1,
	TIMER1_CLOCK_DIV8,
	TIMER1_CLOCK_DIV64,
	TIMER1_CLOCK_DIV256,
	TIMER1_CLOCK_DIV1024,
	TIMER1_CLOCK_EXT_FALLING,
	TIMER1_CLOCK_EXT_RISING
} timer1_clock_t;

typedef enum {
	TIMER2_CLOCK_NONE,
	TIMER2_CLOCK_DIV1,
	TIMER2_CLOCK_DIV8,
	TIMER2_CLOCK_DIV32,
	TIMER2_CLOCK_DIV64,
	TIMER2_CLOCK_DIV128,
	TIMER2_CLOCK_DIV256,
	TIMER2_CLOCK_DIV1024
} timer2_clock_t;

void lmtz_timer0_init(timer0_clock_t clk, uint8_t interval);
void lmtz_timer0_set_interval(uint8_t interval);

void lmtz_timer1_init(timer1_clock_t clk, uint16_t interval);
void lmtz_timer1_set_interval(uint16_t interval);

void lmtz_timer2_init(timer2_clock_t, uint8_t interval);
void lmtz_timer2_set_interval(uint8_t interval);

#endif /* ATMEGA_TIMER_H_ */